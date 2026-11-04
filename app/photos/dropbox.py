"""Minimal Dropbox API client working through the shared folder link."""
import hashlib
import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import requests
from flask import current_app

API_URL = "https://api.dropboxapi.com/2"
CONTENT_URL = "https://content.dropboxapi.com/2"
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff", ".heic",
    ".cr2", ".cr3", ".nef", ".arw", ".dng", ".raf", ".orf", ".rw2",  # camera RAW
}
THUMBNAIL_SIZES = {"small": "w480h320", "large": "w2048h1536"}
TIMEOUT = 20
DISCOVERY_WORKERS = 8


class DropboxError(Exception):
    pass


_token = {"value": None, "expires": 0.0}
_token_lock = threading.Lock()


def _access_token():
    """Use the refresh token (renewed automatically) if configured, else the static key."""
    config = current_app.config
    if not config.get("DROPBOX_REFRESH_TOKEN"):
        token = config.get("DROPBOX_API_KEY")
        if not token:
            raise DropboxError("DROPBOX_API_KEY non configurata")
        return token
    with _token_lock:
        if _token["value"] and time.time() < _token["expires"]:
            return _token["value"]
        response = requests.post(
            "https://api.dropboxapi.com/oauth2/token",
            data={"grant_type": "refresh_token", "refresh_token": config["DROPBOX_REFRESH_TOKEN"]},
            auth=(config.get("DROPBOX_APP_KEY") or "", config.get("DROPBOX_APP_SECRET") or ""),
            timeout=TIMEOUT,
        )
        if not response.ok:
            raise DropboxError(f"rinnovo del token non riuscito ({response.status_code})")
        data = response.json()
        _token["value"] = data["access_token"]
        _token["expires"] = time.time() + int(data.get("expires_in", 14400)) - 120
        return _token["value"]


def _headers(extra=None):
    token = _access_token()
    return {"Authorization": f"Bearer {token}", **(extra or {})}


def _post(url, **kwargs):
    """POST to Dropbox, waiting and retrying when it rate-limits us."""
    for attempt in range(4):
        response = requests.post(url, timeout=TIMEOUT, **kwargs)
        if response.status_code != 429 or attempt == 3:
            return response
        time.sleep(min(int(response.headers.get("Retry-After", 1)), 10))


def _list_folder(path):
    """Yield the entries of a folder (path relative to the shared link, '' is the root)."""
    endpoint = "/files/list_folder"
    body = {
        "path": path,
        "shared_link": {"url": current_app.config["DROPBOX_FOLDER_URL"]},
        "limit": 2000,
    }
    while True:
        response = _post(API_URL + endpoint, headers=_headers(), json=body)
        if not response.ok:
            raise DropboxError(f"errore Dropbox {response.status_code}")
        data = response.json()
        yield from data["entries"]
        if not data.get("has_more"):
            return
        endpoint = "/files/list_folder/continue"
        body = {"cursor": data["cursor"]}

def _is_image(entry):
    name = entry["name"]
    return (
        entry[".tag"] == "file"
        and "." in name
        and "." + name.rsplit(".", 1)[1].lower() in IMAGE_EXTENSIONS
    )


def _parse_time(value):
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")


def _date_from_path(path):
    """Read the date from a '<year>/<month> - name' folder layout, if the path follows it."""
    parts = path.strip("/").split("/")
    for i, part in enumerate(parts):
        if re.fullmatch(r"(19|20)\d\d", part):
            month = re.match(r"(\d{1,2})\b", parts[i + 1]) if i + 1 < len(parts) else None
            month = int(month.group(1)) if month else 1
            return datetime(int(part), month if 1 <= month <= 12 else 1, 1)
    return None


def fetch_albums():
    """Return {album path: (title, date)} for the album folders, without reading any photo.

    Albums are the folders ALBUM_DEPTH levels below the shared folder (default: year/album).
    Only folder names are listed, one level at a time, several folders in parallel.
    """
    app = current_app._get_current_object()
    depth = app.config["DROPBOX_ALBUM_DEPTH"]

    def subfolders(path):
        with app.app_context():
            return [f"{path}/{e['name']}" for e in _list_folder(path) if e[".tag"] == "folder"]

    level = [""]
    with ThreadPoolExecutor(max_workers=DISCOVERY_WORKERS) as pool:
        for _ in range(depth):
            level = [child for children in pool.map(subfolders, level) for child in children]

    now = datetime.now()
    return {
        path: (path.strip("/").replace("/", " / "), _date_from_path(path) or now) for path in level
    }

def fetch_album_photos(path):
    """Return [(photo path, name, taken_at), ...] for a single album folder."""
    return [
        (f"{path}/{entry['name']}", entry["name"], _parse_time(entry["client_modified"]))
        for entry in _list_folder(path)
        if _is_image(entry)
    ]


def _cache_file(path, size):
    folder = Path(current_app.instance_path) / "photo_cache"
    return folder / (hashlib.sha1(f"{size}:{path}".encode("utf-8")).hexdigest() + ".jpg")


def fetch_thumbnail(path, size="small"):
    """Return (bytes, content_type) of a photo's thumbnail, or None if Dropbox refuses.

    Thumbnails are kept on disk, so Dropbox is asked for each image only once.
    """
    cached = _cache_file(path, size)
    if cached.exists():
        return cached.read_bytes(), "image/jpeg"
    arg = {
        "resource": {".tag": "link", "url": current_app.config["DROPBOX_FOLDER_URL"], "path": path},
        "format": "jpeg",
        "size": THUMBNAIL_SIZES[size],
        "mode": "bestfit",
    }
    response = _post(
        CONTENT_URL + "/files/get_thumbnail_v2",
        headers=_headers({"Dropbox-API-Arg": json.dumps(arg)}),
    )
    if not response.ok:
        current_app.logger.warning(
            "Dropbox thumbnail %s failed: %s %s", path, response.status_code, response.text[:300]
        )
        return None
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(response.content)
    return response.content, "image/jpeg"