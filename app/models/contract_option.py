import json
from datetime import datetime, timezone

from app.extensions import db

FIELD_NAMES = {
    "tipo_servico": "Tipo de serviço",
    "forma_pagamento": "Forma de pagamento",
    "mes_vencimento": "Mês do vencimento",
    "reajuste": "Reajuste",
    "decima_terceira_parcela": "13ª parcela",
    "rescisao": "Rescisão",
    "suspensao": "Suspensão",
    "enquadramento_tributario": "Enquadramento tributário",
    "detalhamento_servico": "Detalhamento do serviço",
    "foro": "Foro",
}

DROPDOWN_FIELDS = list(FIELD_NAMES.keys())


class ContractOption(db.Model):
    __tablename__ = "contract_options"

    id = db.Column(db.Integer, primary_key=True)
    field_name = db.Column(db.String(100), nullable=False, index=True)
    option_label = db.Column(db.String(300), nullable=False)
    option_value = db.Column(db.String(300), nullable=False)
    full_text = db.Column(db.Text)
    extra_data_json = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    @property
    def extra_data(self):
        if not self.extra_data_json:
            return {}
        try:
            return json.loads(self.extra_data_json)
        except json.JSONDecodeError:
            return {}

    @extra_data.setter
    def extra_data(self, value):
        self.extra_data_json = json.dumps(value or {}, ensure_ascii=False)

    @property
    def field_label(self):
        return FIELD_NAMES.get(self.field_name, self.field_name)

    def __repr__(self):
        return f"<ContractOption {self.field_name}:{self.option_value}>"
