FROM python:3-alpine


# System deps:

RUN apk --no-cache add \
     bash \
     build-base \
     curl \
     gcc \
     gettext \
     git \
     libffi-dev \
     linux-headers \
     musl-dev \
     postgresql-dev \
     tini

COPY . /code
WORKDIR /code

COPY entrypoint.sh /docker-entrypoint.sh


# Project initialization:

RUN chmod +x "/docker-entrypoint.sh" \
  && pip install pipenv \
  && pipenv install python-telegram-bot 


ENTRYPOINT ["/sbin/tini", "--", "/docker-entrypoint.sh"]


