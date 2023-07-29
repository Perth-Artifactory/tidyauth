# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY main.py main.py
COPY scripts scripts

VOLUME config.json

CMD ["python3", "main.py"]
