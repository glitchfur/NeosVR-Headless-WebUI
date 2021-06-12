# This is a blank reference configuration. Do not edit this directly.
# Copy this file to "config.py" in your instance folder and fill values there.

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
