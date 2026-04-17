FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Instalar dependencias del sistema útiles
RUN apt-get update && apt-get install -y \
    graphviz \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /workspace

# Copiar archivos de requerimientos primero para cache
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
