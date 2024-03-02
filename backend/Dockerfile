FROM python:3.13.0a4-slim

RUN python -m pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY curesdev curesdev
COPY manage.py manage.py
COPY datasets datasets
COPY accounts accounts
COPY static static
COPY templates templates

COPY db.sqlite3 db.sqlite3

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
