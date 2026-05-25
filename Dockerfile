# Intentionally bad Dockerfile — every V1 DFA-* check should fire on this file.
FROM nginx:latest

MAINTAINER bad@example.com

ENV API_TOKEN=ghp_realtoken123abc456 DB_PASSWORD=hardcoded-pw-shame

ARG SECRET_KEY=changeme

USER root

RUN apt-get update
RUN apt-get install -y curl

RUN curl https://get.docker.com | bash

RUN sudo chmod 777 /var/lib/myapp

RUN pip install requests

ADD ./local-file.txt /app/local-file.txt

CMD nginx -g 'daemon off;'
