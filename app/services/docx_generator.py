from copy import deepcopy
from datetime import datetime
from pathlib import Path

from docx import Document
from docxtpl import DocxTemplate
from flask import current_app


def _find_contratantes_table(document):
    for table in document.tables:
        if not table.rows:
            continue
        header_cells = [cell.text.strip() for cell in table.rows[0].cells]
        if "CNPJ" in header_cells and "Razão Social" in header_cells:
            return table
    return None


def _set_row_cells(row, contratante):
    values = [
        contratante.get("cnpj", ""),
        contratante.get("enquadramento", ""),
        contratante.get("razao_social", ""),
        contratante.get("valor_mensal_formatado", ""),
    ]
    for cell, value in zip(row.cells, values):
        cell.text = value


def _expand_contratantes_table(docx_path, contratantes):
    if len(contratantes) <= 1:
        return

    document = Document(str(docx_path))
    table = _find_contratantes_table(document)
    if not table or len(table.rows) < 2:
        return

    template_row = table.rows[1]
    for contratante in contratantes[1:]:
        new_row = deepcopy(template_row._tr)
        table._tbl.append(new_row)
        _set_row_cells(table.rows[-1], contratante)

    document.save(str(docx_path))


def generate_docx(context, razao_social):
    template_path = Path(current_app.config["TEMPLATE_DOCX"])
    if not template_path.exists():
        raise FileNotFoundError(f"Modelo Word não encontrado: {template_path}")

    contratantes = context.get("contratantes") or []
    render_context = dict(context)
    if contratantes:
        first = contratantes[0]
        render_context.update(
            {
                "cnpj": first.get("cnpj", ""),
                "enquadramento": first.get("enquadramento", ""),
                "razao_social": first.get("razao_social", ""),
                "valor_mensal_formatado": first.get("valor_mensal_formatado", ""),
            }
        )

    doc = DocxTemplate(str(template_path))
    doc.render(render_context)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    from app.services.formatters import slugify

    filename = f"contrato_{slugify(razao_social)}_{timestamp}.docx"
    output_dir = Path(current_app.config["GENERATED_DOCX_DIR"])
    output_path = output_dir / filename
    doc.save(str(output_path))

    _expand_contratantes_table(output_path, contratantes)
    return output_path
