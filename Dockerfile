# Topic 1 — Customer Value & Promotion Targeting
# One image for tests, pipeline, dashboard and notebooks (see docker-compose.yml).
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencies first (layer cache)
COPY requirements.txt requirements-dev.txt ./
ARG INSTALL_DEV=false
RUN pip install -r requirements.txt \
 && if [ "$INSTALL_DEV" = "true" ]; then pip install -r requirements-dev.txt; fi

# Project (src/tests are also bind-mounted in compose for live editing)
COPY pyproject.toml project_config.example.yaml project_config.yaml ./
COPY src ./src
COPY tests ./tests
COPY dashboard ./dashboard
RUN pip install -e . \
 && useradd --create-home --uid 1000 app \
 && mkdir -p data/raw data/interim data/processed outputs/tables outputs/figures outputs/models outputs/reports \
 && chown -R app:app /app
USER app

CMD ["python", "-m", "pytest", "-q"]
