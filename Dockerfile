# TraceMap: API + built UI + Chromium in one image.
# NOTE: written on a machine without Docker; build and test once Docker is installed.

# ---- build the React UI
FROM node:24-slim AS ui
WORKDIR /ui
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- runtime: Playwright's official Python image ships Chromium and its OS deps
FROM mcr.microsoft.com/playwright/python:v1.63.0-noble
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    TRACEMAP_DATA_DIR=/data
COPY pyproject.toml README.md ./
COPY tracemap/ tracemap/
COPY testbed/ testbed/
COPY data/lists/supplement/ data/lists/supplement/
COPY data/corpus/ data/corpus/
RUN pip install --no-cache-dir .
COPY --from=ui /ui/dist frontend/dist
# Tracker lists are fetched at build time (their licences forbid bundling them in the repo).
RUN python -m tracemap lists fetch
VOLUME ["/data"]
EXPOSE 8000
# channel=auto falls back to Playwright's Chromium when Google Chrome is not installed.
CMD ["python", "-m", "tracemap", "serve", "--host", "0.0.0.0", "--port", "8000"]
