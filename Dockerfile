# Ethos Kernel — multi-stage image: slim runtime + venv from builder (reproducible dev/edge).
# Optional Ollama: `docker compose --profile llm up` (see docker-compose.yml).

FROM python:3.12-slim-bookworm AS builder
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt /app/requirements.txt
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

FROM python:3.12-slim-bookworm AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN useradd --create-home --uid 1000 --shell /bin/bash appuser

COPY --chown=appuser:appuser . /app
USER appuser

EXPOSE 8765

# Bind all interfaces for container/LAN use; override via CHAT_HOST / CHAT_PORT.
CMD ["uvicorn", "src.chat_server:app", "--host", "0.0.0.0", "--port", "8765"]
