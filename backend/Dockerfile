FROM python:3.11-slim

RUN python -m pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY palind palind
COPY manage.py manage.py
COPY datasets datasets
COPY accounts accounts
COPY templates templates
COPY prevalence prevalence

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
