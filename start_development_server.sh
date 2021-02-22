#!/bin/bash
source venv/bin/activate
export FLASK_APP=neosvr_headless_webui
export FLASK_ENV=development
flask run
