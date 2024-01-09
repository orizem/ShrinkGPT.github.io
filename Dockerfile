# syntax=docker/dockerfile:1
FROM --platform=$BUILDPLATFORM python:3.9.7 AS builder

WORKDIR /ShrinkGPT.github.io
COPY . /ShrinkGPT.github.io
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

ENV NAME venv

EXPOSE 8080
CMD ["python3", "main.py"]