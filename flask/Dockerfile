FROM python:3.9-slim AS base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install Flask Flask-SQLAlchemy

RUN python3 -m venv venv

CMD ["flask", "run", "--host=0.0.0.0"]
