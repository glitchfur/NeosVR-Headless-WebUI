FROM python:3.9-alpine

ENV PIP_NO_CACHE_DIR=true
ENV PIP_DISABLE_PIP_VERSION_CHECK=true

RUN ["adduser", "-D", "webui"]
RUN ["pip", "install", "gunicorn"]

WORKDIR /home/webui

# NeosVR-Headless-WebUI
COPY requirements.txt .
# Install requirements for WebUI
RUN ["pip", "install", "-r", "requirements.txt"]

# NeosVR-Headless-API
RUN ["wget", "https://github.com/glitchfur/NeosVR-Headless-API/archive/refs/tags/v0.1.1-alpha.tar.gz"]
RUN ["tar", "xzf", "v0.1.1-alpha.tar.gz"]
# Install requirements for API
RUN ["pip", "install", "-r", "NeosVR-Headless-API-0.1.1-alpha/requirements.txt"]
# Move module into proper directory
RUN ["mv", "NeosVR-Headless-API-0.1.1-alpha/neosvr_headless_api", "."]

COPY . .

# Clean up
RUN ["rm", "-r", "NeosVR-Headless-API-0.1.1-alpha", "v0.1.1-alpha.tar.gz", "requirements.txt"]

USER webui:webui

ENV FLASK_APP=neosvr_headless_webui

EXPOSE 8000

CMD gunicorn -b 0.0.0.0 -w 4 "neosvr_headless_webui:create_app()"
