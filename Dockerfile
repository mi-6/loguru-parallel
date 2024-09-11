FROM python:3.11-slim

WORKDIR /app

RUN apt-get -y update && \
    apt-get -y --no-install-recommends install make curl

COPY . .

RUN make uv

ENV PATH="/root/.cargo/bin/:$PATH"
ENV PATH="/app/.venv/bin:$PATH"

RUN uv sync --frozen
