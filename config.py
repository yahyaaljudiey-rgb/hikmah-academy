import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
RUNTIME_ENV_FILE = INSTANCE_DIR / "runtime.env"


def load_runtime_env(env_file: Path) -> None:
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


load_runtime_env(RUNTIME_ENV_FILE)


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'hikmah_academy.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "hikmah-dev-secret-key")
    ADMIN_ACCESS_CODE = os.getenv("ADMIN_ACCESS_CODE", "1234")
    TEACHER_ACCESS_CODE = os.getenv("TEACHER_ACCESS_CODE", "")

    EXAM_UPLOAD_DIR = os.getenv(
        "EXAM_UPLOAD_DIR",
        str(BASE_DIR / "data" / "exam_uploads"),
    )
    ASSIGNMENT_UPLOAD_DIR = os.getenv(
        "ASSIGNMENT_UPLOAD_DIR",
        str(BASE_DIR / "data" / "assignment_uploads"),
    )
    WEEKLY_REPORT_ARCHIVE_DIR = os.getenv(
        "WEEKLY_REPORT_ARCHIVE_DIR",
        str(BASE_DIR / "data" / "weekly_reports"),
    )

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "16")) * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = env_flag("SESSION_COOKIE_SECURE", default=False)
