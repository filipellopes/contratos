import json
import re
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from app.extensions import db
from app.models.contract_generation import ContractGeneration
from app.models.contract_option import DROPDOWN_FIELDS, ContractOption
from app.models.contracted_company import ContractedCompany
from app.models.generation_log import GenerationLog
from app.services.context_builder import build_contract_context
from app.services.docx_generator import generate_docx
from app.services.form_validator import ValidationError, validate_contract_form
from app.services.formatters import only_digits, parse_currency, parse_date
from app.services.pdf_converter import convert_docx_to_pdf

contracts_bp = Blueprint("contracts", __name__)

CONTRACT_FIELD_LABELS = {
    "generated_by_name": "Nome de quem está gerando",
    "tipo_servico": "Tipo de serviço",
    "inicio_vigencia": "Início da vigência",
    "forma_pagamento": "Forma de pagamento",
    "dia_vencimento": "Dia do vencimento",
    "mes_vencimento": "Mês do vencimento",
    "reajuste": "Reajuste",
    "decima_terceira_parcela": "13ª parcela",
    "rescisao": "Rescisão",
    "suspensao": "Suspensão",
    "foro": "Foro",
    "detalhamento_servico": "Detalhamento do serviço",
    "contratantes": "Contratante(s)",
    "empresa_contratada_id": "Empresa contratada",
    "cnpj_contratada": "CNPJ contratada",
    "endereco_contratado": "Endereço contratado",
    "nome_contratado": "Nome contratado",
    "cpf_contratado": "CPF contratado",
    "crc_contratado": "CRC contratado",
    "local": "Local",
    "data_contrato": "Data do contrato",
}

CONTRATANTE_FIELD_LABELS = {
    "cnpj": "CNPJ",
    "enquadramento_tributario": "Enquadramento tributário",
    "razao_social": "Razão social",
    "valor_mensal": "Valor mensal",
    "nome": "Nome (pessoa física)",
    "cpf": "CPF",
}


def _error_label(key):
    match = re.match(r"contratantes\[(\d+)\]\.(\w+)", key)
    if match:
        index = int(match.group(1)) + 1
        field = CONTRATANTE_FIELD_LABELS.get(match.group(2), match.group(2))
        return f"Contratante {index} — {field}"
    return CONTRACT_FIELD_LABELS.get(key, key)


def _build_error_summary(errors):
    return [(_error_label(key), message) for key, message in errors.items()]


def _parse_contratantes():
    indices = set()
    for key in request.form:
        if key.startswith("contratantes[") and "][" in key:
            index = key.split("[")[1].split("]")[0]
            indices.add(index)

    contratantes = []
    for index in sorted(indices, key=lambda x: int(x)):
        contratantes.append(
            {
                "cnpj": request.form.get(f"contratantes[{index}][cnpj]", ""),
                "enquadramento_tributario": request.form.get(
                    f"contratantes[{index}][enquadramento_tributario]", ""
                ),
                "razao_social": request.form.get(f"contratantes[{index}][razao_social]", ""),
                "valor_mensal": request.form.get(f"contratantes[{index}][valor_mensal]", ""),
                "nome": request.form.get(f"contratantes[{index}][nome]", ""),
                "cpf": request.form.get(f"contratantes[{index}][cpf]", ""),
            }
        )
    return contratantes


def _parse_form_data():
    company_id = request.form.get("empresa_contratada_id")
    company = ContractedCompany.query.get(company_id) if company_id else None

    return {
        "generated_by_name": request.form.get("generated_by_name", "").strip(),
        "tipo_servico": request.form.get("tipo_servico", ""),
        "inicio_vigencia": request.form.get("inicio_vigencia", ""),
        "forma_pagamento": request.form.get("forma_pagamento", ""),
        "dia_vencimento": request.form.get("dia_vencimento", ""),
        "mes_vencimento": request.form.get("mes_vencimento", ""),
        "reajuste": request.form.get("reajuste", ""),
        "decima_terceira_parcela": request.form.get("decima_terceira_parcela", ""),
        "rescisao": request.form.get("rescisao", ""),
        "suspensao": request.form.get("suspensao", ""),
        "foro": request.form.get("foro", ""),
        "detalhamento_servico": request.form.get("detalhamento_servico", ""),
        "contratantes": _parse_contratantes(),
        "empresa_contratada_id": company_id,
        "empresa_contratada_nome": company.company_name if company else "",
        "cnpj_contratada": request.form.get("cnpj_contratada", ""),
        "endereco_contratado": request.form.get("endereco_contratado", ""),
        "nome_contratado": request.form.get("nome_contratado", ""),
        "cpf_contratado": request.form.get("cpf_contratado", ""),
        "crc_contratado": request.form.get("crc_contratado", ""),
        "local": request.form.get("local", "").strip(),
        "data_contrato": request.form.get("data_contrato", ""),
    }


def _load_dropdown_options():
    options = {}
    for field in DROPDOWN_FIELDS:
        options[field] = (
            ContractOption.query.filter_by(field_name=field, is_active=True)
            .order_by(ContractOption.sort_order, ContractOption.option_label)
            .all()
        )
    return options


def _add_log(contract, action, message, details=None):
    log = GenerationLog(
        contract_generation_id=contract.id,
        action=action,
        message=message,
    )
    log.details = details or {}
    db.session.add(log)


def _client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr


@contracts_bp.route("/contratos")
def list_contracts():
    contracts = ContractGeneration.query.order_by(ContractGeneration.created_at.desc()).all()
    return render_template("contracts/list.html", contracts=contracts)


def _render_contract_form(form_data=None, errors=None):
    errors = errors or {}
    companies = ContractedCompany.query.filter_by(is_active=True).order_by(
        ContractedCompany.company_name
    ).all()
    return render_template(
        "contracts/form.html",
        dropdown_options=_load_dropdown_options(),
        companies=companies,
        form_data=form_data,
        errors=errors,
        error_summary=_build_error_summary(errors) if errors else [],
    )


@contracts_bp.route("/contratos/novo", methods=["GET"])
def new_contract():
    return _render_contract_form()


@contracts_bp.route("/contratos/editar", methods=["GET"])
def edit_contract():
    raw = session.get("pending_contract")
    if not raw:
        flash("Sessão expirada. Preencha o formulário novamente.", "warning")
        return redirect(url_for("contracts.new_contract"))
    return _render_contract_form(form_data=json.loads(raw))


@contracts_bp.route("/contratos/preview", methods=["POST"])
def preview_contract():
    form_data = _parse_form_data()
    try:
        validate_contract_form(form_data)
        context = build_contract_context(form_data)
        session["pending_contract"] = json.dumps(form_data, ensure_ascii=False)
        session["pending_context"] = json.dumps(context, default=str, ensure_ascii=False)
        return render_template("contracts/preview.html", context=context, form_data=form_data)
    except ValidationError as exc:
        return _render_contract_form(form_data=form_data, errors=exc.errors)


@contracts_bp.route("/contratos/gerar", methods=["POST"])
def generate_contract():
    raw = session.get("pending_contract")
    if not raw:
        flash("Sessão expirada. Preencha o formulário novamente.", "warning")
        return redirect(url_for("contracts.new_contract"))

    form_data = json.loads(raw)
    context = build_contract_context(form_data)

    primeira = form_data["contratantes"][0]
    total = sum(parse_currency(c.get("valor_mensal")) or 0 for c in form_data["contratantes"])

    contract = ContractGeneration(
        generated_by_name=form_data["generated_by_name"],
        contratante_razao_social=primeira.get("razao_social", ""),
        contratante_cnpj=only_digits(primeira.get("cnpj", "")),
        tipo_servico=context["tipo_servico"],
        valor_mensal=total,
        empresa_contratada=context["empresa_contratada"],
        local=form_data.get("local"),
        data_contrato=parse_date(form_data.get("data_contrato")),
        status="rascunho",
        form_data_json=json.dumps(form_data, ensure_ascii=False),
    )
    db.session.add(contract)
    db.session.flush()

    _add_log(
        contract,
        "validacao",
        "Formulário validado com sucesso.",
        {"ip": _client_ip(), "generated_by": form_data["generated_by_name"]},
    )

    try:
        docx_path = generate_docx(context, primeira.get("razao_social", "contrato"))
        contract.docx_path = str(docx_path)
        contract.status = "gerado_com_sucesso"
        _add_log(contract, "render_docx", "DOCX gerado com sucesso.", {"path": str(docx_path)})

        try:
            pdf_path = convert_docx_to_pdf(docx_path)
            if pdf_path:
                contract.pdf_path = str(pdf_path)
                _add_log(contract, "convert_pdf", "PDF gerado com sucesso.", {"path": str(pdf_path)})
            else:
                _add_log(
                    contract,
                    "convert_pdf",
                    "PDF não gerado — LibreOffice indisponível (modo auto).",
                    {"hint": "No VPS Linux: apt install libreoffice-writer-nogui"},
                )
        except Exception as pdf_exc:
            contract.status = "erro_ao_converter_pdf"
            contract.error_message = str(pdf_exc)
            _add_log(contract, "erro", "Erro na conversão PDF.", {"error": str(pdf_exc)})

    except Exception as docx_exc:
        contract.status = "erro_ao_gerar_docx"
        contract.error_message = str(docx_exc)
        _add_log(contract, "erro", "Erro na geração DOCX.", {"error": str(docx_exc)})

    db.session.commit()
    session.pop("pending_contract", None)
    session.pop("pending_context", None)

    if contract.status.startswith("erro"):
        msg = (contract.error_message or "").split("\n")[0]
        flash(f"Contrato registrado com erro: {msg}", "danger")
    elif contract.docx_path and not contract.pdf_path:
        flash(
            "Contrato Word gerado com sucesso. PDF não foi gerado "
            "(LibreOffice indisponível neste ambiente — no VPS Linux será gerado automaticamente).",
            "warning",
        )
    else:
        flash("Contrato gerado com sucesso!", "success")

    return redirect(url_for("contracts.contract_detail", contract_id=contract.id))


@contracts_bp.route("/contratos/<int:contract_id>")
def contract_detail(contract_id):
    contract = ContractGeneration.query.get_or_404(contract_id)
    form_data = json.loads(contract.form_data_json)
    logs = contract.logs.order_by(GenerationLog.created_at.desc()).all()
    return render_template(
        "contracts/detail.html",
        contract=contract,
        form_data=form_data,
        logs=logs,
    )


@contracts_bp.route("/contratos/<int:contract_id>/download/docx")
def download_docx(contract_id):
    contract = ContractGeneration.query.get_or_404(contract_id)
    if not contract.docx_path:
        abort(404)
    return send_file(contract.docx_path, as_attachment=True)


@contracts_bp.route("/contratos/<int:contract_id>/download/pdf")
def download_pdf(contract_id):
    contract = ContractGeneration.query.get_or_404(contract_id)
    if not contract.pdf_path:
        abort(404)
    return send_file(contract.pdf_path, as_attachment=True)


@contracts_bp.route("/contratos/<int:contract_id>/gerar-pdf", methods=["POST"])
def retry_pdf(contract_id):
    contract = ContractGeneration.query.get_or_404(contract_id)
    if not contract.docx_path:
        flash("DOCX não disponível para conversão.", "danger")
        return redirect(url_for("contracts.contract_detail", contract_id=contract.id))

    try:
        pdf_path = convert_docx_to_pdf(Path(contract.docx_path), required="required")
        if not pdf_path:
            flash("LibreOffice indisponível. Instale no servidor ou use Docker.", "warning")
            return redirect(url_for("contracts.contract_detail", contract_id=contract.id))

        contract.pdf_path = str(pdf_path)
        contract.status = "gerado_com_sucesso"
        contract.error_message = None
        _add_log(contract, "convert_pdf", "PDF gerado com sucesso (nova tentativa).", {"path": str(pdf_path)})
        db.session.commit()
        flash("PDF gerado com sucesso!", "success")
    except Exception as exc:
        contract.status = "erro_ao_converter_pdf"
        contract.error_message = str(exc)
        _add_log(contract, "erro", "Erro na conversão PDF (nova tentativa).", {"error": str(exc)})
        db.session.commit()
        flash(str(exc).split("\n")[0], "danger")

    return redirect(url_for("contracts.contract_detail", contract_id=contract.id))
