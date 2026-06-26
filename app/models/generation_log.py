import json
from datetime import datetime, timezone

from app.extensions import db


class GenerationLog(db.Model):
    __tablename__ = "generation_logs"

    id = db.Column(db.Integer, primary_key=True)
    contract_generation_id = db.Column(
        db.Integer,
        db.ForeignKey("contract_generations.id"),
        nullable=False,
        index=True,
    )
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    action = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)
    details_json = db.Column(db.Text)

    contract_generation = db.relationship(
        "ContractGeneration",
        back_populates="logs",
    )

    @property
    def details(self):
        if not self.details_json:
            return {}
        try:
            return json.loads(self.details_json)
        except json.JSONDecodeError:
            return {}

    @details.setter
    def details(self, value):
        self.details_json = json.dumps(value or {}, ensure_ascii=False)

    def __repr__(self):
        return f"<GenerationLog {self.action}>"
