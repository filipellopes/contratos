from pathlib import Path

from flask import Flask, redirect, url_for

from app.config import Config
from app.extensions import db, migrate
from app.services.formatters import (
    format_cnpj as _format_cnpj,
    format_cpf as _format_cpf,
    format_currency as _format_currency,
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    for directory in (
        app.config["GENERATED_DOCX_DIR"],
        app.config["GENERATED_PDF_DIR"],
    ):
        Path(directory).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import (  # noqa: F401
        ContractGeneration,
        ContractOption,
        ContractedCompany,
        GenerationLog,
    )
    from app.routes.companies import companies_bp
    from app.routes.contracts import contracts_bp
    from app.routes.docs import docs_bp
    from app.routes.options import options_bp

    app.register_blueprint(contracts_bp)
    app.register_blueprint(options_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(docs_bp)

    @app.route("/")
    def index():
        return redirect(url_for("contracts.list_contracts"))

    @app.context_processor
    def inject_globals():
        from app.models.contract_option import FIELD_NAMES

        return {"FIELD_NAMES": FIELD_NAMES}

    @app.template_filter("format_cnpj")
    def format_cnpj_filter(value):
        return _format_cnpj(value)

    @app.template_filter("format_cpf")
    def format_cpf_filter(value):
        return _format_cpf(value)

    @app.template_filter("format_currency")
    def format_currency_filter(value):
        return _format_currency(value)

    @app.route("/api/empresas-contratadas/<int:company_id>")
    def api_empresa_contratada(company_id):
        from flask import jsonify

        from app.models.contracted_company import ContractedCompany
        company = ContractedCompany.query.get_or_404(company_id)
        data = company.to_dict()
        data["cnpj_formatted"] = _format_cnpj(company.cnpj)
        data["responsible_cpf_formatted"] = _format_cpf(company.responsible_cpf)
        return jsonify(data)

    return app
