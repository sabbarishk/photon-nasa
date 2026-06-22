FROM python:3.11-slim

RUN pip install --no-cache-dir \
    pandas \
    numpy \
    matplotlib

RUN useradd --no-create-home --shell /bin/false sandbox
USER sandbox

WORKDIR /workspace
