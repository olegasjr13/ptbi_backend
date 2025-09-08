FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential libpq-dev gcc netcat-openbsd &&     apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN chmod +x docker/entrypoint.sh docker/start.sh
ENTRYPOINT ["./docker/entrypoint.sh"]
