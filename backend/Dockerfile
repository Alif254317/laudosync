FROM python:3.11-slim

# Instala dependências do sistema (Tesseract e Poppler para OCR/PDF)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Expõe a porta
EXPOSE 8000

# Comando para rodar
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
