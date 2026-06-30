"""Popula o banco com opções e empresa contratada de exemplo."""

from app import create_app
from app.extensions import db
from app.models.contract_option import ContractOption
from app.models.contracted_company import ContractedCompany

DETALHAMENTO_SERVICO = """2.2  A CONTRATADA será responsável pelos seguintes serviços mensais:

a) Assessoria Contábil:
Classificação da contabilidade de acordo com normas e princípios contábeis vigentes; emissão dos balancetes em periodicidade trimestral; elaboração de balanço anual e demais demonstrações contábeis obrigatórias ("Serviços Contábeis").

b) Assessoria Fiscal:
Orientação e controle da aplicação dos dispositivos legais vigentes, sejam federais, estaduais ou municipais; escrituração dos registros fiscais de todos os livros obrigatórios perante o governo federal, estadual e municipal; cálculo e emissão das guias de impostos, pró labore, transmissão das obrigações acessórias como, por exemplo, DeSTDA, DEFIS e demais obrigatórias por lei para o enquadramento do Simples Nacional; DCTF, EFD Contribuições, EFD ICMS/IPI, ECF, ECD e demais transmissões para o enquadramento no Lucro Presumido, Lucro Real ou Outras; transmissão e homologação dos livros contábeis e fiscais na Junta Comercial; e atendimento das demais exigências previstas na legislação brasileira ("Serviços Fiscais").

c) Assessoria Trabalhista:
Orientação e controle da aplicação dos preceitos da Consolidação das Leis do Trabalho, bem como aqueles atinentes à Previdência Social, PIS, FGTS e outros aplicáveis às relações de emprego mantidas pela CONTRATANTE; elaboração de contratos de experiência de empregados; orientação da comunicação ao sindicato de admissão e demissão de empregados; processamento de folha de pagamento e recibo de pagamento; cálculo e recolhimento de FGTS e INSS; elaboração de documentos para homologação de rescisões trabalhistas; elaboração de recibo de férias; emissão de Guia de Contribuição Sindical de Empregado; emissão de comprovante de rendimento de empregado e empregador ("Serviços Trabalhistas")."""


def seed_options():
    options = [
        ("tipo_servico", "Assessoria Contábil", "assessoria_contabil", "Assessoria Contábil", 1),
        ("forma_pagamento", "Boleto bancário", "boleto", "via boleto bancário", 1),
        ("forma_pagamento", "PIX", "pix", "via PIX", 2),
        ("mes_vencimento", "Dia fixo do mês", "dia_fixo", "de cada mês", 1),
        ("mes_vencimento", "Mês corrente", "mes_corrente", "do mês corrente", 2),
        ("mes_vencimento", "Mês subsequente", "mes_subsequente", "do mês subsequente", 3),
        ("reajuste", "SM ou IPCA / IGPM", "sm_ipca_igpm", "4.2  Os honorários serão reajustados anualmente pela atualização do salário-mínimo ou, em sua ausência, IPCA ou IGP-M.", 1),
        ("decima_terceira_parcela", "Sim", "sim", "4.6  Adicionalmente, será paga uma parcela extra referente ao encerramento das demonstrações contábeis anuais, DRJ, DMF, ECD, ECF e DAIF.", 1, {"exibir_clausula": True}),
        ("decima_terceira_parcela", "Não", "nao", "", 2, {"exibir_clausula": False}),
        ("rescisao", "60 dias", "60_dias", "Qualquer parte pode rescindi-lo mediante aviso prévio de 60 (sessenta) dias por e-mail para info@valore.com.br.", 1),
        ("rescisao", "90 dias", "90_dias", "Qualquer parte pode rescindi-lo mediante aviso prévio de 90 (noventa) dias por e-mail para info@valore.com.br.", 2),
        ("suspensao", "Inadimplência 1 parcela", "inadimplencia_1", "6.9  A inadimplência de 1 (uma) parcela autoriza a CONTRATADA a suspender os serviços até quitação integral.", 1),
        ("suspensao", "Inadimplência 2 ou + Parcelas", "inadimplencia_2", "6.9  A inadimplência de 2 ou mais parcelas autoriza a CONTRATADA a suspender os serviços até quitação integral.", 2),
        ("suspensao", "Inadimplência 90 dias", "inadimplencia_90d", "6.9  A inadimplência superior a 90 (noventa) dias autoriza a CONTRATADA a suspender os serviços até quitação integral.", 3),
        ("enquadramento_tributario", "Simples Nacional", "simples", "Simples Nacional", 1),
        ("enquadramento_tributario", "Lucro Presumido", "lucro_presumido", "Lucro Presumido", 2),
        ("enquadramento_tributario", "Lucro Real", "lucro_real", "Lucro Real", 3),
        ("detalhamento_servico", "Escopo padrão VCA", "escopo_padrao", DETALHAMENTO_SERVICO, 1),
        ("foro", "Recife/PE", "recife_pe", "Recife/PE", 1),
    ]

    for item in options:
        extra = item[5] if len(item) > 5 else {}
        field_name, label, value, full_text, sort_order = item[:5]
        existing = ContractOption.query.filter_by(field_name=field_name, option_value=value).first()
        if existing:
            continue
        opt = ContractOption(
            field_name=field_name,
            option_label=label,
            option_value=value,
            full_text=full_text,
            sort_order=sort_order,
            is_active=True,
        )
        opt.extra_data = extra
        db.session.add(opt)


def seed_company():
    if ContractedCompany.query.filter_by(cnpj="24863877000174").first():
        return
    company = ContractedCompany(
        company_name="Valore Contadores Associados LTDA",
        cnpj="24863877000174",
        address="Rua Irmã Maria David, 99",
        responsible_name="André Abdom Ximenes Cavalcanti",
        responsible_cpf="05359403438",
        crc="PE-030717/O",
        is_active=True,
    )
    db.session.add(company)


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_options()
        seed_company()
        db.session.commit()
        print("Seed concluído.")


if __name__ == "__main__":
    main()
