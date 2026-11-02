import argparse
import html
import posixpath
import shutil
import tempfile
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from flask import render_template

from app import create_app
from app.calendar.palette import ACTIVITY_CATEGORIES
from app.calendar.services import get_upcoming_inscription_deadlines
from app.extensions import db
from app.models import CalendarActivity, News, Product


ROOT = Path(__file__).resolve().parent
PUBLIC_PAGES = (
    "/",
    "/what-is-orienteering",
    "/links",
    "/training",
    "/races",
    "/activities",
    "/about-us",
    "/gallery",
    "/vans",
    "/contact",
    "/calendar",
    "/news/",
    "/shop",
    "/auth/login",
    "/auth/register",
)


def _route_path(path):
    normalized = path.rstrip("/")
    return normalized or "/"


def _page_output_path(route_path):
    path = route_path.strip("/")
    return Path(path, "index.html") if path else Path("index.html")


def _calendar_events():
    activities = db.session.execute(
        db.select(CalendarActivity).order_by(CalendarActivity.starts_at, CalendarActivity.id)
    ).scalars()
    return [
        {
            "id": activity.id,
            "title": activity.title,
            "start": activity.starts_at.isoformat(),
            "end": activity.ends_at.isoformat(),
            "time": activity.time_label,
            "location": activity.location,
            "activity_type": activity.activity_type,
            "category": activity.category,
            "category_label": activity.category_label,
            "color": activity.color,
        }
        for activity in activities
    ]


def _render_static_calendar(app, events):
    with app.test_request_context("/calendar"):
        return render_template(
            "calendar/index.html",
            activity_categories=ACTIVITY_CATEGORIES,
            deadlines=get_upcoming_inscription_deadlines(),
            static_events=events,
        )


class _HTMLRewriter(HTMLParser):
    def __init__(self, source_path, page_paths):
        super().__init__(convert_charrefs=False)
        self.source_path = source_path.as_posix()
        self.page_paths = page_paths
        self.output = []
        self.media_urls = set()

    def _rewrite_url(self, value):
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
            return value

        route_path = _route_path(parsed.path)
        target = self.page_paths.get(route_path)
        if target is None:
            target = parsed.path.lstrip("/")
        else:
            target = target.as_posix()

        relative = posixpath.relpath(
            target,
            posixpath.dirname(self.source_path) or ".",
        )
        query = f"?{parsed.query}" if parsed.query else ""
        fragment = f"#{parsed.fragment}" if parsed.fragment else ""
        return f"{relative}{query}{fragment}"

    def _start_tag(self, tag, attrs, close=False):
        rewritten = []
        for name, value in attrs:
            if value is not None and name in {"href", "src", "action", "poster"}:
                parsed = urlsplit(value)
                if parsed.path.startswith("/media/"):
                    self.media_urls.add(value)
                value = self._rewrite_url(value)
            if value is None:
                rewritten.append(name)
            else:
                rewritten.append(f'{name}="{html.escape(value, quote=True)}"')
        ending = " />" if close else ">"
        self.output.append(f"<{tag}{' ' if rewritten else ''}{' '.join(rewritten)}{ending}")

    def handle_starttag(self, tag, attrs):
        self._start_tag(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._start_tag(tag, attrs, close=True)

    def handle_endtag(self, tag):
        self.output.append(f"</{tag}>")

    def handle_data(self, data):
        self.output.append(data)

    def handle_entityref(self, name):
        self.output.append(f"&{name};")

    def handle_charref(self, name):
        self.output.append(f"&#{name};")

    def handle_comment(self, data):
        self.output.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.output.append(f"<!{decl}>")


def _write_static_directories(app, destination):
    for rule in app.url_map.iter_rules():
        if not rule.endpoint.endswith(".static") or "<path:filename>" not in rule.rule:
            continue
        blueprint_name = rule.endpoint.rsplit(".", 1)[0]
        blueprint = app.blueprints.get(blueprint_name)
        if blueprint is None or not blueprint.static_folder:
            continue
        source = Path(blueprint.static_folder)
        if source.is_dir():
            url_prefix = rule.rule.split("<", 1)[0].strip("/")
            target = destination / Path(url_prefix)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target, dirs_exist_ok=True)


def _safe_destination(root, relative_path):
    destination = (root / Path(*relative_path.parts)).resolve()
    if destination != root.resolve() and root.resolve() not in destination.parents:
        raise ValueError(f"Export path escapes destination: {relative_path}")
    return destination


def export_site(app, output_path):
    output_path = Path(output_path).resolve()
    with app.app_context():
        event_ids = db.session.execute(
            db.select(CalendarActivity.id).order_by(CalendarActivity.id)
        ).scalars().all()
        news_ids = db.session.execute(
            db.select(News.id).where(News.is_verified.is_(True)).order_by(News.id)
        ).scalars().all()
        product_ids = db.session.execute(
            db.select(Product.id).where(Product.is_verified.is_(True)).order_by(Product.id)
        ).scalars().all()
        calendar_events = _calendar_events()

    page_urls = list(PUBLIC_PAGES)
    page_urls.extend(f"/calendar/activity/{item_id}" for item_id in event_ids)
    page_urls.extend(f"/news/{item_id}" for item_id in news_ids)
    page_urls.extend(f"/shop/{item_id}" for item_id in product_ids)
    page_paths = {
        _route_path(url): _page_output_path(_route_path(url))
        for url in page_urls
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="site-export-") as temp_dir:
        staging = Path(temp_dir)
        _write_static_directories(app, staging)
        client = app.test_client()
        rendered_pages = {}

        for url in page_urls:
            if url == "/calendar":
                body = _render_static_calendar(app, calendar_events).encode("utf-8")
            else:
                response = client.get(url)
                if response.status_code != 200:
                    raise RuntimeError(f"Could not export {url}: HTTP {response.status_code}")
                body = response.data
            rendered_pages[url] = body

        media_urls = set()
        for url, body in rendered_pages.items():
            route_path = _route_path(url)
            output = _safe_destination(staging, page_paths[route_path])
            output.parent.mkdir(parents=True, exist_ok=True)
            rewriter = _HTMLRewriter(page_paths[route_path], page_paths)
            rewriter.feed(body.decode("utf-8"))
            output.write_text("".join(rewriter.output), encoding="utf-8")
            media_urls.update(rewriter.media_urls)

        for media_url in sorted(media_urls):
            response = client.get(media_url)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Could not export media asset {urlsplit(media_url).path}: "
                    f"HTTP {response.status_code}"
                )
            target = _safe_destination(
                staging,
                Path(urlsplit(media_url).path.lstrip("/")),
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(response.data)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(staging.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(staging).as_posix())

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Export the current public site pages and assets to a ZIP preview."
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "site-preview.zip"),
        help="ZIP file to create (default: site-preview.zip)",
    )
    args = parser.parse_args()
    output_path = export_site(create_app(), args.output)
    print(f"Static preview exported to {output_path}")


if __name__ == "__main__":
    main()
