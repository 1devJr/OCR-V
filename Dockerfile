FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx tesseract-ocr libsm6 libxrender1 libxext6 libxcb-xinerama0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["python", "/app/main.py"]