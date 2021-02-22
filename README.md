# NeosVR-Headless-WebUI

**NeoVR-Headless-WebUI** is a [Flask](https://palletsprojects.com/p/flask/) application that provides a web interface for managing one or several instances of the [NeosVR](https://neos.com/) [headless client](https://wiki.neos.com/Headless_Client/Server).

_This project is in very early development stages and is not currently a functioning app._ It's also semi-tailored to fit [BLFC](https://goblfc.org/)'s needs, as they are the initial users of this app, but the code may be generalized in the future to allow others to use it as well.

Furthermore, a dependency of this app is `NeosVR-Headless-API`, a Python wrapper to the headless client which is also currently in development and is not yet available as an open-source project.

This project is not officially affiliated with Neos or the Neos development team in any way.

## Configuring the app

First, make sure you have an `instance` folder created. Next, copy `config_example.py` to `instance/config.py` and edit it as needed.

## Running the development server

The development server should only be used to test code changes and is not designed to be run in production. After installing the dependencies in `requirements.txt`, you can run the app with:

```
export FLASK_APP=neosvr_headless_webui
export FLASK_ENV=development
flask run
```

Alternatively, assuming you have a virtualenv set up in `venv`, run `./start_development_server.sh`.
