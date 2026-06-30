import os
import platform
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

_DEFAULT_LIBREOFFICE = (
    r"C:\Program Files\LibreOffice\program\soffice.exe"
    if platform.system() == "Windows"
    else "/usr/bin/soffice"
)


def _database_url():
    url = os.getenv("DATABASE_URL", f"sqlite:///{INSTANCE_DIR / 'contratos.db'}")
    # Railway/Heroku usam postgres://; SQLAlchemy exige postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TEMPLATE_DOCX = BASE_DIR / "app" / "templates_docx" / "contrato_modelo.docx"
    GENERATED_DOCX_DIR = BASE_DIR / "app" / "generated_contracts" / "docx"
    GENERATED_PDF_DIR = BASE_DIR / "app" / "generated_contracts" / "pdf"

    # auto = gera PDF se LibreOffice existir; required = falha sem PDF; disabled = só DOCX
    PDF_CONVERSION = os.getenv("PDF_CONVERSION", "auto").lower()

    LIBREOFFICE_PATH = os.getenv("LIBREOFFICE_PATH", _DEFAULT_LIBREOFFICE)
    PDF_CONVERSION_TIMEOUT = int(os.getenv("PDF_CONVERSION_TIMEOUT", "120"))

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
