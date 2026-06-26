import json

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models.contract_option import DROPDOWN_FIELDS, ContractOption, FIELD_NAMES

options_bp = Blueprint("options", __name__, url_prefix="/opcoes")


def _parse_form():
    extra_raw = request.form.get("extra_data_json", "").strip()
    extra_data = {}
    if extra_raw:
        extra_data = json.loads(extra_raw)

    return {
        "field_name": request.form.get("field_name", "").strip(),
        "option_label": request.form.get("option_label", "").strip(),
        "option_value": request.form.get("option_value", "").strip(),
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
            option = ContractOption(**{k: v for k, v in data.items() if k != "extra_data"})
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
            for key, value in data.items():
                if key == "extra_data":
                    option.extra_data = value
                else:
                    setattr(option, key, value)
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
