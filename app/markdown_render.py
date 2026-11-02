import re
from html import unescape
from urllib.parse import unquote

import markdown
import nh3
from markupsafe import Markup
from werkzeug.utils import secure_filename

from app.storage import media_url

_ABSOLUTE_URL = re.compile(r"^([a-z][a-z0-9+.-]*:|//|/)", re.IGNORECASE)
_IMAGE_REF = re.compile(r'!\[[^\]]*\]\(\s*([^)"]+?)\s*(?:"[^"]*")?\s*\)')


def photo_key(name):
    """Normalised form used to match a name typed in the text with an uploaded file."""
    return secure_filename(unquote(name).replace("\\", "/").split("/")[-1]).lower()


def missing_photo_names(text, available_originals):
    """Relative images used in the text that match none of the uploaded photos."""
    available = {photo_key(name) for name in available_originals}
    missing = []
    for ref in _IMAGE_REF.findall(text or ""):
        if _ABSOLUTE_URL.match(ref):
            continue
        if photo_key(ref) not in available and ref not in missing:
            missing.append(ref)
    return missing


def _news_image_filter(article):
    """Rewrite relative <img src> values to the article's uploaded photos."""
    stored = {}
    for image in article.images:
        stored.setdefault(photo_key(image.original_name), image.filename)

    return _image_filter(
        lambda key: media_url(f"{article.storage_prefix}/{stored[key]}") if key in stored else None
    )


def _image_filter(resolve):
    def attribute_filter(tag, attr, value):
        if tag != "img" or attr != "src":
            return value
        if _ABSOLUTE_URL.match(value):
            return value
        return resolve(photo_key(value))

    return attribute_filter


SIZE_NAMES = {"piccola": 50, "media": 70, "grande": 85, "intera": 100}
_IMG_TITLE = re.compile(r'<img\b[^>]*?\btitle="([^"]*)"[^>]*>')


def _apply_sizes(html):
    """Turn an image title such as "piccola" or "40%" into a width attribute."""

    def replace(match):
        label = match.group(1).strip().lower().rstrip("%").strip()
        percent = SIZE_NAMES.get(label)
        if percent is None and label.isdigit():
            percent = min(max(int(label), 5), 100)
        if percent is None:
            return match.group(0)
        tag = re.sub(r'\s*\btitle="[^"]*"', "", match.group(0), count=1)
        return tag[:-1].rstrip("/ ") + f' width="{percent}%">'

    return _IMG_TITLE.sub(replace, html)


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


def _render(text, attribute_filter):
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    text = _IMAGE_LINE.sub(r"\n\1\n", text)  # an image on its own line is its own block
    html = markdown.markdown(text, extensions=["extra", "sane_lists", "nl2br"])
    clean = nh3.clean(_apply_sizes(html), attribute_filter=attribute_filter)
    return Markup(_captioned(clean))


def render_news_markdown(text, article):
    """Render a post's markdown to sanitized HTML.

    Images written with the name of an uploaded photo, e.g. ![alt](photo.jpg), are
    replaced with that photo's stored URL. A title sets the size: ![alt](photo.jpg "piccola").
    """
    return _render(text, _news_image_filter(article))


def render_preview_markdown(text, photo_names):
    """Same rendering as the final page; photos become #photo-<n> placeholders for the browser."""
    indexes = {}
    for index, name in enumerate(photo_names):
        indexes.setdefault(photo_key(name), index)
    return _render(
        text, _image_filter(lambda key: f"#photo-{indexes[key]}" if key in indexes else None)
    )


render_blog_markdown = render_news_markdown

_TEXT_TAGS = nh3.ALLOWED_TAGS - {"img"}


def plain_excerpt(text, length=280):
    """Markdown stripped to plain text and cut at a word boundary, for book-page previews."""
    html = markdown.markdown((text or "").replace("\r\n", "\n"), extensions=["extra", "sane_lists"])
    plain = nh3.clean(html, tags=set())
    plain = re.sub(r"\s+", " ", unescape(plain)).strip()
    if len(plain) <= length:
        return plain
    return plain[:length].rsplit(" ", 1)[0].rstrip(",.;:!?-") + " (…)"


def render_text_markdown(text):
    """Render markdown for image-free content (news): images are dropped."""
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    html = markdown.markdown(text, extensions=["extra", "sane_lists", "nl2br"])
    return Markup(nh3.clean(html, tags=_TEXT_TAGS))
