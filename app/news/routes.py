from functools import wraps
from pathlib import Path

from flask import abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import News
from app.news import news
from app.news.forms import NewsForm

PER_PAGE = 12


def news_manager_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_news_manager:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped

def save_article_images(article, files):
    """Store uploads in app/news/static/<id>/ and return the saved filenames."""
    folder = Path(news.static_folder) / str(article.id)
    saved = []
    for storage in files:
        filename = secure_filename(storage.filename or "")
        if not filename:
            continue
        folder.mkdir(parents=True, exist_ok=True)
        storage.save(folder / filename)
        saved.append(filename)
    return saved


@news.route("/")
def index():
    page = db.paginate(
        db.select(News)
        .where(News.is_verified.is_(True))
        .order_by(News.created_at.desc(), News.id.desc()),
        per_page=PER_PAGE,
        error_out=False,
    )
    return render_template("news/index.html", page=page)


@news.route("/pending")
@admin_required
def pending():
    articles = db.session.execute(
        db.select(News)
        .where(News.is_verified.is_(False))
        .order_by(News.created_at.desc(), News.id.desc())
    ).scalars().all()
    return render_template("news/pending.html", articles=articles)


@news.route("/<int:news_id>/verify", methods=["POST"])
@admin_required
def verify(news_id):
    article = db.get_or_404(News, news_id)
    article.is_verified = True
    db.session.commit()
    flash("News verificata e pubblicata.", "success")
    return redirect(url_for("news.detail", news_id=article.id))


@news.route("/create", methods=["GET", "POST"])
@news_manager_required
def create():
    form = NewsForm()
    if form.validate_on_submit():
        article = News(
            title=form.title.data,
            summary=form.summary.data or None,
            text=form.text.data,
        )
        db.session.add(article)
        db.session.flush()  # the id names the article's photo folder
        try:
            saved = save_article_images(article, form.photos.data or [])
            thumbnail = form.thumbnail.data
            if thumbnail and thumbnail.filename:
                thumb_saved = save_article_images(article, [thumbnail])
                article.thumbnail_filename = thumb_saved[0] if thumb_saved else None
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception("News creation failed")
            flash("Non è stato possibile salvare la news.", "error")
        else:
            flash("News salvata: sarà pubblicata dopo la verifica di un amministratore.", "success")
            if saved:
                flash("Foto salvate come: " + ", ".join(saved), "message")
            return redirect(url_for("news.detail", news_id=article.id))
    return render_template("news/create.html", form=form)


@news.route("/<int:news_id>")
def detail(news_id):
    article = db.get_or_404(News, news_id)
    if not article.is_verified and not (
        current_user.is_authenticated
        and (current_user.is_admin or current_user.is_news_manager)
    ):
        abort(404)
    return render_template("news/detail.html", article=article)
