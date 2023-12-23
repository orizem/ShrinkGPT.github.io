# syntax=docker/dockerfile:1
FROM --platform=$BUILDPLATFORM python:3.9.7 AS builder

WORKDIR /src
COPY requirements.txt /src
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . .
EXPOSE 5000
CMD ["python3", "app.py"]