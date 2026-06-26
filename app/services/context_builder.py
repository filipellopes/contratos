from app.models.contract_option import ContractOption
from app.models.contracted_company import ContractedCompany
from app.services.formatters import (
    format_cnpj,
    format_cpf,
    format_currency,
    format_date,
    format_date_extenso,
    join_enquadramentos,
    parse_currency,
    parse_date,
)


def _get_option(field_name, option_value):
    if not option_value:
        return None
    return ContractOption.query.filter_by(
        field_name=field_name,
        option_value=option_value,
        is_active=True,
    ).first()


def _build_texto_partes(contratantes, contratada):
    partes = []
    for index, c in enumerate(contratantes):
        if index == 0:
            prefix = "representado por "
        elif index == len(contratantes) - 1:
            prefix = " e "
        else:
            prefix = ", "
        partes.append(f"{prefix}{c['nome']}, CPF nº {c['cpf']}")

    representantes = "".join(partes)
    return (
        f"Doravante denominado CONTRATANTE, {representantes}, e o contador "
        f"{contratada['nome_contratado']}, com escritório {contratada['empresa_contratada']}, "
        f"CNPJ {contratada['cnpj_contratada']}, {contratada['endereco_contratado']}, "
        f"CRC nº {contratada['crc_contratado']}, doravante denominado CONTRATADA."
    )


def build_contract_context(form_data):
    contratantes_raw = form_data.get("contratantes") or []
    contratantes = []
    total = 0
    enquadramentos = []

    for item in contratantes_raw:
        enq_option = _get_option("enquadramento_tributario", item.get("enquadramento_tributario"))
        enq_label = enq_option.option_label if enq_option else item.get("enquadramento_tributario", "")
        enquadramentos.append(enq_label)
        valor = parse_currency(item.get("valor_mensal")) or 0
        total += valor
        contratantes.append(
            {
                "cnpj": format_cnpj(item.get("cnpj")),
                "enquadramento": enq_label,
                "razao_social": item.get("razao_social", ""),
                "valor_mensal_formatado": format_currency(valor),
                "nome": item.get("nome", ""),
                "cpf": format_cpf(item.get("cpf")),
            }
        )

    company = ContractedCompany.query.get(form_data.get("empresa_contratada_id"))
    empresa_nome = company.company_name if company else form_data.get("empresa_contratada_nome", "")

    contratada = {
        "empresa_contratada": empresa_nome,
        "cnpj_contratada": format_cnpj(form_data.get("cnpj_contratada")),
        "endereco_contratado": form_data.get("endereco_contratado", ""),
        "nome_contratado": form_data.get("nome_contratado", ""),
        "cpf_contratado": format_cpf(form_data.get("cpf_contratado")),
        "crc_contratado": form_data.get("crc_contratado", ""),
    }

    tipo_servico = _get_option("tipo_servico", form_data.get("tipo_servico"))
    forma_pagamento = _get_option("forma_pagamento", form_data.get("forma_pagamento"))
    mes_vencimento = _get_option("mes_vencimento", form_data.get("mes_vencimento"))
    reajuste = _get_option("reajuste", form_data.get("reajuste"))
    decima_terceira = _get_option("decima_terceira_parcela", form_data.get("decima_terceira_parcela"))
    rescisao = _get_option("rescisao", form_data.get("rescisao"))
    suspensao = _get_option("suspensao", form_data.get("suspensao"))
    foro = _get_option("foro", form_data.get("foro"))
    detalhamento = _get_option("detalhamento_servico", form_data.get("detalhamento_servico"))

    dia_vencimento = int(form_data.get("dia_vencimento"))
    inicio_vigencia = parse_date(form_data.get("inicio_vigencia"))
    data_contrato = parse_date(form_data.get("data_contrato"))
    local = form_data.get("local", "")

    texto_forma_pagamento = forma_pagamento.full_text if forma_pagamento and forma_pagamento.full_text else (
        f"{dia_vencimento} de {mes_vencimento.option_label if mes_vencimento else form_data.get('mes_vencimento', '')} de cada mês"
    )

    exibir_clausula = True
    if decima_terceira:
        exibir_clausula = decima_terceira.extra_data.get("exibir_clausula", True)

    texto_decima_terceira = ""
    if decima_terceira and decima_terceira.full_text:
        texto_decima_terceira = decima_terceira.full_text
    elif exibir_clausula:
        texto_decima_terceira = (
            "4.6  Adicionalmente, será paga uma parcela extra referente ao encerramento "
            "das demonstrações contábeis anuais, Declaração de Rendimentos da Pessoa Jurídica, "
            "Declaração de Movimento Fiscal Estadual (inventário anual), transmissão da "
            "Escrituração Contábil Digital (ECD), transmissão da Escrituração Contábil Fiscal (ECF) "
            "e atendimento à Declaração Anual de Incentivos Fiscais administrados pela SUDENE (DAIF)."
        )

    texto_rescisao = rescisao.full_text if rescisao and rescisao.full_text else (
        f"Qualquer parte pode rescindi-lo mediante aviso prévio de {rescisao.option_label if rescisao else ''} por e-mail para info@valore.com.br."
    )

    context = {
        "tipo_servico": tipo_servico.option_label if tipo_servico else form_data.get("tipo_servico", ""),
        "empresa_contratada": empresa_nome,
        "inicio_vigencia_formatada": format_date(inicio_vigencia),
        "texto_vigencia": "12 meses, com renovação automática",
        "texto_forma_pagamento": texto_forma_pagamento,
        "texto_reajuste": reajuste.option_label if reajuste else "",
        "label_reajuste": reajuste.option_label if reajuste else "",
        "label_decima_terceira_parcela": decima_terceira.option_label if decima_terceira else "",
        "label_rescisao": rescisao.option_label if rescisao else "",
        "label_suspensao": suspensao.option_label if suspensao else "",
        "texto_foro": foro.full_text if foro and foro.full_text else (foro.option_label if foro else local),
        "contratantes": contratantes,
        "texto_partes": _build_texto_partes(contratantes, contratada),
        "texto_regime_tributario": join_enquadramentos(enquadramentos),
        "texto_detalhamento_servico": detalhamento.full_text if detalhamento and detalhamento.full_text else "",
        "texto_vigencia_clausula": (
            f"3.1  Este Contrato entra em vigor em {format_date(inicio_vigencia)} e tem duração de "
            f"12 (doze) meses, renovando-se automaticamente por períodos iguais. {texto_rescisao} "
            f"Todos os pagamentos vencidos até a rescisão efetiva permanecem devidos."
        ),
        "texto_rescisao": texto_rescisao,
        "valor_mensal_total_formatado": format_currency(total),
        "texto_clausula_4_1": (
            f"4.1  Os honorários mensais são de {format_currency(total)}, com vencimento conforme "
            f"{texto_forma_pagamento}."
        ),
        "texto_clausula_4_2": reajuste.full_text if reajuste and reajuste.full_text else f"4.2  {reajuste.option_label if reajuste else ''}",
        "exibir_clausula_decima_terceira": exibir_clausula,
        "texto_decima_terceira_parcela": texto_decima_terceira,
        "texto_suspensao": suspensao.full_text if suspensao and suspensao.full_text else (
            f"6.9  {suspensao.option_label if suspensao else ''}"
        ),
        "texto_clausula_8_1": (
            f"8.1  Fica eleito o foro da Comarca de {foro.option_label if foro else local} "
            f"para dirimir quaisquer litígios decorrentes deste Contrato."
        ),
        **contratada,
        "local": local,
        "data_formatada": format_date(data_contrato),
        "data_extenso": format_date_extenso(data_contrato, local=local),
        "valor_mensal_total": total,
    }
    return context
