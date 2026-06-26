FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PDF_CONVERSION=auto \
    LIBREOFFICE_PATH=/usr/bin/soffice

WORKDIR /app

# LibreOffice headless para conversão DOCX → PDF (fidelidade ao layout Word)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libreoffice-writer-nogui \
        fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p instance app/generated_contracts/docx app/generated_contracts/pdf

EXPOSE 5000

CMD ["sh", "-c", "python seed.py && python run.py"]
