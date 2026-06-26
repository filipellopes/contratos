from flask import Blueprint, current_app, render_template, send_file

from app.models.contract_option import ContractOption, FIELD_NAMES
from app.services.model_reference import (
    FORM_FIELDS,
    OPTION_FIELD_GUIDE,
    WORD_VARIABLES,
    get_template_placeholders,
)

docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/referencia")
def model_reference():
    options_by_field = {}
    for field in FIELD_NAMES:
        options_by_field[field] = (
            ContractOption.query.filter_by(field_name=field)
            .order_by(ContractOption.sort_order, ContractOption.option_label)
            .all()
        )

    placeholders_in_docx = get_template_placeholders()
    in_docx = set()
    for p in placeholders_in_docx:
        if p.startswith("{{"):
            in_docx.add(p[2:-2].strip())
    conditional_tags = [p for p in placeholders_in_docx if p.startswith("{%")]
    expected_vars = {v["variable"] for v in WORD_VARIABLES}
    missing_in_docx = sorted(expected_vars - in_docx - {"exibir_clausula_decima_terceira"})

    return render_template(
        "docs/model_reference.html",
        word_variables=WORD_VARIABLES,
        option_guide=OPTION_FIELD_GUIDE,
        form_fields=FORM_FIELDS,
        field_names=FIELD_NAMES,
        options_by_field=options_by_field,
        placeholders_in_docx=placeholders_in_docx,
        conditional_tags=conditional_tags,
        missing_in_docx=missing_in_docx,
    )


@docs_bp.route("/referencia/download-modelo")
def download_template():
    path = current_app.config["TEMPLATE_DOCX"]
    return send_file(path, as_attachment=True, download_name="contrato_modelo.docx")
