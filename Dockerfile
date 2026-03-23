FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENV PORT=8502
EXPOSE 8502

CMD ["sh", "-c", "streamlit run echomesh_app.py --server.headless true --server.address 0.0.0.0 --server.port ${PORT:-8502}"]
