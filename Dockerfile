# P10c — deterministic FastAPI service container (local smoke testing only).
# Packages mip.service; does not run Streamlit, LLM providers, or measurement engines.

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock README.md ./
COPY src ./src
COPY app ./app

RUN poetry install --only main --no-ansi

EXPOSE 8000

CMD ["uvicorn", "mip.service.app:app", "--host", "0.0.0.0", "--port", "8000"]
