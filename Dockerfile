FROM python:3.12.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /opt/journal

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# TODO make orm and settings standalone libraries
COPY orm ./orm
COPY settings ./settings

COPY app ./app
COPY gunicorn.conf.py manage.py ./

CMD ["python", "manage.py", "gunicorn"]