FROM python:3.14.2-trixie

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml uv.lock* .

RUN uv sync --frozen --no-cache

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 7000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7000", "--reload"]
