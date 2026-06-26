"""Adapta o modelo Word original inserindo placeholders docxtpl via substituição textual."""

import re
import shutil
import zipfile
from pathlib import Path

SOURCE = Path(
    r"g:\Drives compartilhados\99. Interno\7.1 Comercial\7.1.2 Contratos\Valore - Contratos\VCA - Contrato Assessoria Contábil - 2026.docx"
)
TARGET = Path(__file__).resolve().parent.parent / "app" / "templates_docx" / "contrato_modelo.docx"

MODEL_ROW = (
    "<w:tr>"
    "<w:tc><w:tcPr><w:tcW w:w=\"1707\" w:type=\"dxa\"/></w:tcPr>"
    "<w:p><w:r><w:t>{{ cnpj }}</w:t></w:r></w:p></w:tc>"
    "<w:tc><w:tcPr><w:tcW w:w=\"1707\" w:type=\"dxa\"/></w:tcPr>"
    "<w:p><w:r><w:t>{{ enquadramento }}</w:t></w:r></w:p></w:tc>"
    "<w:tc><w:tcPr><w:tcW w:w=\"1707\" w:type=\"dxa\"/></w:tcPr>"
    "<w:p><w:r><w:t>{{ razao_social }}</w:t></w:r></w:p></w:tc>"
    "<w:tc><w:tcPr><w:tcW w:w=\"1707\" w:type=\"dxa\"/></w:tcPr>"
    "<w:p><w:r><w:t>{{ valor_mensal_formatado }}</w:t></w:r></w:p></w:tc>"
    "</w:tr>"
)

CONTRATANTE_CNPJS = [
    "42.957.943/0001-57",
    "21.669.413/0001-33",
    "17.299.260/0001-02",
    "42.409.031/0001-40",
]


def replace_paragraph_text(xml, old_text, new_text):
    pattern = re.compile(
        r"(<w:p\b[^>]*>(?:(?!</w:p>).)*?<w:t[^>]*>)"
        + re.escape(old_text)
        + r"(</w:t>)",
        re.DOTALL,
    )
    if not pattern.search(xml):
        return xml, False
    return pattern.sub(r"\1" + new_text + r"\2", xml, count=1), True


def replace_table_row_containing(xml, needle, replacement):
    pattern = re.compile(
        r"<w:tr\b[^>]*>(?:(?!</w:tr>).)*?"
        + re.escape(needle)
        + r".*?</w:tr>",
        re.DOTALL,
    )
    if not pattern.search(xml):
        return xml, False
    if replacement:
        return pattern.sub(replacement, xml, count=1), True
    return pattern.sub("", xml, count=1), True


def build_template():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Modelo original não encontrado: {SOURCE}")

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, TARGET)

    with zipfile.ZipFile(TARGET, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    xml = files["word/document.xml"].decode("utf-8")

    replacements = [
        ("Assessoria Contábil", "{{ tipo_servico }}"),
        ("Valore Contadores Associados LTDA", "{{ empresa_contratada }}"),
        (
            "01/07/2026 e 12 meses, com renovação automática",
            "{{ inicio_vigencia_formatada }} e {{ texto_vigencia }}",
        ),
        ("25 de cada mês", "{{ texto_forma_pagamento }}"),
        ("SM ou IPCA / IGPM", "{{ texto_reajuste }}"),
        ("Sim", "{{ label_decima_terceira_parcela }}"),
        ("60 dias", "{{ label_rescisao }}"),
        ("Inadimplência 2 ou + Parcelas", "{{ label_suspensao }}"),
        ("Recife/PE", "{{ texto_foro }}"),
        ("Lucro Presumido e Lucro Real.", "{{ texto_regime_tributario }}."),
        (
            "3.1  Este Contrato entra em vigor em 01/07/2026 e tem duração de 12 (doze) meses, renovando-se automaticamente por períodos iguais. Qualquer parte pode rescindi-lo mediante aviso prévio de 60 (sessenta) dias por e-mail para info@valore.com.br. Todos os pagamentos vencidos até a rescisão efetiva permanecem devidos.",
            "{{ texto_vigencia_clausula }}",
        ),
        (
            "4.1  Os honorários mensais são de R$ 22.694,00, com vencimento no dia 25 de cada mês, via boleto bancário.",
            "{{ texto_clausula_4_1 }}",
        ),
        (
            "4.2  Os honorários serão reajustados anualmente pela atualização do salário-mínimo ou, em sua ausência, IPCA ou IGP-M.",
            "{{ texto_clausula_4_2 }}",
        ),
        (
            "4.6  «M_Adicional_Parcela» (encerramento das demonstrações contábeis anuais, Declaração de Rendimentos da Pessoa Jurídica, Declaração de Movimento Fiscal Estadual (inventário anual), transmissão da Escrituração Contábil Digital (ECD), transmissão da Escrituração Contábil Fiscal (ECF) e atendimento à Declaração Anual de Incentivos Fiscais administrados pela SUDENE (DAIF).",
            "{% if exibir_clausula_decima_terceira %}{{ texto_decima_terceira_parcela }}{% endif %}",
        ),
        (
            "6.9  A inadimplência de 2 ou mais parcelas autoriza a CONTRATADA a suspender os serviços até quitação integral.",
            "{{ texto_suspensao }}",
        ),
        (
            "8.1  Fica eleito o foro da Comarca de «Foro» para dirimir quaisquer litígios decorrentes deste Contrato.",
            "{{ texto_clausula_8_1 }}",
        ),
        ("Recife/PE, 15/06/2026", "{{ data_extenso }}"),
    ]

    for old, new in replacements:
        xml, _ = replace_paragraph_text(xml, old, new)

    intro_old = (
        "Doravante denominado CONTRATANTE, representado por Andreia de Oliveira Belaus, CPF nº 021.751.119-89, "
        "Hugo Altevir Costa Lima, CPF nº 382.321.119-68, Bruna Costa Lima, CPF nº 104.932.889-29, e o contador "
        "André Abdom Ximenes Cavalcanti, com escritório Valore Contadores Associados LTDA, CNPJ 24.863.877/0001-74, "
        "Rua Irmã Maria David, 99, CRC nº PE-030717/O, doravante denominado CONTRATADA."
    )
    xml, _ = replace_paragraph_text(xml, intro_old, "{{ texto_partes }}")

    detalhamento_old = "2.2  A CONTRATADA será responsável pelos seguintes serviços mensais:"
    xml, _ = replace_paragraph_text(xml, detalhamento_old, "{{ texto_detalhamento_servico }}")

    xml, ok = replace_table_row_containing(xml, CONTRATANTE_CNPJS[0], MODEL_ROW)
    if not ok:
        raise RuntimeError("Linha modelo de contratante não encontrada.")

    for cnpj in CONTRATANTE_CNPJS[1:]:
        xml, _ = replace_table_row_containing(xml, cnpj, "")

    files["word/document.xml"] = xml.encode("utf-8")

    temp = TARGET.with_suffix(".tmp.docx")
    with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, content in files.items():
            zout.writestr(name, content)
    temp.replace(TARGET)
    print(f"Template gerado: {TARGET}")


if __name__ == "__main__":
    build_template()
