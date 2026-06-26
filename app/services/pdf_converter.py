import os
import shutil
import subprocess
from pathlib import Path

from flask import current_app


def _candidate_paths():
    configured = os.getenv("LIBREOFFICE_PATH", "")
    if configured:
        yield Path(configured.strip().strip('"'))

    config_value = current_app.config.get("LIBREOFFICE_PATH")
    if config_value:
        yield Path(config_value)

    found = shutil.which("soffice")
    if found:
        yield Path(found)

    program_files = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
    ]
    for base in program_files:
        yield base / "LibreOffice" / "program" / "soffice.exe"

    yield Path("/usr/bin/libreoffice")
    yield Path("/usr/bin/soffice")


def find_libreoffice():
    seen = set()
    for path in _candidate_paths():
        if not path:
            continue
        key = str(path).lower()
        if key in seen:
            continue
        seen.add(key)
        if path.exists():
            return path.resolve()
    return None


def libreoffice_error_message():
    tried = list({str(p) for p in _candidate_paths() if p})
    lines = [
        "LibreOffice não encontrado para conversão em PDF.",
        "",
        "Desenvolvimento local (Windows): não é necessário instalar.",
        "Use PDF_CONVERSION=auto no .env — o Word (.docx) será gerado normalmente.",
        "",
        "Produção (VPS Linux): instale no servidor:",
        "  sudo apt update && sudo apt install -y libreoffice-writer-nogui",
        "",
        "Ou use Docker (recomendado): docker compose up -d",
        "",
        "Windows (opcional): https://www.libreoffice.org/download/",
        '  LIBREOFFICE_PATH=C:\\Program Files\\LibreOffice\\program\\soffice.exe',
    ]
    if tried:
        lines.extend(["", "Caminhos verificados:"])
        for path in tried[:6]:
            lines.append(f"  - {path}")
    return "\n".join(lines)


def convert_docx_to_pdf(docx_path, *, required=None):
    """Converte DOCX em PDF. Retorna Path ou None se modo auto/disabled e LO indisponível."""
    mode = (required if required is not None else current_app.config.get("PDF_CONVERSION", "auto")).lower()

    if mode == "disabled":
        return None

    docx_path = Path(docx_path)
    output_dir = Path(current_app.config["GENERATED_PDF_DIR"])
    output_dir.mkdir(parents=True, exist_ok=True)

    soffice = find_libreoffice()
    if not soffice:
        if mode == "required":
            raise RuntimeError(libreoffice_error_message())
        return None

    cmd = [
        str(soffice),
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output_dir),
        str(docx_path.resolve()),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=current_app.config["PDF_CONVERSION_TIMEOUT"],
    )

    if result.returncode != 0:
        message = f"Falha na conversão PDF: {result.stderr or result.stdout or 'erro desconhecido'}"
        if mode == "required":
            raise RuntimeError(message)
        return None

    pdf_path = output_dir / f"{docx_path.stem}.pdf"
    if not pdf_path.exists():
        if mode == "required":
            raise RuntimeError("Arquivo PDF não foi gerado pelo LibreOffice.")
        return None

    return pdf_path
