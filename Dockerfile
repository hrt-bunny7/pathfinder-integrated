FROM python:3.11-slim

# Tesseract is only needed for scanned/image resumes. Remove this line if you only support text PDFs/DOCX.
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Train Member 2's careers model at build time so it matches the installed scikit-learn version
RUN python -c "from careers.train_model import train_model; train_model()"

ENV PORT=8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
