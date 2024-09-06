FROM python:3.11-slim

WORKDIR /app

RUN apt-get -y update && \
    apt-get -y --no-install-recommends install make curl

COPY . .

# RUN make uv && \
    # uv sync

RUN pip install joblib loguru pytest
RUN pip install -e .
