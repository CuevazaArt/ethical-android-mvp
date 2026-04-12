# Ethos Kernel chat runtime (FastAPI + WebSocket). Build from repository root.
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8765

# Bind all interfaces for container/LAN use; override via CHAT_HOST / CHAT_PORT.
CMD ["uvicorn", "src.chat_server:app", "--host", "0.0.0.0", "--port", "8765"]
