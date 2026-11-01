from pathlib import Path

from flask import current_app, flash, redirect, render_template, url_for

from app.email import send_email
from app.extensions import db
from app.main import main
from app.main.forms import ContactForm
from app.models import News

CONTACT_EMAIL = "info@o-92.ch"

SPONSOR_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}


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


@main.route("/")
def index():
    latest_news = db.session.execute(
        db.select(News)
        .where(News.is_verified.is_(True))
        .order_by(News.created_at.desc(), News.id.desc())
        .limit(3)
    ).scalars().all()
    return render_template("main/home.html", latest_news=latest_news)


@main.route("/whats_orienteering")
def whats_orienteering():
    return render_template("main/whats_orienteering.html")


@main.route("/allenamenti")
def allenamenti():
    return render_template("activities/allenamenti.html")


@main.route("/gare")
def gare():
    return render_template("activities/gare.html")


@main.route("/attivita")
def attivita():
    return render_template("activities/attivita.html")


@main.route("/chi-siamo")
def chi_siamo():
    return render_template("main/chi_siamo.html")


@main.route("/foto")
def foto():
    return render_template("main/foto.html")


@main.route("/furgoni")
def furgoni():
    return render_template("main/furgoni.html")


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


@main.route("/calendario")
def calendario():
    return render_template("main/calendario.html")
