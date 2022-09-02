FROM python:3.8

WORKDIR /AICOREPROJECT_DATACOLLECTION

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./src ./src
COPY ./images ./images
COPY ./raw_data ./raw_data

WORKDIR /AICOREPROJECT_DATACOLLECTION

CMD ["python", "src/main/scraper.py"]
