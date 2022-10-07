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
  && pipenv install python-telegram-bot \
  && pipenv install pyTelegramBotAPI \
  && pipenv install sqlalchemy \
  && pipenv install cython \
  && pipenv install vedis \
  && pipenv run pip install psycopg2-binary



CMD ["/bin/bash"]
#CMD ["pipenv", "run", "python", "bot2.py"]

#ENTRYPOINT ["/sbin/tini", "--", "/docker-entrypoint.sh"]


