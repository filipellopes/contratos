from datetime import datetime, timezone

from app.extensions import db


class ContractedCompany(db.Model):
    __tablename__ = "contracted_companies"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(300), nullable=False)
    cnpj = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(500))
    responsible_name = db.Column(db.String(200))
    responsible_cpf = db.Column(db.String(20))
    crc = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
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

    def to_dict(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            "cnpj": self.cnpj,
            "address": self.address or "",
            "responsible_name": self.responsible_name or "",
            "responsible_cpf": self.responsible_cpf or "",
            "crc": self.crc or "",
        }

    def __repr__(self):
        return f"<ContractedCompany {self.company_name}>"
