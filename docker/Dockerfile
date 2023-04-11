FROM python:3.11 as base

ENV LANG=C.UTF-8
ENV PYTHONIOENCODING=utf8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system level dependencies.
RUN apt-get update && \
    apt-get install -y \
        curl \
        unzip && \
    apt clean

WORKDIR /workspace

# Install Poetry.
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$PATH:/root/.local/bin"
RUN poetry config virtualenvs.create false
COPY ./pyproject.toml pyproject.toml

COPY ./docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["bash", "/entrypoint.sh"]

FROM base AS dev
# Install all packages
COPY ./ /workspace/
RUN poetry install

FROM base AS prod
# Install only prod packages
COPY ./src/ src/
RUN poetry install  --no-dev
