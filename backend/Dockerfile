FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git \
        libffi-dev \
        libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

FROM base AS dependencies

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

FROM base AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    HOST=0.0.0.0 \
    PORT=8000

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=dependencies /app/.venv /app/.venv
COPY app ./app
COPY scripts ./scripts
COPY pyproject.toml uv.lock ./
COPY alembic.ini ./
COPY migrations ./migrations

RUN groupadd --system vocalis \
    && useradd --system --gid vocalis --home-dir /app --shell /usr/sbin/nologin vocalis \
    && chown -R vocalis:vocalis /app

USER vocalis

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/api/v1/health || exit 1

CMD ["litestar", "--app", "app.main:app", "run", "--host", "0.0.0.0", "--port", "8000"]
