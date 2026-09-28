# syntax=docker/dockerfile:1

# ---------- Stage 1: builder ----------
# Installs dependencies into a virtual environment. Anything needed only to
# BUILD (pip cache, build tools) stays in this stage and is thrown away.
FROM python:3.12-slim AS builder

WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only requirements first so Docker can cache this layer: dependencies
# are re-installed only when requirements.txt changes, not on every code edit.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ---------- Stage 2: runtime ----------
# The final image: a clean Python base + the ready-made venv + your code.
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY app ./app

EXPOSE 8000

# 0.0.0.0 = listen on all interfaces inside the container, so the published
# port (-p 8000:8000) can reach the app from outside.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
