from pathlib import Path

from flask import current_app, flash, redirect, render_template, url_for

from app.calendar.services import get_next_activity, get_upcoming_activities
from app.email import send_email
from app.extensions import db
from app.main import main
from app.main.forms import ContactForm
from app.models import News

CONTACT_EMAIL = "info@o-92.ch"

SPONSOR_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}
SLIDESHOW_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


@main.app_context_processor
def inject_sponsors():
    folder = Path(main.static_folder) / "pictures" / "sponsors"
    files = []
    if folder.is_dir():
        files = sorted(
            f.name
            for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in SPONSOR_EXTENSIONS
        )
    return {"sponsor_logos": files}


def get_slideshow_images(folder=None):
    folder = folder or Path(main.static_folder) / "pictures" / "slideshow"
    if not folder.is_dir():
        return []
    return sorted(
        file.name
        for file in folder.iterdir()
        if file.is_file() and file.suffix.lower() in SLIDESHOW_EXTENSIONS
    )


@main.route("/")
def index():
    latest_news = db.session.execute(
        db.select(News)
        .where(News.is_verified.is_(True))
        .order_by(News.created_at.desc(), News.id.desc())
        .limit(3)
    ).scalars().all()
    upcoming = {
        activity_type: get_next_activity(activity_type)
        for activity_type in ("allenamento", "gara", "attivita")
    }
    return render_template("main/home.html", latest_news=latest_news, upcoming=upcoming)


@main.route("/whats_orienteering")
def whats_orienteering():
    return render_template("main/whats_orienteering.html")


@main.route("/links")
def links():
    return render_template("main/links.html")


@main.route("/allenamenti")
def allenamenti():
    upcoming_activities = get_upcoming_activities("allenamento")
    return render_template(
        "activities/allenamenti.html",
        upcoming_activities=upcoming_activities,
    )


@main.route("/gare")
def gare():
    upcoming_activities = get_upcoming_activities("gara")
    return render_template(
        "activities/gare.html",
        upcoming_activities=upcoming_activities,
    )


@main.route("/attivita")
def attivita():
    upcoming_activities = get_upcoming_activities("attivita")
    return render_template(
        "activities/attivita.html",
        upcoming_activities=upcoming_activities,
    )


@main.route("/chi-siamo")
def chi_siamo():
    return render_template(
        "main/chi_siamo.html",
        slideshow_images=get_slideshow_images(),
    )


@main.route("/foto")
def foto():
    return render_template("main/foto.html")


@main.route("/contatti", methods=["GET", "POST"])
def contatti():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            send_email(
                subject=f"Messaggio dal sito da {form.name.data}",
                recipients=[CONTACT_EMAIL],
                body=f"Da: {form.name.data} <{form.email.data}>\n\n{form.message.data}",
            )
        except Exception:
            current_app.logger.exception("Contact form email failed")
            flash("Non è stato possibile inviare il messaggio. Riprova più tardi.", "error")
        else:
            flash("Grazie! Il tuo messaggio è stato inviato.", "success")
            return redirect(url_for("main.contatti"))
    return render_template("main/contatti.html", form=form, contact_email=CONTACT_EMAIL)
