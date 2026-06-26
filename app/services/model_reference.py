"""Referência do modelo de contrato — variáveis, campos e opções."""

from app.models.contract_option import DROPDOWN_FIELDS, FIELD_NAMES

# Variáveis que o sistema monta para o Word (docxtpl)
WORD_VARIABLES = [
    {
        "variable": "tipo_servico",
        "section": "Tabela resumo",
        "where": "Linha «Serviço»",
        "source": "Opção → nome exibido (option_label)",
        "option_field": "tipo_servico",
    },
    {
        "variable": "empresa_contratada",
        "section": "Tabela resumo",
        "where": "Linha «Prestadora»",
        "source": "Cadastro em Empresas contratadas → company_name",
        "option_field": None,
    },
    {
        "variable": "inicio_vigencia_formatada",
        "section": "Tabela resumo / Cláusula 3.1",
        "where": "Início da vigência",
        "source": "Formulário → data início (dd/mm/aaaa)",
        "option_field": None,
    },
    {
        "variable": "texto_vigencia",
        "section": "Tabela resumo",
        "where": "Texto fixo após data de início",
        "source": "Fixo: «12 meses, com renovação automática»",
        "option_field": None,
    },
    {
        "variable": "texto_forma_pagamento",
        "section": "Tabela resumo / Cláusula 4.1",
        "where": "Linha «Pagamento»",
        "source": "Opção forma_pagamento → full_text (ou dia + mês do formulário)",
        "option_field": "forma_pagamento",
    },
    {
        "variable": "texto_reajuste",
        "section": "Tabela resumo",
        "where": "Linha «Reajuste»",
        "source": "Opção reajuste → option_label (resumo)",
        "option_field": "reajuste",
    },
    {
        "variable": "label_decima_terceira_parcela",
        "section": "Tabela resumo",
        "where": "Linha «13ª Parcela»",
        "source": "Opção decima_terceira_parcela → option_label",
        "option_field": "decima_terceira_parcela",
    },
    {
        "variable": "label_rescisao",
        "section": "Tabela resumo",
        "where": "Linha «Rescisão»",
        "source": "Opção rescisao → option_label",
        "option_field": "rescisao",
    },
    {
        "variable": "label_suspensao",
        "section": "Tabela resumo",
        "where": "Linha «Suspensão»",
        "source": "Opção suspensao → option_label",
        "option_field": "suspensao",
    },
    {
        "variable": "texto_foro",
        "section": "Tabela resumo",
        "where": "Linha «Foro»",
        "source": "Opção foro → option_label ou full_text",
        "option_field": "foro",
    },
    {
        "variable": "cnpj",
        "section": "Tabela contratantes",
        "where": "Coluna CNPJ (1ª linha; duplicada para N contratantes)",
        "source": "Formulário → CNPJ de cada contratante",
        "option_field": None,
    },
    {
        "variable": "enquadramento",
        "section": "Tabela contratantes",
        "where": "Coluna Enquadramento tributário",
        "source": "Opção enquadramento_tributario → option_label",
        "option_field": "enquadramento_tributario",
    },
    {
        "variable": "razao_social",
        "section": "Tabela contratantes",
        "where": "Coluna Razão social",
        "source": "Formulário → razão social",
        "option_field": None,
    },
    {
        "variable": "valor_mensal_formatado",
        "section": "Tabela contratantes",
        "where": "Coluna Valor mensal",
        "source": "Formulário → valor mensal (R$ formatado)",
        "option_field": None,
    },
    {
        "variable": "texto_partes",
        "section": "Introdução das partes",
        "where": "Parágrafo após tabela de contratantes",
        "source": "Montado em Python (representantes + dados da contratada)",
        "option_field": None,
    },
    {
        "variable": "texto_regime_tributario",
        "section": "Cláusula 2.1",
        "where": "Regime tributário da contratante",
        "source": "União dos enquadramentos das contratantes",
        "option_field": "enquadramento_tributario",
    },
    {
        "variable": "texto_detalhamento_servico",
        "section": "Cláusula 2.2",
        "where": "Escopo dos serviços (pode ser longo)",
        "source": "Opção detalhamento_servico → full_text",
        "option_field": "detalhamento_servico",
    },
    {
        "variable": "texto_vigencia_clausula",
        "section": "Cláusula 3.1",
        "where": "Parágrafo inteiro de vigência",
        "source": "Data início + opção rescisao → full_text",
        "option_field": "rescisao",
    },
    {
        "variable": "texto_clausula_4_1",
        "section": "Cláusula 4.1",
        "where": "Honorários mensais totais",
        "source": "Soma dos valores + forma de pagamento",
        "option_field": "forma_pagamento",
    },
    {
        "variable": "texto_clausula_4_2",
        "section": "Cláusula 4.2",
        "where": "Reajuste anual",
        "source": "Opção reajuste → full_text",
        "option_field": "reajuste",
    },
    {
        "variable": "exibir_clausula_decima_terceira",
        "section": "Cláusula 4.6",
        "where": "Bloco condicional {% if %}",
        "source": "Opção decima_terceira_parcela → extra_data.exibir_clausula",
        "option_field": "decima_terceira_parcela",
    },
    {
        "variable": "texto_decima_terceira_parcela",
        "section": "Cláusula 4.6",
        "where": "Texto da 13ª parcela (se exibir)",
        "source": "Opção decima_terceira_parcela → full_text",
        "option_field": "decima_terceira_parcela",
    },
    {
        "variable": "texto_suspensao",
        "section": "Cláusula 6.9",
        "where": "Suspensão por inadimplência",
        "source": "Opção suspensao → full_text",
        "option_field": "suspensao",
    },
    {
        "variable": "texto_clausula_8_1",
        "section": "Cláusula 8.1",
        "where": "Foro eleito",
        "source": "Opção foro → option_label",
        "option_field": "foro",
    },
    {
        "variable": "bloco_assinatura_contratantes",
        "section": "Assinaturas",
        "where": "Coluna esquerda da tabela de assinaturas",
        "source": "Nomes e CPFs de todos os representantes da contratante",
        "option_field": None,
    },
    {
        "variable": "bloco_assinatura_contratada",
        "section": "Assinaturas",
        "where": "Coluna direita da tabela de assinaturas",
        "source": "Nome e CPF do responsável da contratada",
        "option_field": None,
    },
    {
        "variable": "data_extenso",
        "section": "Assinaturas",
        "where": "Local e data por extenso",
        "source": "Formulário → local + data",
        "option_field": None,
    },
    {
        "variable": "cnpj_contratada",
        "section": "Introdução / assinaturas",
        "where": "Dados da contratada no texto_partes",
        "source": "Empresa contratada (cadastro ou formulário)",
        "option_field": None,
    },
    {
        "variable": "nome_contratado",
        "section": "Assinaturas",
        "where": "Bloco CONTRATADA",
        "source": "Empresa contratada → responsável",
        "option_field": None,
    },
    {
        "variable": "cpf_contratado",
        "section": "Assinaturas",
        "where": "Bloco CONTRATADA",
        "source": "Empresa contratada → CPF responsável",
        "option_field": None,
    },
    {
        "variable": "crc_contratado",
        "section": "Introdução das partes",
        "where": "CRC do contador",
        "source": "Empresa contratada → CRC",
        "option_field": None,
    },
]

OPTION_FIELD_GUIDE = [
    {
        "field_name": "tipo_servico",
        "form_block": "Bloco 1",
        "valor_interno_hint": "assessoria_contabil",
        "full_text_use": "Não usado no resumo — usa option_label",
        "extra_data_use": "—",
    },
    {
        "field_name": "forma_pagamento",
        "form_block": "Bloco 1",
        "valor_interno_hint": "boleto, pix",
        "full_text_use": "Cláusula 4.1 e linha Pagamento do resumo (ex.: «via boleto bancário»)",
        "extra_data_use": "—",
    },
    {
        "field_name": "mes_vencimento",
        "form_block": "Bloco 1",
        "valor_interno_hint": "dia_fixo",
        "full_text_use": "Combinado com dia_vencimento se forma_pagamento não tiver full_text",
        "extra_data_use": "—",
    },
    {
        "field_name": "reajuste",
        "form_block": "Bloco 1",
        "valor_interno_hint": "sm_ipca_igpm",
        "full_text_use": "Cláusula 4.2 (texto completo). Resumo usa option_label",
        "extra_data_use": "—",
    },
    {
        "field_name": "decima_terceira_parcela",
        "form_block": "Bloco 1",
        "valor_interno_hint": "sim, nao",
        "full_text_use": "Cláusula 4.6 quando exibir_clausula=true",
        "extra_data_use": '{"exibir_clausula": true} ou false',
    },
    {
        "field_name": "rescisao",
        "form_block": "Bloco 1",
        "valor_interno_hint": "60_dias, 90_dias",
        "full_text_use": "Cláusula 3.1 (trecho de aviso prévio). Resumo usa option_label",
        "extra_data_use": "—",
    },
    {
        "field_name": "suspensao",
        "form_block": "Bloco 1",
        "valor_interno_hint": "inadimplencia_2",
        "full_text_use": "Cláusula 6.9 (parágrafo completo)",
        "extra_data_use": "—",
    },
    {
        "field_name": "foro",
        "form_block": "Bloco 1",
        "valor_interno_hint": "recife_pe",
        "full_text_use": "Resumo e cláusula 8.1",
        "extra_data_use": "—",
    },
    {
        "field_name": "enquadramento_tributario",
        "form_block": "Bloco 2 (por contratante)",
        "valor_interno_hint": "simples, lucro_presumido, lucro_real",
        "full_text_use": "Tabela contratantes + cláusula 2.1 (via labels)",
        "extra_data_use": "—",
    },
    {
        "field_name": "detalhamento_servico",
        "form_block": "Bloco 2 (global)",
        "valor_interno_hint": "escopo_padrao",
        "full_text_use": "Cláusula 2.2 inteira — pode incluir itens a/b/c",
        "extra_data_use": "—",
    },
]

FORM_FIELDS = [
    {"field": "generated_by_name", "block": "Identificação", "type": "texto", "required": True},
    {"field": "inicio_vigencia", "block": "Bloco 1", "type": "data", "required": True},
    {"field": "dia_vencimento", "block": "Bloco 1", "type": "número 1–31", "required": True},
    {"field": "contratantes[].cnpj", "block": "Bloco 2", "type": "CNPJ", "required": True},
    {"field": "contratantes[].razao_social", "block": "Bloco 2", "type": "texto", "required": True},
    {"field": "contratantes[].valor_mensal", "block": "Bloco 2", "type": "moeda", "required": True},
    {"field": "contratantes[].nome", "block": "Bloco 2", "type": "texto (representante PF)", "required": True},
    {"field": "contratantes[].cpf", "block": "Bloco 2", "type": "CPF", "required": True},
    {"field": "empresa_contratada_id", "block": "Bloco 3", "type": "lista (Empresas)", "required": True},
    {"field": "cnpj_contratada", "block": "Bloco 3", "type": "CNPJ", "required": True},
    {"field": "endereco_contratado", "block": "Bloco 3", "type": "texto", "required": True},
    {"field": "nome_contratado", "block": "Bloco 3", "type": "texto", "required": True},
    {"field": "cpf_contratado", "block": "Bloco 3", "type": "CPF", "required": True},
    {"field": "crc_contratado", "block": "Bloco 3", "type": "texto", "required": True},
    {"field": "local", "block": "Bloco 4", "type": "texto", "required": True},
    {"field": "data_contrato", "block": "Bloco 4", "type": "data", "required": True},
]


def get_template_placeholders():
    """Lê placeholders presentes no arquivo .docx atual."""
    import re
    import zipfile
    from pathlib import Path

    from flask import current_app

    path = Path(current_app.config["TEMPLATE_DOCX"])
    if not path.exists():
        return []

    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    texts = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)
    full = "".join(texts)
    return sorted(set(re.findall(r"\{\{[^}]+\}\}|\{%[^%]+%\}", full)))
