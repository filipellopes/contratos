"""Adapta o modelo Word original: remove dados de exemplo e insere placeholders."""

import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCE = Path(
    r"g:\Drives compartilhados\99. Interno\7.1 Comercial\7.1.2 Contratos\Valore - Contratos\VCA - Contrato Assessoria Contábil - 2026.docx"
)
# Override local para regenerar a partir de uma cópia recebida fora do drive compartilhado.
_LOCAL_OVERRIDE = Path(__file__).resolve().parent.parent / "VCA - Contrato Assessoria Contábil - 2026.docx"
if _LOCAL_OVERRIDE.exists():
    SOURCE = _LOCAL_OVERRIDE
TARGET = Path(__file__).resolve().parent.parent / "app" / "templates_docx" / "contrato_modelo.docx"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

CONTRATANTE_CNPJS = [
    "42.957.943/0001-57",
    "21.669.413/0001-33",
    "17.299.260/0001-02",
    "42.409.031/0001-40",
]

MODEL_ROW_XML = """
<w:tr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:tc><w:tcPr><w:tcW w:w="1707" w:type="dxa"/></w:tcPr><w:p><w:r><w:t>{{ cnpj }}</w:t></w:r></w:p></w:tc>
  <w:tc><w:tcPr><w:tcW w:w="1707" w:type="dxa"/></w:tcPr><w:p><w:r><w:t>{{ enquadramento }}</w:t></w:r></w:p></w:tc>
  <w:tc><w:tcPr><w:tcW w:w="1707" w:type="dxa"/></w:tcPr><w:p><w:r><w:t>{{ razao_social }}</w:t></w:r></w:p></w:tc>
  <w:tc><w:tcPr><w:tcW w:w="1707" w:type="dxa"/></w:tcPr><w:p><w:r><w:t>{{ valor_mensal_formatado }}</w:t></w:r></w:p></w:tc>
</w:tr>
""".strip()


def set_cell_text(cell, text):
    for para in cell.findall(_tag("p")):
        set_para_text(para, text)
        return
    para = ET.SubElement(cell, _tag("p"))
    set_para_text(para, text)

# (início do parágrafo, texto substituto) — só startswith; ordem: mais específico primeiro
# Usado para parágrafos SEM número de cláusula (ou onde o número fica de fora do trecho substituído).
PARAGRAPH_RULES = [
    ("Doravante denominado CONTRATANTE", "{{ texto_partes }}"),
    ("Recife/PE, 15/06/2026", "{{ data_extenso }}"),
    ("Recife/PE, ", "{{ data_extenso }}"),
    ("Assessoria Contábil", "{{ tipo_servico }}"),
    ("Valore Contadores Associados LTDA", "{{ empresa_contratada }}"),
    ("01/07/2026 e 12 meses", "{{ inicio_vigencia_formatada }} e {{ texto_vigencia }}"),
    ("25 de cada mês", "{{ texto_forma_pagamento }}"),
    ("SM ou IPCA / IGPM", "{{ texto_reajuste }}"),
    ("Inadimplência 2 ou + Parcelas", "{{ label_suspensao }}"),
    ("Lucro Presumido e Lucro Real", "{{ texto_regime_tributario }}"),
    ("CPSA-VCA-2026", "CPSA-2026"),
]

# (início do parágrafo, número da cláusula, corpo substituto) — o número fica em uma run
# separada (negrito + azul, igual ao resto do contrato) e o corpo numa run normal.
NUMBERED_CLAUSE_RULES = [
    ("3.1  Este Contrato entra em vigor", "3.1", "{{ texto_vigencia_clausula }}"),
    (
        "3.3  Qualquer das Partes poderá rescindir este Contrato de imediato",
        "3.3",
        "Qualquer das Partes poderá rescindir este Contrato de imediato, sem aviso prévio e "
        "sem a multa da Cláusula 3.2, em caso de: (i) inadimplência superior a 90 (noventa) dias; "
        "(ii) fraude, falsidade documental ou recusa da CONTRATANTE em regularizar operações em "
        "desacordo com a lei; (iii) descumprimento grave de obrigação contratual não sanado em "
        "15 (quinze) dias após notificação escrita.",
    ),
    ("4.1  Os honorários mensais", "4.1", "{{ texto_clausula_4_1 }}"),
    ("4.2  Os honorários serão reajustados", "4.2", "{{ texto_clausula_4_2 }}"),
    ("6.9  A inadimplência", "6.9", "{{ texto_suspensao }}"),
    ("8.1  Fica eleito o foro", "8.1", "{{ texto_clausula_8_1 }}"),
]

# Cláusula 4.6 é condicional — o {% if %} precisa envolver número + corpo, então é
# tratada à parte (ver apply_paragraph_rules).
CLAUSE_4_6_STARTS = ("4.6  «M_Adicional_Parcela»", "4.6  ")

# Resumo — parágrafo com texto exato
SUMMARY_CELL_RULES = [
    ("Sim", "{{ label_decima_terceira_parcela }}"),
    ("60 dias", "{{ label_rescisao }}"),
    ("Recife/PE", "{{ texto_foro }}"),
]

REQUIRED_PLACEHOLDERS = [
    "{{ texto_partes }}",
    "{{ texto_clausula_4_1 }}",
    "{{ texto_vigencia_clausula }}",
    "{{ data_extenso }}",
    "{{ bloco_assinatura_contratantes }}",
    "{{ cnpj }}",
]

EXAMPLE_MARKERS = [
    "Andreia de Oliveira",
    "Hugo Altevir",
    "Bruna Costa Lima",
    "André Abdom",
    "021.751.119",
    "382.321.119",
    "104.932.889",
    "053.594.034",
    "24.863.877",
    "Onvilla",
    "Ecovilla",
    "Nordeste Empreendimentos",
    "Vila Xalés",
    "22.694,00",
    "5.673,5",
]


def _tag(name):
    return f"{{{W}}}{name}"


def para_text(para):
    return "".join(t.text or "" for t in para.iter(_tag("t")))


def set_para_text(para, text):
    for child in list(para):
        if child.tag == _tag("r"):
            para.remove(child)
    r = ET.Element(_tag("r"))
    t = ET.Element(_tag("t"))
    t.text = text
    if text and (text[0].isspace() or text[-1].isspace() or "{{" in text):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.append(t)
    para.append(r)


def _new_run(text, *, bold=False, color="1A1A1A"):
    r = ET.Element(_tag("r"))
    rpr = ET.SubElement(r, _tag("rPr"))
    font = ET.SubElement(rpr, _tag("rFonts"))
    font.set(f"{{{W}}}asciiTheme", "minorHAnsi")
    font.set(f"{{{W}}}hAnsiTheme", "minorHAnsi")
    if bold:
        ET.SubElement(rpr, _tag("b"))
        ET.SubElement(rpr, _tag("bCs"))
    color_el = ET.SubElement(rpr, _tag("color"))
    color_el.set(f"{{{W}}}val", color)
    t = ET.SubElement(r, _tag("t"))
    t.text = text
    if text and (text[0].isspace() or text[-1].isspace() or "{{" in text or "{%" in text):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r


def set_para_clause(para, numero, body_text):
    """Substitui o parágrafo por duas runs: número da cláusula em negrito/azul
    (mesmo padrão do resto do contrato) + corpo em texto normal."""
    for child in list(para):
        if child.tag == _tag("r"):
            para.remove(child)
    para.append(_new_run(f"{numero}  ", bold=True, color="2E6DA4"))
    para.append(_new_run(body_text, color="1A1A1A"))


def set_para_clause_conditional(para, condition, numero, body_text):
    """Como set_para_clause, mas envolve número + corpo num {% if %}{% endif %}
    para que a cláusula inteira (incluindo o número) suma quando a condição é falsa."""
    for child in list(para):
        if child.tag == _tag("r"):
            para.remove(child)
    open_tag = "{% if " + condition + " %}"
    close_tag = "{% endif %}"
    para.append(_new_run(f"{open_tag}{numero}  ", bold=True, color="2E6DA4"))
    para.append(_new_run(f"{body_text}{close_tag}", color="1A1A1A"))


def table_text(tbl):
    return "".join(t.text or "" for t in tbl.iter(_tag("t")))


def apply_paragraph_rules(root):
    for para in root.iter(_tag("p")):
        text = para_text(para)
        if not text:
            continue
        for exact, replacement in SUMMARY_CELL_RULES:
            if text.strip() == exact:
                set_para_text(para, replacement)
                break
        else:
            if text.startswith(CLAUSE_4_6_STARTS):
                set_para_clause_conditional(
                    para, "exibir_clausula_decima_terceira", "4.6", "{{ texto_decima_terceira_parcela }}"
                )
                continue
            for start, numero, body in NUMBERED_CLAUSE_RULES:
                if text.startswith(start):
                    set_para_clause(para, numero, body)
                    break
            else:
                for start, replacement in PARAGRAPH_RULES:
                    if text.startswith(start):
                        set_para_text(para, replacement)
                        break


def remove_section_22_examples(body):
    """Remove parágrafos de exemplo entre 2.2 e 2.3; 2.2 vira placeholder."""
    removing = False
    for child in list(body):
        if child.tag != _tag("p"):
            continue
        text = para_text(child)
        if text.startswith("2.2  A CONTRATADA"):
            set_para_clause(child, "2.2", "{{ texto_detalhamento_servico }}")
            removing = True
            continue
        if removing:
            if text.startswith("2.3"):
                removing = False
            else:
                body.remove(child)


def fix_contratantes_table(body):
    for child in list(body):
        if child.tag != _tag("tbl"):
            continue
        tbl_text = table_text(child)
        if "CNPJ" not in tbl_text or "Razão Social" not in tbl_text:
            continue
        rows = child.findall(_tag("tr"))
        if len(rows) < 2:
            continue
        data_row = rows[1]
        cells = data_row.findall(_tag("tc"))
        if len(cells) >= 4:
            set_cell_text(cells[0], "{{ cnpj }}")
            set_cell_text(cells[1], "{{ enquadramento }}")
            set_cell_text(cells[2], "{{ razao_social }}")
            set_cell_text(cells[3], "{{ valor_mensal_formatado }}")
        for row in rows[2:]:
            if any(cnpj in table_text(row) for cnpj in CONTRATANTE_CNPJS):
                child.remove(row)
        break


def fix_signature_tables(body):
    sig_tables = []
    for child in list(body):
        if child.tag != _tag("tbl"):
            continue
        tt = table_text(child)
        if "CONTRATANTE" in tt and "CPF" in tt and not ("CNPJ" in tt and "Razão Social" in tt):
            sig_tables.append(child)

    if not sig_tables:
        return

    first = sig_tables[0]
    rows = first.findall(_tag("tr"))
    if rows:
        cells = rows[0].findall(_tag("tc"))
        if len(cells) >= 2:
            set_cell_text(cells[0], "{{ bloco_assinatura_contratantes }}")
            set_cell_text(cells[1], "{{ bloco_assinatura_contratada }}")
        elif len(cells) == 1:
            set_cell_text(cells[0], "{{ bloco_assinatura_contratantes }}\n\n{{ bloco_assinatura_contratada }}")

    for extra in sig_tables[1:]:
        body.remove(extra)


def scrub_remaining_examples(root):
    """Remove parágrafos soltos que ainda contenham dados do exemplo."""
    body = root.find(_tag("body"))
    if body is None:
        return
    for para in list(body.iter(_tag("p"))):
        text = para_text(para)
        if not text:
            continue
        if any(m in text for m in EXAMPLE_MARKERS):
            if "{{" not in text:
                parent = None
                for p in root.iter():
                    if para in list(p):
                        parent = p
                        break
                if parent is not None and para in list(parent):
                    parent.remove(para)


# Fonte usada em todo o corpo do documento original (tema minorHAnsi).
BODY_FONT_ASCII_THEME = "minorHAnsi"


def normalize_body_formatting(body):
    """Garante a mesma fonte em todos os runs do documento (inclusive nos runs
    de placeholder, que não tinham rFonts). Não mexe em negrito, cor ou tamanho —
    só unifica a tipografia."""
    for p in body.iter(_tag("p")):
        for r in p.findall(_tag("r")):
            t = r.find(_tag("t"))
            if t is not None and t.text and any(ord(ch) > 0x2100 for ch in t.text):
                continue  # preserva fonte de emoji/símbolos (ex.: 📋)
            rpr = r.find(_tag("rPr"))
            if rpr is None:
                rpr = ET.Element(_tag("rPr"))
                r.insert(0, rpr)
            font_el = rpr.find(_tag("rFonts"))
            if font_el is None:
                font_el = ET.Element(_tag("rFonts"))
                rpr.insert(0, font_el)
            font_el.set(f"{{{W}}}asciiTheme", BODY_FONT_ASCII_THEME)
            font_el.set(f"{{{W}}}hAnsiTheme", BODY_FONT_ASCII_THEME)
            for attr in ("ascii", "hAnsi", "cs"):
                font_el.attrib.pop(f"{{{W}}}{attr}", None)


def build_template():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Modelo original não encontrado: {SOURCE}")

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, TARGET)

    with zipfile.ZipFile(TARGET, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    root = ET.fromstring(files["word/document.xml"])
    body = root.find(_tag("body"))
    if body is None:
        raise RuntimeError("document.xml sem w:body")

    apply_paragraph_rules(root)
    remove_section_22_examples(body)
    fix_contratantes_table(body)
    fix_signature_tables(body)
    apply_paragraph_rules(root)
    scrub_remaining_examples(root)
    normalize_body_formatting(body)

    ET.register_namespace("w", W)
    files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    temp = TARGET.with_suffix(".tmp.docx")
    with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, content in files.items():
            zout.writestr(name, content)
    temp.replace(TARGET)

    verify_template()
    print(f"Template gerado: {TARGET}")


def verify_template():
    with zipfile.ZipFile(TARGET) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    texts = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)
    full = "".join(texts)
    found = [m for m in EXAMPLE_MARKERS if m in full]
    if found:
        print("AVISO — ainda contém dados de exemplo:", found)
    else:
        print("OK — nenhum dado de exemplo detectado.")
    missing = [p for p in REQUIRED_PLACEHOLDERS if p not in xml]
    if missing:
        print("AVISO — placeholders ausentes:", missing)
    else:
        print("OK — placeholders obrigatórios presentes.")


if __name__ == "__main__":
    build_template()
