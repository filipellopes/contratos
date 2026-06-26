import shutil
import zipfile

from scripts import build_template as bt

shutil.copy2(bt.SOURCE, "tests/step.docx")
with zipfile.ZipFile("tests/step.docx", "r") as z:
    files = {n: z.read(n) for n in z.namelist()}
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
]

for old, new in replacements:
    xml, ok = bt.replace_paragraph_text(xml, old, new)
    print(f"{old[:25]:25} -> {ok}")

print("tipo in xml:", "{{ tipo_servico }}" in xml)
print("len xml:", len(xml))
