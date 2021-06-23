# This is a blank reference configuration. Do not edit this directly.
# Copy this file to "config.py" in your instance folder and fill values there.

# App name, displayed on every page in the top-left corner when logged in.
APP_NAME = "Event Name"
# Optional app logo, which is displayed to the left of the app name and also on
# the login page if it exists. The path should be relative to the instance
# folder. The image must be a PNG image. Image size should ideally be 256x256 or
# less as it will be scaled down.
APP_LOGO = "logo.png"
# Secret key used for encrypting session cookies.
# A secure random key can be generated like this:
# python -c 'import os; print(os.urandom(16))'
SECRET_KEY = ""
# List of user IDs authorized to access the application.
AUTHORIZED_USERS = []
# OAuth app/service name
# This is used on the login page: "Sign in with <Name>"
OAUTH_APP_NAME = ""
# OAuth client parameters for ConCat
CONCAT_CLIENT_ID = ""
CONCAT_CLIENT_SECRET = ""
# OAuth endpoints for ConCat
CONCAT_ACCESS_TOKEN_URL = ""
CONCAT_AUTHORIZE_URL = ""
CONCAT_API_BASE_URL = ""
# Host and port of the manager server. Defaults are provided.
MANAGER_HOST, MANAGER_PORT = "127.0.0.1", 16882
# Links to external sites which are displayed in the sidebar can be specified
# here. They will show up underneath the "Dashboard" link at the top.
# Every link should be a tuple containing three strings: The first one being
# the Font Awesome classes to use for the navigation icon, the second being the
# name of the link, and the third being the link itself.
# Example: ("fas fa-globe", "Neos Website", "https://neos.com/")
SIDEBAR_LINKS = []
