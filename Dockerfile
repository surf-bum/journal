FROM python:3.12.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /opt/journal

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY blueprints ./blueprints
COPY orm ./orm
COPY settings ./settings
COPY templates ./templates
COPY app.py config.py gunicorn.conf.py manage.py utils.py ./

CMD ["python", "manage.py", "gunicorn"]