"""Uploaded-image storage.

All uploads live under one key space: "<feature>/<owner id>/<unique name>", e.g.
"news/12/3f2a....jpg" or "shop/4/9c1d....png". Each owner gets its own folder and
every file gets a random name, so uploads can never overwrite each other.

Backends share one small interface (save, delete_prefix, url). Only the local-disk
backend exists today; a Cloudflare R2/S3 backend can be added next to it and selected
with the STORAGE_BACKEND config value without touching any calling code.
"""

import io
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

from flask import current_app, url_for
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_DIMENSION = 1600
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "GIF"}
Image.MAX_IMAGE_PIXELS = 40_000_000


class InvalidImage(ValueError):
    """The uploaded file is not a usable image."""


@dataclass
class PreparedImage:
    data: bytes
    extension: str


def prepare_image(file_storage, max_dimension=MAX_DIMENSION):
    """Validate an upload by its real content and re-encode it.

    Re-encoding drops metadata (EXIF/GPS), applies the camera rotation and caps the
    size, so the original bytes are never stored or served.
    """
    name = file_storage.filename or "file"
    try:
        image = Image.open(file_storage.stream)
        if image.format not in ALLOWED_FORMATS:
            raise InvalidImage(f"{name}: formato immagine non supportato.")
        image.load()
    except InvalidImage:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as exc:
        raise InvalidImage(f"{name}: non è un'immagine valida.") from exc

    image = ImageOps.exif_transpose(image)
    image.thumbnail((max_dimension, max_dimension))
    has_alpha = image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    )
    buffer = io.BytesIO()
    if has_alpha:
        image.convert("RGBA").save(buffer, "PNG", optimize=True)
        return PreparedImage(buffer.getvalue(), ".png")
    image.convert("RGB").save(buffer, "JPEG", quality=85, optimize=True)
    return PreparedImage(buffer.getvalue(), ".jpg")


class LocalStorage:
    def __init__(self, root):
        self.root = Path(root).resolve()

    def path(self, key):
        """Absolute path for a key, or None if it would escape the storage root."""
        candidate = (self.root / key).resolve()
        if candidate == self.root or self.root not in candidate.parents:
            return None
        return candidate

    def save(self, key, data):
        path = self.path(key)
        if path is None:
            raise ValueError("Invalid storage key.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def delete_prefix(self, prefix):
        path = self.path(prefix)
        if path is not None:
            shutil.rmtree(path, ignore_errors=True)

    def url(self, key):
        return url_for("media.serve", key=key)


def init_storage(app):
    app.config.setdefault("UPLOAD_FOLDER", str(Path(app.instance_path) / "uploads"))
    backend = app.config.get("STORAGE_BACKEND", "local")
    if backend != "local":
        raise RuntimeError(f"Unknown STORAGE_BACKEND: {backend}")
    app.extensions["storage"] = LocalStorage(app.config["UPLOAD_FOLDER"])


def get_storage():
    return current_app.extensions["storage"]


def save_image(prefix, prepared):
    """Store a prepared image under <prefix>/ with a unique name; return that name."""
    name = f"{uuid.uuid4().hex}{prepared.extension}"
    get_storage().save(f"{prefix}/{name}", prepared.data)
    return name


def media_url(key):
    return get_storage().url(key)
