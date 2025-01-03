FROM python:3.12-slim

WORKDIR /home/django/app

RUN useradd -ms /bin/bash django_user

USER django_user

EXPOSE 8000

CMD ["tail", "-f", "/dev/null"]
