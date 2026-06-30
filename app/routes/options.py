import json
import re
import unicodedata

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models.contract_option import DROPDOWN_FIELDS, ContractOption, FIELD_NAMES

options_bp = Blueprint("options", __name__, url_prefix="/opcoes")


def _slugify(text):
    """Converte um texto em snake_case ASCII, para uso como valor interno."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "opcao"


def _generate_option_value(field_name, label):
    """Gera um option_value único (por field_name) a partir do label."""
    base = _slugify(label)
    existing = {
        row.option_value
        for row in ContractOption.query.filter_by(field_name=field_name)
        .with_entities(ContractOption.option_value)
        .all()
    }
    if base not in existing:
        return base
    for n in range(2, 9999):
        candidate = f"{base}_{n}"
        if candidate not in existing:
            return candidate
    return base


def _parse_form():
    extra_raw = request.form.get("extra_data_json", "").strip()
    extra_data = {}
    if extra_raw:
        extra_data = json.loads(extra_raw)

    return {
        "field_name": request.form.get("field_name", "").strip(),
        "option_label": request.form.get("option_label", "").strip(),
        "full_text": request.form.get("full_text", "").strip(),
        "extra_data": extra_data,
        "is_active": request.form.get("is_active") == "on",
        "sort_order": int(request.form.get("sort_order") or 0),
    }


@options_bp.route("")
def list_options():
    field_filter = request.args.get("field_name", "")
    query = ContractOption.query.order_by(
        ContractOption.field_name,
        ContractOption.sort_order,
        ContractOption.option_label,
    )
    if field_filter:
        query = query.filter_by(field_name=field_filter)
    options = query.all()
    return render_template(
        "options/list.html",
        options=options,
        field_filter=field_filter,
        dropdown_fields=DROPDOWN_FIELDS,
    )


@options_bp.route("/nova", methods=["GET", "POST"])
def create_option():
    if request.method == "POST":
        try:
            data = _parse_form()
            option_value = _generate_option_value(data["field_name"], data["option_label"])
            option = ContractOption(
                field_name=data["field_name"],
                option_label=data["option_label"],
                option_value=option_value,
                full_text=data["full_text"],
                is_active=data["is_active"],
                sort_order=data["sort_order"],
            )
            option.extra_data = data["extra_data"]
            db.session.add(option)
            db.session.commit()
            flash("Opção cadastrada com sucesso.", "success")
            return redirect(url_for("options.list_options"))
        except (json.JSONDecodeError, ValueError) as exc:
            flash(f"Erro ao salvar: {exc}", "danger")

    return render_template("options/form.html", option=None, dropdown_fields=DROPDOWN_FIELDS)


@options_bp.route("/<int:option_id>/editar", methods=["GET", "POST"])
def edit_option(option_id):
    option = ContractOption.query.get_or_404(option_id)
    if request.method == "POST":
        try:
            data = _parse_form()
            # option_value é preservado — não regerar para não quebrar contratos já salvos
            option.field_name = data["field_name"]
            option.option_label = data["option_label"]
            option.full_text = data["full_text"]
            option.is_active = data["is_active"]
            option.sort_order = data["sort_order"]
            option.extra_data = data["extra_data"]
            db.session.commit()
            flash("Opção atualizada com sucesso.", "success")
            return redirect(url_for("options.list_options"))
        except (json.JSONDecodeError, ValueError) as exc:
            flash(f"Erro ao salvar: {exc}", "danger")

    return render_template("options/form.html", option=option, dropdown_fields=DROPDOWN_FIELDS)


@options_bp.route("/<int:option_id>/desativar", methods=["POST"])
def deactivate_option(option_id):
    option = ContractOption.query.get_or_404(option_id)
    option.is_active = False
    db.session.commit()
    flash("Opção desativada.", "warning")
    return redirect(url_for("options.list_options"))
