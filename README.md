# Gerador de Contratos Valore

Sistema web interno para geração de contratos de assessoria contábil a partir de modelo Word, com prévia HTML, exportação DOCX/PDF, histórico e auditoria.

## Requisitos

- Python 3.11+
- **LibreOffice** — necessário apenas para PDF; no desenvolvimento local (Windows) pode ficar desligado

## Desenvolvimento local (Windows) — sem instalar LibreOffice

No `.env`:

```env
PDF_CONVERSION=auto
```

Com `auto`, o sistema **sempre gera o Word (.docx)**. Se o LibreOffice não existir na máquina, o PDF é omitido com aviso — não é erro. Ideal para desenvolver no Windows e publicar no VPS depois.

## Instalação

```bash
cd contratos
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

Copie o arquivo de exemplo:

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # Linux
```

Para desenvolvimento local, `PDF_CONVERSION=auto` (padrão) já basta — **não precisa instalar LibreOffice no Windows**.

## Deploy no VPS Linux (recomendado)

### Opção A — Docker (mais simples)

O `Dockerfile` já inclui LibreOffice. No servidor:

```bash
git clone <seu-repo> contratos && cd contratos
docker compose up -d --build
```

Acesse na porta 5000 (coloque Nginx/Caddy na frente em produção).

### Opção B — Instalação direta no Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y python3-venv libreoffice-writer-nogui

cd contratos
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed.py

# .env em produção:
# PDF_CONVERSION=auto
# LIBREOFFICE_PATH=/usr/bin/soffice

python run.py
```

Use **systemd** ou **gunicorn** para manter o processo rodando (ex.: `gunicorn -w 2 -b 0.0.0.0:5000 run:app`).

### Opção C — Railway (URL pública, ideal para celular)

Deploy em nuvem com domínio HTTPS automático. Guia completo: **[RAILWAY.md](RAILWAY.md)**.

Resumo:

1. [railway.com/new](https://railway.com/new) → conecte o repo GitHub
2. Adicione **PostgreSQL** e referencie `DATABASE_URL`
3. Defina `SECRET_KEY` e `FLASK_DEBUG=0`
4. **Generate Domain** nas configurações de rede

Acesse de qualquer dispositivo: `https://sua-url.up.railway.app/contratos`

> **Trial do Railway expirou?** Use o deploy gratuito no Render — guia: **[RENDER.md](RENDER.md)**.

### Por que LibreOffice no servidor?

Alternativas puramente Python (WeasyPrint, docx2pdf) **não preservam** tabelas, margens e estilos do Word. No Linux, o LibreOffice em modo headless é o padrão da indústria para conversão fiel — roda **no VPS**, não na sua máquina de desenvolvimento.

## Banco de dados e seed

```bash
python seed.py
```

O seed cria as tabelas SQLite e popula opções de exemplo + empresa Valore.

## Modelo Word

O template base fica em `app/templates_docx/contrato_modelo.docx`.

Para regenerar a partir do Word original da Valore:

```bash
python scripts/build_template.py
```

**Múltiplas contratantes:** o template usa uma linha modelo com `{{ cnpj }}`, `{{ enquadramento }}`, etc. Após a renderização, o sistema duplica a linha via `python-docx` para cada contratante adicional (workaround necessário porque tags `{%tr for %}` do docxtpl conflitam com `%}` no XML).

**Importante ao editar placeholders no Word:**

- Substitua o texto selecionado de uma só vez (ex.: `{{ razao_social }}`).
- Não digite `{{` e `}}` em edições separadas — isso quebra o XML do Word.
- Para linhas repetíveis de tabela use `{%tr for c in contratantes %}...{%tr endfor %}`.
- Cláusulas condicionais: envolva o parágrafo inteiro em `{% if exibir_clausula_decima_terceira %}...{% endif %}`.

## Executar

```bash
python run.py
```

Acesse: http://localhost:5000

## Fluxo de uso

1. Cadastre **Opções** (`/opcoes`) para alimentar as listas suspensas.
2. Cadastre **Empresas contratadas** (`/empresas-contratadas`) — a Valore vem no seed.
3. Clique em **Novo contrato**, preencha os 4 blocos (suporta múltiplas contratantes).
4. Visualize a **prévia** e confirme **Gerar contrato**.
5. Baixe Word/PDF na listagem ou na página de detalhes.

## Rotas principais

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/contratos` | Listagem |
| GET | `/contratos/novo` | Formulário |
| POST | `/contratos/preview` | Prévia |
| POST | `/contratos/gerar` | Gera DOCX/PDF |
| GET | `/contratos/<id>` | Detalhes + logs |
| GET | `/api/empresas-contratadas/<id>` | Auto-preenchimento JSON |

## Opções configuráveis

Campos com dropdown administrável:

- tipo_servico, forma_pagamento, mes_vencimento, reajuste
- decima_terceira_parcela, rescisao, suspensao, foro
- enquadramento_tributario, detalhamento_servico

Para a **13ª parcela**, use `extra_data_json`:

```json
{"exibir_clausula": true}
```

## PostgreSQL (futuro)

```bash
set DATABASE_URL=postgresql://usuario:senha@localhost/contratos
python seed.py
```

## Estrutura

```
app/
  models/          # SQLAlchemy
  routes/          # Blueprints Flask
  services/        # Validação, contexto, DOCX, PDF
  templates/       # HTML Bootstrap
  templates_docx/  # Modelo Word
  generated_contracts/
```

## Status de geração

- `rascunho`
- `gerado_com_sucesso`
- `erro_ao_gerar_docx`
- `erro_ao_converter_pdf`
- `erro_geral`

Logs detalhados ficam em `generation_logs` e na página de detalhes do contrato.
