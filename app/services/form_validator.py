from app.services.formatters import only_digits, parse_currency, parse_date


class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(str(errors))


def _require(value, field, errors):
    if value is None or str(value).strip() == "":
        errors[field] = "Campo obrigatório."


def validate_contract_form(data):
    errors = {}

    _require(data.get("generated_by_name"), "generated_by_name", errors)
    _require(data.get("tipo_servico"), "tipo_servico", errors)
    _require(data.get("forma_pagamento"), "forma_pagamento", errors)
    _require(data.get("mes_vencimento"), "mes_vencimento", errors)
    _require(data.get("reajuste"), "reajuste", errors)
    _require(data.get("decima_terceira_parcela"), "decima_terceira_parcela", errors)
    _require(data.get("rescisao"), "rescisao", errors)
    _require(data.get("suspensao"), "suspensao", errors)
    _require(data.get("foro"), "foro", errors)
    _require(data.get("detalhamento_servico"), "detalhamento_servico", errors)
    _require(data.get("empresa_contratada_id"), "empresa_contratada_id", errors)
    _require(data.get("local"), "local", errors)
    _require(data.get("data_contrato"), "data_contrato", errors)

    inicio = parse_date(data.get("inicio_vigencia"))
    if not inicio:
        errors["inicio_vigencia"] = "Data de início inválida."

    data_contrato = parse_date(data.get("data_contrato"))
    if data.get("data_contrato") and not data_contrato:
        errors["data_contrato"] = "Data do contrato inválida."

    try:
        dia = int(data.get("dia_vencimento", ""))
        if dia < 1 or dia > 31:
            errors["dia_vencimento"] = "Dia de vencimento deve estar entre 1 e 31."
    except (TypeError, ValueError):
        errors["dia_vencimento"] = "Dia de vencimento inválido."

    contratantes = data.get("contratantes") or []
    if not contratantes:
        errors["contratantes"] = "Informe ao menos uma contratante."

    for index, contratante in enumerate(contratantes):
        prefix = f"contratantes[{index}]"
        _require(contratante.get("cnpj"), f"{prefix}.cnpj", errors)
        _require(contratante.get("enquadramento_tributario"), f"{prefix}.enquadramento_tributario", errors)
        _require(contratante.get("razao_social"), f"{prefix}.razao_social", errors)
        _require(contratante.get("valor_mensal"), f"{prefix}.valor_mensal", errors)
        _require(contratante.get("nome"), f"{prefix}.nome", errors)
        _require(contratante.get("cpf"), f"{prefix}.cpf", errors)

        cnpj_digits = only_digits(contratante.get("cnpj"))
        if cnpj_digits and len(cnpj_digits) != 14:
            errors[f"{prefix}.cnpj"] = "CNPJ deve conter 14 dígitos."

        cpf_digits = only_digits(contratante.get("cpf"))
        if cpf_digits and len(cpf_digits) != 11:
            errors[f"{prefix}.cpf"] = "CPF deve conter 11 dígitos."

        valor = parse_currency(contratante.get("valor_mensal"))
        if contratante.get("valor_mensal") and valor is None:
            errors[f"{prefix}.valor_mensal"] = "Valor mensal inválido."

    _require(data.get("cnpj_contratada"), "cnpj_contratada", errors)
    _require(data.get("endereco_contratado"), "endereco_contratado", errors)
    _require(data.get("nome_contratado"), "nome_contratado", errors)
    _require(data.get("cpf_contratado"), "cpf_contratado", errors)
    _require(data.get("crc_contratado"), "crc_contratado", errors)

    cnpj_contratada = only_digits(data.get("cnpj_contratada"))
    if cnpj_contratada and len(cnpj_contratada) != 14:
        errors["cnpj_contratada"] = "CNPJ da contratada deve conter 14 dígitos."

    cpf_contratado = only_digits(data.get("cpf_contratado"))
    if cpf_contratado and len(cpf_contratado) != 11:
        errors["cpf_contratado"] = "CPF do contratado deve conter 11 dígitos."

    if errors:
        raise ValidationError(errors)

    return data
