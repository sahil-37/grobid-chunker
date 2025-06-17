# ---- 1. base image ---------------------------------------------------
FROM python:3.10-slim

# ---- 2. install OS libs needed by PyMuPDF & friends ------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev \
    libopenjp2-7-dev \
    build-essential \
    gcc \
    wget \
    ca-certificates \
&& rm -rf /var/lib/apt/lists/*

# ---- 3. copy & install python deps -----------------------------------
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- 4. copy application code ---------------------------------------
COPY ./app ./app

# ---- 5. runtime command ---------------------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
