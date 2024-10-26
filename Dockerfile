FROM python:3.12.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /opt/journal

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

WORKDIR /opt/journal/app

CMD ["python", "manage.py", "gunicorn"]