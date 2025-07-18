FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev \
    libopenjp2-7-dev \
    build-essential \
    gcc \
    wget \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
