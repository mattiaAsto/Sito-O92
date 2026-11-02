from datetime import timedelta
from datetime import datetime
from functools import wraps
from zoneinfo import ZoneInfo

from flask import Response, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Album, Photo
from app.photos import photos
from app.photos.dropbox import DropboxError, fetch_album_photos, fetch_albums, fetch_thumbnail

PER_PAGE = 24
REFRESH_AFTER = timedelta(minutes=30)  # re-read an open album's photos after this long


def photo_manager_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not (current_user.is_photo_manager or current_user.is_admin):
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def sync_albums(remote):
    """Make the albums table match the discovered folders, keeping featured flags and loaded photos."""
    existing = {a.dropbox_path: a for a in db.session.execute(db.select(Album)).scalars()}
    for path, album in existing.items():
        if path not in remote:
            db.session.delete(album)
    for path, (title, cover, date) in remote.items():
        album = existing.get(path)
        if album is None:
            album = Album(dropbox_path=path)
            db.session.add(album)
        album.title, album.cover_path, album.date = title, cover, date
    db.session.commit()


def load_album_photos(album):
    """Read this album's photos from Dropbox; only done when someone opens it."""
    items = fetch_album_photos(album.dropbox_path)
    by_path = {p.dropbox_path: p for p in album.photos}
    wanted = {path for path, _, _ in items}
    for photo in list(album.photos):
        if photo.dropbox_path not in wanted:
            album.photos.remove(photo)
    for path, name, taken in items:
        photo = by_path.get(path)
        if photo is None:
            album.photos.append(Photo(dropbox_path=path, name=name, taken_at=taken))
        else:
            photo.name, photo.taken_at = name, taken
    album.photos_loaded_at = datetime.now(ZoneInfo("Europe/Zurich")).replace(tzinfo=None)
    db.session.commit()


@photos.route("/")
def index():
    page = db.paginate(
        db.select(Album).order_by(Album.date.desc(), Album.id.desc()),
        per_page=PER_PAGE,
        error_out=False,
    )
    return render_template("photos/index.html", page=page)


@photos.route("/album/<int:album_id>")
def album(album_id):
    album = db.get_or_404(Album, album_id)
    stale = (
        album.photos_loaded_at is None
        or datetime.now(ZoneInfo("Europe/Zurich")).replace(tzinfo=None) - album.photos_loaded_at > REFRESH_AFTER
    )
    if stale:
        try:
            load_album_photos(album)
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Loading album photos failed")
            if not album.photos:
                flash("Non è stato possibile caricare le foto di questo album.", "error")
    return render_template("photos/album.html", album=album)


@photos.route("/cover/<int:album_id>/<size>")
def cover(album_id, size):
    album = db.get_or_404(Album, album_id)
    return _thumbnail_response(album.cover_path, size)

def _thumbnail_response(path, size):
    if size not in ("small", "large"):
        abort(404)
    try:
        result = fetch_thumbnail(path, size)
    except Exception:
        current_app.logger.exception("Dropbox thumbnail failed")
        abort(404)
    if result is None:
        abort(404)
    data, content_type = result
    return Response(data, content_type=content_type, headers={"Cache-Control": "public, max-age=86400"})


@photos.route("/image/<int:photo_id>/<size>")
def image(photo_id, size):
    photo = db.get_or_404(Photo, photo_id)
    return _thumbnail_response(photo.dropbox_path, size)

@photos.route("/album/<int:album_id>/feature", methods=["POST"])
@photo_manager_required
def toggle_featured(album_id):
    album = db.get_or_404(Album, album_id)
    album.is_featured = not album.is_featured
    db.session.commit()
    target = request.form.get("next", "")
    return redirect(target if target.startswith("/") and not target.startswith("//") else url_for("photos.index"))


@photos.route("/sync", methods=["POST"])
@photo_manager_required
def sync():
    try:
        remote = fetch_albums()
        sync_albums(remote)
    except DropboxError as exc:
        db.session.rollback()
        flash(f"Sincronizzazione con Dropbox non riuscita: {exc}.", "error")
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Dropbox sync failed")
        flash("Sincronizzazione con Dropbox non riuscita.", "error")
    else:
        if remote:
                        flash(f"Sincronizzati {len(remote)} album da Dropbox.", "success")
        else:
            flash(
                "Nessun album trovato: la cartella Dropbox non contiene foto.",
                "error",
            )
    return redirect(url_for("main.foto"))
