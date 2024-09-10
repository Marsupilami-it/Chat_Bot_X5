ARG PYTHON_VERSION=3.11.7-slim
ARG POETRY_VERSION=1.8.2

FROM python:${PYTHON_VERSION} AS base

# Create app user and group
RUN groupadd --gid 1000 app \
 && useradd --uid 1000 --gid 1000 --no-create-home --shell /bin/bash app \
 && mkdir /app \
 && chown app:app /app

# This flag is important to output python logs correctly in docker!
ENV PYTHONUNBUFFERED 1
# Flag to optimize container size a bit by removing runtime python cache
ENV PYTHONDONTWRITEBYTECODE 1

# Poetry will create a new virtual environment in project dir.
ENV POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app



FROM base AS build
ARG POETRY_VERSION




# Install Poetry
RUN python -m pip --disable-pip-version-check --no-cache-dir install "poetry==${POETRY_VERSION}" \
 && rm -rf ~/.local ~/.cache

# Copy pyproject.toml and poetry.lock* in case it exist
COPY --chown=app pyproject.toml poetry.lock* ./

# Install dependencies
RUN python -m poetry install --only=main --no-root --no-cache

# Copy sources
COPY --chown=app README.md ./
COPY --chown=app src ./src

# Build the distribution
RUN python -m poetry build --format=wheel --no-cache


FROM base AS runtime

# only for healthcheck
RUN apt-get update && apt-get install -y \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Reuse virtual environemnt just to speed up the process
COPY --from=build /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:${PATH}"

COPY --from=build /app/dist/*.whl ./

RUN python -m pip --disable-pip-version-check --no-cache-dir install ./*.whl \
 && rm --force ./*.whl

#COPY ./migrations ./migrations
#COPY ./alembic.ini ./

RUN mkdir -p /media && chown app /media

# Switch to non privileged user
USER app

HEALTHCHECK --interval=5s --timeout=1s --retries=3 \
  CMD curl --fail -I http://localhost:5000/version || exit 1

VOLUME /media

# Launcher
COPY --chmod=555 entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

EXPOSE 5000
