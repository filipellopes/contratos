from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models.contracted_company import ContractedCompany
from app.services.formatters import format_cnpj, format_cpf, only_digits

companies_bp = Blueprint("companies", __name__, url_prefix="/empresas-contratadas")


def _parse_form():
    return {
        "company_name": request.form.get("company_name", "").strip(),
        "cnpj": only_digits(request.form.get("cnpj", "")),
        "address": request.form.get("address", "").strip(),
        "responsible_name": request.form.get("responsible_name", "").strip(),
        "responsible_cpf": only_digits(request.form.get("responsible_cpf", "")),
        "crc": request.form.get("crc", "").strip(),
        "is_active": request.form.get("is_active") == "on",
    }


@companies_bp.route("")
def list_companies():
    companies = ContractedCompany.query.order_by(ContractedCompany.company_name).all()
    return render_template("companies/list.html", companies=companies)


@companies_bp.route("/nova", methods=["GET", "POST"])
def create_company():
    if request.method == "POST":
        data = _parse_form()
        if not data["company_name"] or len(data["cnpj"]) != 14:
            flash("Informe nome e CNPJ válido.", "danger")
        else:
            company = ContractedCompany(**data)
            db.session.add(company)
            db.session.commit()
            flash("Empresa cadastrada com sucesso.", "success")
            return redirect(url_for("companies.list_companies"))
    return render_template("companies/form.html", company=None)


@companies_bp.route("/<int:company_id>/editar", methods=["GET", "POST"])
def edit_company(company_id):
    company = ContractedCompany.query.get_or_404(company_id)
    if request.method == "POST":
        data = _parse_form()
        for key, value in data.items():
            setattr(company, key, value)
        db.session.commit()
        flash("Empresa atualizada com sucesso.", "success")
        return redirect(url_for("companies.list_companies"))
    return render_template("companies/form.html", company=company)


@companies_bp.route("/<int:company_id>/desativar", methods=["POST"])
def deactivate_company(company_id):
    company = ContractedCompany.query.get_or_404(company_id)
    company.is_active = False
    db.session.commit()
    flash("Empresa desativada.", "warning")
    return redirect(url_for("companies.list_companies"))


@companies_bp.route("/api/<int:company_id>")
def api_company(company_id):
    from flask import jsonify

    company = ContractedCompany.query.get_or_404(company_id)
    data = company.to_dict()
    data["cnpj_formatted"] = format_cnpj(company.cnpj)
    data["responsible_cpf_formatted"] = format_cpf(company.responsible_cpf)
    return jsonify(data)
