# syntax=docker/dockerfile:1
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.12.9
ARG PYTHON_IMAGE=python:3.14-slim
ARG CUDA_IMAGE=nvidia/cuda:12.8.1-cudnn-runtime-ubuntu24.04
FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS python-runtime
COPY --from=uv /uv /bin/uv
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates tzdata libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 storage && useradd --uid 10001 --gid 10001 --create-home storage
ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/cache/huggingface
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY alembic.ini ./

FROM python-runtime AS cpu
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-editable --extra transcription
USER 10001:10001
ENTRYPOINT ["python", "src/cli.py"]
CMD ["worker"]

# CUDA 12 + cuDNN 9 runtime for the RTX 2060. No host CUDA installation is needed.
FROM ${CUDA_IMAGE} AS worker
COPY --from=uv /uv /bin/uv
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates tzdata libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 storage && useradd --uid 10001 --gid 10001 --create-home storage
ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_LINK_MODE=copy UV_PYTHON_INSTALL_DIR=/opt/python \
    UV_PYTHON_PREFERENCE=only-managed UV_PYTHON=3.14 \
    PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/cache/huggingface NVIDIA_DRIVER_CAPABILITIES=compute,utility
RUN --mount=type=cache,target=/root/.cache/uv uv python install 3.14
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY alembic.ini ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-editable --extra transcription
USER 10001:10001
ENTRYPOINT ["python", "src/cli.py"]
CMD ["worker"]

FROM python-runtime AS app
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-editable
USER 10001:10001
ENTRYPOINT ["python", "src/cli.py"]
CMD ["api"]
