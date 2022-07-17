FROM python:3.9-alpine

ENV PIP_NO_CACHE_DIR=true

RUN ["adduser", "-D", "webui"]
RUN ["pip", "install", "gunicorn"]

WORKDIR /home/webui

COPY requirements.txt .
# Install requirements for web dashboard
RUN ["pip", "install", "-r", "requirements.txt"]

RUN ["wget", "https://github.com/glitchfur/NeosVR-Headless-API/archive/refs/heads/master.tar.gz"]
RUN ["tar", "xzf", "master.tar.gz"]
# Install requirements for API
RUN ["pip", "install", "-r", "NeosVR-Headless-API-master/requirements.txt"]
# Move module into proper directory
RUN ["mv", "NeosVR-Headless-API-master/neosvr_headless_api", "."]
# Clean up
RUN ["rm", "-r", "NeosVR-Headless-API-master", "master.tar.gz", "requirements.txt"]

COPY . .

USER webui:webui

ENV FLASK_APP=neosvr_headless_webui

EXPOSE 8000

CMD gunicorn -b 0.0.0.0 -w 4 "neosvr_headless_webui:create_app()"
