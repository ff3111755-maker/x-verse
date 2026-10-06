# Web/API image for Render. User programs NEVER execute in this container.
FROM node:22-bookworm-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm AS web
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=10000 AUTH_MODE=supabase RUNNER_MODE=disabled SQLITE_PATH=/var/data/academy.sqlite
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 app \
    && mkdir -p /var/data && chown app:app /var/data
COPY server.py hosting.py runner_gateway.py ./
COPY data/curriculum.json ./data/curriculum.json
COPY frontend/public/favicon.svg ./frontend/public/favicon.svg
COPY --from=frontend /build/frontend/dist ./frontend/dist
# Render mounts a persistent disk here. The startup step fixes mount ownership,
# then drops to the unprivileged account before running the application.
COPY deploy/start-web.py ./start-web.py
EXPOSE 10000
CMD ["python", "start-web.py"]