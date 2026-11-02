from datetime import datetime
from functools import wraps
import json
from zoneinfo import ZoneInfo

from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.blog import blog
from app.blog.forms import BlogPostForm
from app.extensions import db
from app.markdown_render import missing_photo_names
from app.models import BlogImage, BlogPost
from app.storage import InvalidImage, get_storage, prepare_image, save_image

PER_PAGE = 12
MAX_PHOTOS = 30


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def can_manage(post):
    return current_user.is_authenticated and (
        current_user.is_admin or current_user.id == post.author_id
    )


def newest_first():
    return (BlogPost.created_at.desc(), BlogPost.id.desc())


@blog.route("/")
def index():
    page = db.paginate(
        db.select(BlogPost).where(BlogPost.is_verified.is_(True)).order_by(*newest_first()),
        per_page=PER_PAGE,
        error_out=False,
    )
    verified = BlogPost.is_verified.is_(True)
    total = db.session.scalar(db.select(db.func.count()).select_from(BlogPost).where(verified))
    # Chapter 1 is the newest; "next" moves towards older chapters.
    requested = request.args.get("capitolo", type=int)
    chapter = min(max(requested, 1), total) if requested is not None and total else 1
    latest = db.session.execute(
        db.select(BlogPost).where(verified).order_by(*newest_first()).offset(chapter - 1).limit(1)
    ).scalar_one_or_none()
    return render_template(
        "blog/index.html",
        page=page,
        latest=latest,
        chapter=chapter,
        total=total,
        book_open=requested is not None,
    )


@blog.route("/mine")
@login_required
def mine():
    posts = db.session.execute(
        db.select(BlogPost).where(BlogPost.author_id == current_user.id).order_by(*newest_first())
    ).scalars().all()
    return render_template("blog/list.html", title="I miei racconti", posts=posts)


@blog.route("/pending")
@admin_required
def pending():
    posts = db.session.execute(
        db.select(BlogPost).where(BlogPost.is_verified.is_(False)).order_by(*newest_first())
    ).scalars().all()
    return render_template(
        "blog/list.html",
        title="Racconti da verificare",
        posts=posts,
        empty_message="Nessun racconto in attesa di verifica.",
    )


@blog.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = BlogPostForm()
    if form.validate_on_submit():
        photo_files = [f for f in form.photos.data or [] if f and f.filename]
        if len(photo_files) > MAX_PHOTOS:
            flash(f"Puoi caricare al massimo {MAX_PHOTOS} foto.", "error")
            return render_template("blog/create.html", form=form)
        cover_file = form.cover.data if form.cover.data and form.cover.data.filename else None

        # Validate every image before anything is written.
        try:
            photos = [(f.filename, prepare_image(f)) for f in photo_files]
            cover = prepare_image(cover_file) if cover_file else None
        except InvalidImage as exc:
            flash(str(exc), "error")
            return render_template("blog/create.html", form=form)

        # Admins' posts need no review.
        post = BlogPost(
            author_id=current_user.id,
            title=form.title.data,
            summary=form.summary.data or None,
            text=form.text.data,
            is_verified=current_user.is_admin,
        )
        db.session.add(post)
        db.session.flush()  # the id names the post's photo folder
        prefix = post.storage_prefix
        try:
            for original_name, prepared in photos:
                post.images.append(
                    BlogImage(filename=save_image(prefix, prepared), original_name=original_name[:255])
                )
            if cover:
                post.cover_filename = save_image(prefix, cover)
            db.session.commit()
        except Exception:
            db.session.rollback()
            get_storage().delete_prefix(prefix)
            current_app.logger.exception("Blog post creation failed")
            flash("Non è stato possibile salvare il racconto.", "error")
        else:
            if post.is_verified:
                flash("Racconto pubblicato.", "success")
            else:
                flash("Racconto salvato: sarà pubblicato dopo la verifica di un amministratore.", "success")
            missing = missing_photo_names(post.text, [name for name, _ in photos])
            if missing:
                flash(
                    "Nel testo ci sono immagini senza una foto caricata: " + ", ".join(missing),
                    "warning",
                )
            return redirect(url_for("blog.detail", post_id=post.id))
    return render_template("blog/create.html", form=form)


@blog.route("/preview", methods=["POST"])
@login_required
def preview():
    """Render a draft exactly like the final page, without saving anything."""
    try:
        names = json.loads(request.form.get("photo_names", "[]"))
    except ValueError:
        names = []
    names = [n for n in names if isinstance(n, str)][:MAX_PHOTOS]
    html = render_template(
        "blog/_preview.html",
        title=(request.form.get("title") or "").strip(),
        summary=(request.form.get("summary") or "").strip(),
        text=request.form.get("text") or "",
        photo_names=names,
        has_cover=request.form.get("has_cover") == "1",
        author=current_user,
        now_label=datetime.now(ZoneInfo("Europe/Zurich")).strftime("%d.%m.%Y"),
    )
    return {"html": html, "missing": missing_photo_names(request.form.get("text") or "", names)}


@blog.route("/<int:post_id>")
def detail(post_id):
    post = db.get_or_404(BlogPost, post_id)
    if not post.is_verified and not can_manage(post):
        abort(404)
    return render_template("blog/detail.html", post=post, can_manage=can_manage(post))


@blog.route("/<int:post_id>/verify", methods=["POST"])
@admin_required
def verify(post_id):
    post = db.get_or_404(BlogPost, post_id)
    post.is_verified = True
    db.session.commit()
    flash("Racconto verificato e pubblicato.", "success")
    return redirect(url_for("blog.detail", post_id=post.id))


@blog.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    post = db.get_or_404(BlogPost, post_id)
    if not can_manage(post):
        abort(403)
    prefix = post.storage_prefix
    db.session.delete(post)
    db.session.commit()
    get_storage().delete_prefix(prefix)
    flash("Racconto eliminato.", "success")
    return redirect(url_for("blog.index"))
