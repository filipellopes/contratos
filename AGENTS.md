# AGENTS.md

## Cursor Cloud specific instructions

### Product
Single Flask web app (Portuguese): **"Gerador de Contratos Valore"** — generates accounting-service contracts (DOCX/PDF) from a Word template. No monorepo, no extra services. Standard install/run steps are in `README.md`; routes are summarized there too.

### Service: `contratos` (Flask web app)
- Python deps live in a virtualenv at `.venv/` (created/refreshed by the startup update script). Activate with `. .venv/bin/activate` before running anything.
- Database is **SQLite** at `instance/contratos.db` (auto-created). Seed sample data with `python seed.py` (idempotent — skips rows that already exist). Run the seed at least once so the contract form has dropdown options and the Valore "empresa contratada" (id `1`) exists.
- Run the dev server: `python run.py` → serves on `0.0.0.0:5000` (Flask debug/reloader on by default).

### Tests / lint / build
- No linter and no build step are configured in this repo.
- `tests/test_routes.py` is the only pytest-style file: `python -m pytest tests/test_routes.py`. `test_api_empresa` requires the DB to be seeded first.
- `tests/test_docx_render.py` and `tests/test_multi_contratantes.py` are standalone smoke scripts with a `main()`, NOT pytest tests. Run them directly and they need the repo root on the path, e.g. `PYTHONPATH=/workspace python tests/test_docx_render.py`. Generated files land in `app/generated_contracts/docx/`.

### PDF export (non-obvious)
- DOCX→PDF uses **LibreOffice headless** (`/usr/bin/soffice`, package `libreoffice-writer-nogui`), installed as a system dependency in the VM snapshot (not in the update script).
- `PDF_CONVERSION` defaults to `auto`: DOCX is always generated; PDF is skipped (non-fatal) if LibreOffice is missing. With LibreOffice present, PDF is generated end-to-end.
- A `.env` file is **optional on Linux**: `app/config.py` already defaults `LIBREOFFICE_PATH` to `/usr/bin/soffice` and `PDF_CONVERSION` to `auto`. Only create `.env` (from `.env.example`) if you need to override these.
