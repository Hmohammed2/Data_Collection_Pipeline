# syntax=docker/dockerfile:1

FROM python:3.8

WORKDIR /web-scraper

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./src ./src

CMD ["python", "./src/main/scraper.py"]