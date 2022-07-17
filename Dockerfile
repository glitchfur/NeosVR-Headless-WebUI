FROM python:3.9-alpine

RUN ["apk", "add", "git"]

RUN ["adduser", "-D", "webui"]
USER webui:webui
WORKDIR /home/webui
ENV PATH=$PATH:/home/webui/.local/bin

COPY --chown=webui:webui . .

RUN ["pip", "install", "gunicorn"]

# Install requirements for web dashboard
RUN ["pip", "install", "-r", "requirements.txt"]

RUN ["git", "clone", "https://github.com/glitchfur/NeosVR-Headless-API"]
# Install requirements for API
RUN ["pip", "install", "-r", "NeosVR-Headless-API/requirements.txt"]
# Move module into proper directory, and remove the rest.
RUN ["mv", "NeosVR-Headless-API/neosvr_headless_api", "."]
RUN ["rm", "-rf", "NeosVR-Headless-API"]

ENV FLASK_APP=neosvr_headless_webui

EXPOSE 8000

CMD gunicorn -b 0.0.0.0 -w 4 "neosvr_headless_webui:create_app()"
