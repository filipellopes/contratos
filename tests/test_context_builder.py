"""Testes do montador de contexto do contrato."""

import pytest

from app import create_app
from app.extensions import db
from app.services.context_builder import build_contract_context
from seed import seed_company, seed_options


@pytest.fixture
def app_ctx():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_options()
        seed_company()
        db.session.commit()
        yield


def _base_form_data(**overrides):
    data = {
        "tipo_servico": "assessoria_contabil",
        "inicio_vigencia": "2026-07-01",
        "forma_pagamento": "boleto",
        "dia_vencimento": "25",
        "mes_vencimento": "dia_fixo",
        "reajuste": "sm_ipca_igpm",
        "decima_terceira_parcela": "sim",
        "rescisao": "60_dias",
        "suspensao": "inadimplencia_2",
        "foro": "recife_pe",
        "detalhamento_servico": "escopo_padrao",
        "contratantes": [
            {
                "cnpj": "42957943000157",
                "enquadramento_tributario": "simples",
                "razao_social": "Empresa Teste Ltda",
                "valor_mensal": "10000",
                "nome": "João Silva",
                "cpf": "02175111989",
            }
        ],
        "empresa_contratada_id": 1,
        "cnpj_contratada": "24863877000174",
        "endereco_contratado": "Rua Teste, 99",
        "nome_contratado": "André Abdom Ximenes Cavalcanti",
        "cpf_contratado": "05359403438",
        "crc_contratado": "PE-030717/O",
        "local": "Recife/PE",
        "data_contrato": "2026-06-15",
    }
    data.update(overrides)
    return data


def test_clausula_4_1_vencimento_dia_fixo(app_ctx):
    context = build_contract_context(_base_form_data())

    assert "vencimento dia 25 de cada mês" in context["texto_clausula_4_1"]
    assert "via boleto bancário" in context["texto_clausula_4_1"]
    assert "conforme via boleto" not in context["texto_clausula_4_1"]
    assert context["texto_forma_pagamento"] == "25 de cada mês"


def test_clausula_4_1_vencimento_mes_corrente(app_ctx):
    context = build_contract_context(_base_form_data(mes_vencimento="mes_corrente"))

    assert "vencimento dia 25 do mês corrente" in context["texto_clausula_4_1"]
    assert context["texto_forma_pagamento"] == "25 do mês corrente"


def test_clausula_4_1_vencimento_mes_subsequente(app_ctx):
    context = build_contract_context(_base_form_data(mes_vencimento="mes_subsequente"))

    assert "vencimento dia 25 do mês subsequente" in context["texto_clausula_4_1"]
    assert context["texto_forma_pagamento"] == "25 do mês subsequente"


def test_clausula_4_1_dia_vencimento_alterado(app_ctx):
    context = build_contract_context(_base_form_data(dia_vencimento="10"))

    assert "vencimento dia 10 de cada mês" in context["texto_clausula_4_1"]
    assert context["texto_forma_pagamento"] == "10 de cada mês"


def test_clausula_6_9_suspensao_duas_parcelas(app_ctx):
    context = build_contract_context(_base_form_data(suspensao="inadimplencia_2"))

    assert "6.9  A inadimplência de 2 ou mais parcelas" in context["texto_suspensao"]
    assert context["label_suspensao"] == "Inadimplência 2 ou + Parcelas"


def test_clausula_6_9_suspensao_uma_parcela(app_ctx):
    context = build_contract_context(_base_form_data(suspensao="inadimplencia_1"))

    assert "6.9  A inadimplência de 1 (uma) parcela" in context["texto_suspensao"]
    assert context["label_suspensao"] == "Inadimplência 1 parcela"


def test_clausula_6_9_suspensao_90_dias(app_ctx):
    context = build_contract_context(_base_form_data(suspensao="inadimplencia_90d"))

    assert "6.9  A inadimplência superior a 90 (noventa) dias" in context["texto_suspensao"]
    assert context["label_suspensao"] == "Inadimplência 90 dias"
