# When True, the ZIP also contains mobile.html: the site shown inside a phone-sized
# frame, so the small-screen layout can be reviewed from a desktop browser.
export_small_screen_version = True

import argparse
import html
import mimetypes
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
from app.models import Album, BlogPost, CalendarActivity, News, Product
from app.shop.catalog import MATERIALS_BY_SLUG


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
    "/blog/",
    "/photos/",
    "/shop",
    "/auth/login",
    "/auth/register",
)
URL_ATTRIBUTES = {"href", "src", "action", "poster", "data-src"}
# Served by the app rather than from a static folder, so they are fetched and saved.
STRICT_ASSET_PREFIXES = ("/media/",)
BEST_EFFORT_ASSET_PREFIXES = ("/photos/cover/", "/photos/image/")  # proxied from Dropbox
MOBILE_PAGE = "mobile.html"
MOBILE_TEMPLATE = """<!doctype html>
<html lang="it">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Anteprima schermo piccolo</title>
    <style>
      body { margin: 0; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem; background: #e9ecef; font-family: sans-serif; }
      .phone { width: 390px; max-width: 100%; height: min(844px, 90vh); border: 12px solid #212529; border-radius: 36px; overflow: hidden; background: #fff; box-shadow: 0 10px 30px rgba(0, 0, 0, .3); }
      iframe { width: 100%; height: 100%; border: 0; }
      p { margin: 0; color: #495057; font-size: .9rem; }
    </style>
  </head>
  <body>
    <div class="phone"><iframe src="index.html" title="Sito in versione per schermo piccolo"></iframe></div>
    <p>Anteprima a 390 px di larghezza. <a href="index.html">Versione completa</a></p>
  </body>
</html>
"""


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


def _is_asset(path):
    return path.startswith(STRICT_ASSET_PREFIXES + BEST_EFFORT_ASSET_PREFIXES)


class _HTMLRewriter(HTMLParser):
    def __init__(self, source_path, page_paths, asset_paths=None):
        super().__init__(convert_charrefs=False)
        self.source_path = source_path.as_posix()
        self.page_paths = page_paths
        self.asset_paths = asset_paths or {}
        self.output = []
        self.asset_urls = set()

    def _rewrite_url(self, value):
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
            return value

        route_path = _route_path(parsed.path)
        target = self.page_paths.get(route_path) or self.asset_paths.get(parsed.path)
        if target is None:
            target = Path(parsed.path.lstrip("/"))
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
            if value is not None and name in URL_ATTRIBUTES:
                parsed = urlsplit(value)
                if not parsed.netloc and _is_asset(parsed.path):
                    self.asset_urls.add(parsed.path)
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
        if not rule.endpoint.endswith("static") or "<path:filename>" not in rule.rule:
            continue
        if rule.endpoint == "static":
            static_folder = app.static_folder
        else:
            blueprint = app.blueprints.get(rule.endpoint.rsplit(".", 1)[0])
            static_folder = blueprint.static_folder if blueprint else None
        if not static_folder:
            continue
        source = Path(static_folder)
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


def _asset_path(url_path, content_type):
    path = Path(url_path.lstrip("/"))
    if path.suffix:
        return path
    extension = mimetypes.guess_extension((content_type or "").split(";")[0].strip()) or ""
    if extension == ".jpe":
        extension = ".jpg"
    return path.with_name(path.name + extension)


def _fetch_assets(client, asset_urls):
    """Download every app-served asset; returns {url path: (output path, bytes)}."""
    assets = {}
    for url_path in sorted(asset_urls):
        response = client.get(url_path)
        if response.status_code != 200:
            message = f"Could not export asset {url_path}: HTTP {response.status_code}"
            if url_path.startswith(STRICT_ASSET_PREFIXES):
                raise RuntimeError(message)
            print(f"Warning: {message}")
            continue
        assets[url_path] = (
            _asset_path(url_path, response.headers.get("Content-Type")),
            response.data,
        )
    return assets


def export_site(app, output_path, small_screen_version=export_small_screen_version):
    output_path = Path(output_path).resolve()
    with app.app_context():
        event_ids = db.session.execute(
            db.select(CalendarActivity.id).order_by(CalendarActivity.id)
        ).scalars().all()
        news_ids = db.session.execute(
            db.select(News.id).where(News.is_verified.is_(True)).order_by(News.id)
        ).scalars().all()
        blog_ids = db.session.execute(
            db.select(BlogPost.id).where(BlogPost.is_verified.is_(True)).order_by(BlogPost.id)
        ).scalars().all()
        album_ids = db.session.execute(db.select(Album.id).order_by(Album.id)).scalars().all()
        product_ids = db.session.execute(
            db.select(Product.id).where(Product.is_verified.is_(True)).order_by(Product.id)
        ).scalars().all()
        calendar_events = _calendar_events()

    page_urls = list(PUBLIC_PAGES)
    page_urls.extend(f"/calendar/activity/{item_id}" for item_id in event_ids)
    page_urls.extend(f"/news/{item_id}" for item_id in news_ids)
    page_urls.extend(f"/blog/{item_id}" for item_id in blog_ids)
    page_urls.extend(f"/photos/album/{item_id}" for item_id in album_ids)
    page_urls.extend(f"/shop/{item_id}" for item_id in product_ids)
    page_urls.extend(f"/shop/materiale/{slug}" for slug in MATERIALS_BY_SLUG)
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
            rendered_pages[url] = body.decode("utf-8")

        asset_urls = set()
        for url, body in rendered_pages.items():
            collector = _HTMLRewriter(page_paths[_route_path(url)], page_paths)
            collector.feed(body)
            asset_urls.update(collector.asset_urls)
        assets = _fetch_assets(client, asset_urls)
        asset_paths = {url_path: path for url_path, (path, _) in assets.items()}

        for url, body in rendered_pages.items():
            page_path = page_paths[_route_path(url)]
            rewriter = _HTMLRewriter(page_path, page_paths, asset_paths)
            rewriter.feed(body)
            output = _safe_destination(staging, page_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text("".join(rewriter.output), encoding="utf-8")

        for path, data in assets.values():
            target = _safe_destination(staging, path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

        if small_screen_version:
            (staging / MOBILE_PAGE).write_text(MOBILE_TEMPLATE, encoding="utf-8")

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
    parser.add_argument(
        "--small-screen",
        action=argparse.BooleanOptionalAction,
        default=export_small_screen_version,
        help=f"include {MOBILE_PAGE}, a phone-sized preview (default: {export_small_screen_version})",
    )
    args = parser.parse_args()
    output_path = export_site(create_app(), args.output, args.small_screen)
    print(f"Static preview exported to {output_path}")


if __name__ == "__main__":
    main()
