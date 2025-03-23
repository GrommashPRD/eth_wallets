FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip wheel setuptools
COPY req.txt req.txt
RUN pip install -r req.txt

COPY . /app

EXPOSE 8000

ENTRYPOINT ["python", "./manage.py"]