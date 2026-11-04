import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DB_COMPLETE_URL") or os.getenv("DATABASE_URL") or "sqlite:///app.db"
    ).replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # uploaded photos
    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() in {"1", "true", "yes", "on"}
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "60"))

    TRANSPORT_SHEET_URL = (
        "https://docs.google.com/spreadsheets/d/1YZKKoVIZ8jJVh1FqvBLej4Y5x_F_vZwwCQYzGR3_oME/"
        "edit?gid=957375013#gid=957375013"
    )

    DROPBOX_FOLDER_URL = os.getenv(
        "DROPBOX_FOLDER_URL",
        "https://www.dropbox.com/scl/fo/uypvkzvavbhxglc48n2wd/AIu0AJRFYe020lw8_yGsPAU"
        "?rlkey=o3vax0pgi2svl5r40bevwsj5v&e=1&dl=0",
    )
    DROPBOX_UPLOAD_URL = "https://www.dropbox.com/request/dxyytZyQd0h8PufJkxk3"
    DROPBOX_ALBUM_DEPTH = int(os.getenv("DROPBOX_ALBUM_DEPTH", "2"))  # folders below the root, e.g. year/album
    DROPBOX_API_KEY = os.getenv("DROPBOX_API_KEY")  # short-lived access token (expires in ~4h)
    # Preferred: a refresh token lets the site renew its own access token.
    DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
    DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
    DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv(
        "SESSION_COOKIE_SECURE",
        "true" if os.getenv("APP_ENV", "").lower() == "production" else "false",
    ).lower() in {"1", "true", "yes", "on"}
