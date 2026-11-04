import io
import shutil
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import MetaData, text

from app import create_app
from app.calendar.palette import ACTIVITY_CATEGORIES
from app.extensions import db
from app.models import CalendarActivity, User


app = create_app()


def create_test_user():
    # Testing only: never ship this account with a real database.
    user = User(
        first_name="Admin",
        last_name="Admin",
        email="webmaster@o-92.ch",
        is_admin=True,
        is_photo_manager=True,
        is_van_manager=True,
        is_news_manager=True,
        is_calendar_manager=True,
    )
    user.set_password("admin@o-92.ch")
    db.session.add(user)
    db.session.commit()


def create_test_calendar_activities():
    month_start = datetime.now(ZoneInfo("Europe/Zurich")).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    activities = []

    for category, weekday, titles in (
        (
            "training_wednesday",
            2,
            ("Allenamento in cartina", "Allenamento tecnico", "Allenamento bosco", "Staffetta"),
        ),
        (
            "training_friday",
            4,
            ("Allenamento in palestra", "Giochi di squadra", "Tecnica di corsa", "Unihockey"),
        ),
    ):
        first_offset = (weekday - month_start.weekday()) % 7
        for occurrence, title in enumerate(titles):
            starts_at = month_start + timedelta(days=first_offset + occurrence * 7, hours=18)
            activities.append(
                CalendarActivity(
                    activity_type=ACTIVITY_CATEGORIES[category]["activity_type"],
                    category=category,
                    title=title,
                    description="Attività di prova per visualizzare il calendario.",
                    starts_at=starts_at,
                    ends_at=starts_at + timedelta(hours=1, minutes=30),
                    location="Piano di Magadino",
                    latitude=46.1605,
                    longitude=8.9360,
                )
            )

    other_activities = (
        ("race_ticino", "Gara cantonale", 1, 0, "Bellinzona", 46.1946, 9.0244),
        ("other_activity", "Assemblea della società", 3, 0, "Cadenazzo", 46.1450, 8.9400),
        ("race_switzerland", "Gara nazionale", 5, 0, "Aarau", 47.3925, 8.0442),
        ("camp", "Campo pasquale", 8, 2, "Sonogno", 46.3519, 8.7829),
        ("race_ticino", "Gara regionale", 10, 0, "Locarno", 46.1708, 8.7995),
        ("other_activity", "Presentazione del club", 12, 0, "Contone", 46.1590, 8.9170),
        ("race_switzerland", "Campionato svizzero", 15, 0, "Neuchâtel", 46.9896, 6.9293),
        ("camp", "Campo cantonale", 18, 2, "Leventina", 46.4930, 8.8010),
        ("race_ticino", "Sprint in città", 21, 0, "Lugano", 46.0037, 8.9511),
        ("other_activity", "Giornata di orientamento", 24, 0, "Gambarogno", 46.1050, 8.8570),
        ("race_switzerland", "Gara nazionale di staffetta", 28, 0, "Zurigo", 47.3769, 8.5417),
        # No coordinates: exercises the detail page without a map.
        ("race_ticino", "Gara d'autunno", 33, 0, None, None, None),
    )
    for category, title, day_offset, duration_days, location, latitude, longitude in other_activities:
        starts_at = (month_start + timedelta(days=day_offset)).replace(hour=9)
        # Presentazione del club has no registration; others close 7 days before the start.
        has_deadline = title != "Presentazione del club"
        activities.append(
            CalendarActivity(
                activity_type=ACTIVITY_CATEGORIES[category]["activity_type"],
                category=category,
                title=title,
                description="Attività di prova per visualizzare il calendario.",
                starts_at=starts_at,
                ends_at=starts_at + timedelta(days=duration_days, hours=6),
                location=location,
                latitude=latitude,
                longitude=longitude,
                inscription_delay_date=(starts_at - timedelta(days=7)).date() if has_deadline else None,
            )
        )

    db.session.add_all(activities)
    db.session.commit()


def _placeholder_image(color, label):
    from PIL import Image, ImageDraw

    from app.storage import PreparedImage

    image = Image.new("RGB", (1200, 800), color)
    draw = ImageDraw.Draw(image)
    draw.text((40, 40), label, fill="white")
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=80)
    return PreparedImage(buffer.getvalue(), ".jpg")


def create_test_blog_posts():
    from app.models import BlogImage, BlogPost
    from app.storage import save_image

    author = db.session.execute(db.select(User)).scalars().first()
    second_author = User(first_name="Marco", last_name="Bianchi", email="marco@test.com")
    second_author.set_password("12345678")
    db.session.add(second_author)
    db.session.flush()

    now = datetime.now(ZoneInfo("Europe/Zurich"))
    posts = (
        (
            author,
            "Capitolo o-Ringen 2026",
            "1500 km, meta Göteborg",
            (
                "Abbiamo caricato il furgone alle quattro del mattino, tra borse con vestiti, scarpe "
                "ancora fangose e una cassa di banane. Davanti a noi c'erano millecinquecento chilometri "
                "e un solo obiettivo: arrivare in Svezia.\n\n"
                "## La partenza\n\n"
                "Il **primo giorno** è passato tra autogrill e playlist discutibili. Verso sera abbiamo "
                "attraversato la Germania, con la *pioggia* che non ci ha mai mollati.\n\n"
                "![Il furgone carico pronto a partire](furgone.jpg)\n\n"
                "## Cosa abbiamo imparato\n\n"
                "- le banane finiscono sempre prima del previsto\n"
                "- la bussola non perdona\n"
                "- il bosco svedese è un'altra storia\n\n"
                "> Non conta quanto corri, conta quante lanterne trovi.\n"
            ),
            True,
            now - timedelta(days=1),
            "#e8930c",
        ),
        (
            second_author,
            "Una settimana in Giappone",
            "Sprint tra i templi di Kyoto",
            (
                "Non avrei mai pensato di correre una gara di orientamento tra torii rossi e lanterne "
                "di pietra. Eppure eccomi qui, con la cartina in mano e il fiato corto.\n\n"
                "## La gara\n\n"
                "Il terreno era fittissimo, con sentieri che sparivano nel bambù. Ho sbagliato la "
                "terza lanterna, ma ne è valsa la pena.\n\n"
                "![Tra i templi di Kyoto](kyoto.jpg)\n"
            ),
            True,
            now - timedelta(days=12),
            "#3a7d5c",
        ),
        (
            author,
            "Il mio primo campo estivo",
            "Una settimana tra le montagne della Leventina",
            "Un racconto breve, senza foto: tende, risotto e tante cartine. Più di una gara, una vacanza.",
            True,
            now - timedelta(days=40),
            None,
        ),
        (
            second_author,
            "Racconto in attesa di verifica",
            "Solo gli admin lo vedono in /blog/pending",
            "Questo racconto non è ancora stato verificato: serve per provare il flusso di verifica.",
            False,
            now - timedelta(hours=2),
            None,
        ),
    )
    for writer, title, summary, text, verified, created_at, color in posts:
        post = BlogPost(
            author_id=writer.id,
            title=title,
            summary=summary,
            text=text,
            is_verified=verified,
            created_at=created_at,
        )
        db.session.add(post)
        db.session.flush()
        if color:
            prefix = post.storage_prefix
            post.cover_filename = save_image(prefix, _placeholder_image(color, title))
            for original_name in ("furgone.jpg", "kyoto.jpg"):
                if f"]({original_name})" in text:
                    post.images.append(
                        BlogImage(
                            filename=save_image(prefix, _placeholder_image(color, original_name)),
                            original_name=original_name,
                        )
                    )
    db.session.commit()


def reset_database():
    # Early development only: wipe and rebuild every table (and local uploads) on each start.
    with app.app_context():
        # Reflect the real schema so tables no longer in the models (stale FKs) are dropped too.
        existing = MetaData()
        existing.reflect(bind=db.engine)
        with db.engine.begin() as connection:
            if connection.dialect.name == "mysql":
                connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            existing.drop_all(bind=connection)
            if connection.dialect.name == "mysql":
                connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        db.create_all()
        if app.config["STORAGE_BACKEND"] == "local":
            shutil.rmtree(app.config["UPLOAD_FOLDER"], ignore_errors=True)
        create_test_user()
        create_test_calendar_activities()
        create_test_blog_posts()


if __name__ == "__main__":
    reset_database()
    print("Database reset, main running...")

    # Development server: reload templates and refresh the browser on file changes.
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.jinja_env.auto_reload = True

    from livereload import Server

    server = Server(app.wsgi_app)
    for pattern in ("app/**/templates/**/*.html", "app/**/static/**/*.css", "app/**/static/**/*.js"):
        server.watch(pattern)
    # Python changes restart the process (debug autoreload); once the browser's
    # livereload client reconnects to the new process, tell it to refresh.
    from livereload.handlers import LiveReloadHandler
    from tornado.ioloop import IOLoop

    def refresh_after_restart(attempts_left=60):
        if LiveReloadHandler.waiters:
            LiveReloadHandler.reload_waiters()
        elif attempts_left:
            IOLoop.current().call_later(0.5, refresh_after_restart, attempts_left - 1)

    IOLoop.current().call_later(0.5, refresh_after_restart)
    server.serve(port=5000, debug=True)
