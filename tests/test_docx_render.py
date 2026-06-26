"""Smoke test para renderização do template Word."""

import json
from datetime import date

from app import create_app
from app.services.context_builder import build_contract_context
from app.services.docx_generator import generate_docx


def main():
    app = create_app()
    with app.app_context():
        form_data = {
            "generated_by_name": "Teste Usuario",
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
                    "razao_social": "Onvilla Empreendimentos Hoteleiros e Turismo Ltda",
                    "valor_mensal": "5673.50",
                    "nome": "Andreia de Oliveira Belaus",
                    "cpf": "02175111989",
                }
            ],
            "empresa_contratada_id": 1,
            "cnpj_contratada": "24863877000174",
            "endereco_contratado": "Rua Irmã Maria David, 99",
            "nome_contratado": "André Abdom Ximenes Cavalcanti",
            "cpf_contratado": "05359403438",
            "crc_contratado": "PE-030717/O",
            "local": "Recife/PE",
            "data_contrato": "2026-06-15",
        }
        context = build_contract_context(form_data)
        path = generate_docx(context, "Onvilla")
        print("DOCX gerado:", path)
        content = path.read_bytes()
        assert len(content) > 10000
        print("OK")


if __name__ == "__main__":
    main()
