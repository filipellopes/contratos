from datetime import datetime, timezone

from app.extensions import db


class ContractGeneration(db.Model):
    __tablename__ = "contract_generations"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    generated_by_name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)  # reservado para login futuro

    contratante_razao_social = db.Column(db.String(300), nullable=False)
    contratante_cnpj = db.Column(db.String(20), nullable=False)
    tipo_servico = db.Column(db.String(200), nullable=False)
    valor_mensal = db.Column(db.Numeric(12, 2), nullable=False)
    empresa_contratada = db.Column(db.String(300), nullable=False)

    local = db.Column(db.String(200))
    data_contrato = db.Column(db.Date)

    docx_path = db.Column(db.String(500))
    pdf_path = db.Column(db.String(500))
    status = db.Column(db.String(50), nullable=False, default="rascunho")
    error_message = db.Column(db.Text)
    form_data_json = db.Column(db.Text, nullable=False)

    logs = db.relationship(
        "GenerationLog",
        back_populates="contract_generation",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    STATUS_LABELS = {
        "rascunho": "Rascunho",
        "gerado_com_sucesso": "Gerado com sucesso",
        "erro_ao_gerar_docx": "Erro ao gerar DOCX",
        "erro_ao_converter_pdf": "Erro ao converter PDF",
        "erro_geral": "Erro geral",
    }

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)

    def __repr__(self):
        return f"<ContractGeneration {self.id}>"
