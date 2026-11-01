import re
from pathlib import Path
from urllib.parse import unquote

import markdown
import nh3
from flask import current_app, url_for
from markupsafe import Markup
from werkzeug.utils import secure_filename

_ABSOLUTE_URL = re.compile(r"^([a-z][a-z0-9+.-]*:|//|/)", re.IGNORECASE)


def _resolve_photo(news_id, value):
    """Map a filename typed in the text to the file actually stored for the article.

    Uploads are stored with secure_filename(), so apply it here too, then fall back
    to a case-insensitive match against the article folder.
    """
    wanted = secure_filename(unquote(value).replace("\\", "/").split("/")[-1])
    if not wanted:
        return None
    folder = Path(current_app.blueprints["news"].static_folder) / str(news_id)
    if folder.is_dir():
        for stored in folder.iterdir():
            if stored.name.lower() == wanted.lower():
                return stored.name
    return wanted


def _news_image_filter(news_id):
    """Rewrite relative <img src> values to the article's photo folder."""

    def attribute_filter(tag, attr, value):
        if tag != "img" or attr != "src":
            return value
        if _ABSOLUTE_URL.match(value):
            return value
        filename = _resolve_photo(news_id, value)
        if not filename:
            return None
        return url_for("news.static", filename=f"{news_id}/{filename}")

    return attribute_filter


_STANDALONE_IMG = re.compile(r'<p>\s*(<img\b[^>]*>)\s*</p>')
_ALT = re.compile(r'\balt="([^"]*)"')


def _captioned(html):
    """Turn a paragraph holding only an image into <figure> with its alt as caption."""

    def replace(match):
        img = match.group(1)
        alt = _ALT.search(img)
        caption = f"<figcaption>{alt.group(1)}</figcaption>" if alt and alt.group(1) else ""
        return f"<figure>{img}{caption}</figure>"

    return _STANDALONE_IMG.sub(replace, html)


_IMAGE_LINE = re.compile(r"^[ \t]*(!\[[^\]]*\]\([^)]*\))[ \t]*$", re.MULTILINE)


def render_news_markdown(text, news_id):
    """Render markdown to sanitized HTML.

    Images written with a bare filename, e.g. ![alt](photo.jpg), resolve to
    app/news/static/<news_id>/photo.jpg.
    """
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    text = _IMAGE_LINE.sub(r"\n\1\n", text)  # an image on its own line is its own block
    html = markdown.markdown(text, extensions=["extra", "sane_lists", "nl2br"])
    clean = nh3.clean(html, attribute_filter=_news_image_filter(news_id))
    return Markup(_captioned(clean))
