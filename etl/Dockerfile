# ETL Dockerfile — lightweight one-shot pipeline container
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tableau_etl.py .

RUN mkdir -p /app/exports

CMD ["python", "tableau_etl.py"]
