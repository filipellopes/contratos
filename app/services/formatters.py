import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

MESES = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]


def only_digits(value):
    if value is None:
        return ""
    return re.sub(r"\D", "", str(value))


def format_cnpj(value):
    digits = only_digits(value)
    if len(digits) != 14:
        return value or ""
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


def format_cpf(value):
    digits = only_digits(value)
    if len(digits) != 11:
        return value or ""
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def parse_currency(value):
    if value is None or value == "":
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    cleaned = str(value).strip()
    cleaned = cleaned.replace("R$", "").replace(" ", "")
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def format_currency(value):
    if value is None:
        return ""
    amount = Decimal(str(value)).quantize(Decimal("0.01"))
    formatted = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            continue
    return None


def format_date(value):
    parsed = parse_date(value)
    if not parsed:
        return ""
    return parsed.strftime("%d/%m/%Y")


def format_date_extenso(value, local=None):
    parsed = parse_date(value)
    if not parsed:
        return ""
    texto = f"{parsed.day} de {MESES[parsed.month - 1]} de {parsed.year}"
    if local:
        return f"{local}, {texto}."
    return f"{texto}."


def slugify(value, max_length=50):
    if not value:
        return "contrato"
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_text.lower()).strip("_")
    return (slug or "contrato")[:max_length]


def join_enquadramentos(enquadramentos):
    unique = []
    seen = set()
    for item in enquadramentos:
        label = (item or "").strip()
        key = label.lower()
        if label and key not in seen:
            seen.add(key)
            unique.append(label)
    if not unique:
        return ""
    if len(unique) == 1:
        return unique[0]
    if len(unique) == 2:
        return f"{unique[0]} e {unique[1]}"
    return ", ".join(unique[:-1]) + f" e {unique[-1]}"
