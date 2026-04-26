FROM python:3.11-alpine

LABEL org.opencontainers.image.source="https://github.com/PrivateCapybara/beget-billing-exporter"
LABEL org.opencontainers.image.description="Prometheus billing exporter for Beget API"
LABEL org.opencontainers.image.version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY beget-billing-exporter.py .

EXPOSE 9481

CMD ["python", "beget-billing-exporter.py"]
