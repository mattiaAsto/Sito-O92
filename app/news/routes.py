from functools import wraps

from flask import abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import News
from app.news import news
from app.news.forms import NewsForm
from app.storage import InvalidImage, get_storage, prepare_image, save_image

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


@news.route("/<int:news_id>/delete", methods=["POST"])
@admin_required
def delete(news_id):
    article = db.get_or_404(News, news_id)
    prefix = article.storage_prefix
    db.session.delete(article)
    db.session.commit()
    get_storage().delete_prefix(prefix)
    flash("News eliminata.", "success")
    return redirect(url_for("news.index"))


@news.route("/create", methods=["GET", "POST"])
@news_manager_required
def create():
    form = NewsForm()
    if form.validate_on_submit():
        thumbnail_file = form.thumbnail.data if form.thumbnail.data and form.thumbnail.data.filename else None

        # Validate the image before anything is written.
        try:
            thumbnail = prepare_image(thumbnail_file) if thumbnail_file else None
        except InvalidImage as exc:
            flash(str(exc), "error")
            return render_template("news/create.html", form=form)

        article = News(
            title=form.title.data,
            summary=form.summary.data or None,
            text=form.text.data,
        )
        db.session.add(article)
        db.session.flush()  # the id names the article's photo folder
        prefix = article.storage_prefix
        try:
            if thumbnail:
                article.thumbnail_filename = save_image(prefix, thumbnail)
            db.session.commit()
        except Exception:
            db.session.rollback()
            get_storage().delete_prefix(prefix)
            current_app.logger.exception("News creation failed")
            flash("Non è stato possibile salvare la news.", "error")
        else:
            flash("News salvata: sarà pubblicata dopo la verifica di un amministratore.", "success")
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
