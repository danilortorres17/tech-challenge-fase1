# Imagem base enxuta com Python 3.13
FROM python:3.13-slim

# Evita .pyc e deixa o log sair na hora
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala as dependências primeiro (aproveita o cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Hardening: a aplicação roda como usuário sem privilégios (não-root), e o
# volume /data (banco SQLite) pertence a ele.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data
USER appuser

# Porta da API
EXPOSE 8000

# Sobe a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
