# ==============================================================
# BUILD
# ==============================================================
FROM python:3.13-slim AS build

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-editable

COPY app/ ./app/

# ==============================================================
# RUN
# ==============================================================
FROM python:3.13-slim AS run

WORKDIR /app

RUN useradd --no-create-home --shell /bin/false appuser

COPY --from=build /app/.venv /app/.venv
COPY --from=build /app/app /app/app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]