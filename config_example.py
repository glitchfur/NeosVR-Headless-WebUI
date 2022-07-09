# This is a blank reference configuration. Do not edit this directly.
# Copy this file to "config.py" in your instance folder and fill values there.

# App name, displayed on every page in the top-left corner when logged in.
APP_NAME = "Event Name"
# Optional app logo, which is displayed to the left of the app name and also on
# the login page if it exists. The path should be relative to the instance
# folder. The image must be a PNG image. Image size should ideally be 256x256 or
# less as it will be scaled down.
APP_LOGO = "logo.png"
# Logging file path, used for logging actions by users.
# If left a blank string, no logging to a file will occur.
LOG_FILE = ""
# Secret key used for encrypting session cookies.
# A secure random key can be generated like this:
# python -c 'import os; print(os.urandom(16))'
SECRET_KEY = ""
# Location of the SQLite database for storing users.
DB_NAME = "users.db"
# Host and port of the manager server. Defaults are provided.
MANAGER_HOST, MANAGER_PORT = "127.0.0.1", 16882
# Links to external sites which are displayed in the sidebar can be specified
# here. They will show up underneath the "Dashboard" link at the top.
# Every link should be a tuple containing three strings: The first one being
# the Font Awesome classes to use for the navigation icon, the second being the
# name of the link, and the third being the link itself.
# Example: ("fas fa-globe", "Neos Website", "https://neos.com/")
SIDEBAR_LINKS = []
# Show or hide the "Invite" and "Message" buttons on session pages.
# Both of these actions require being friends with the Neos account hosting the
# session. If you are hosting a public session, this may not be the case for
# most people, and so it may be desirable to hide these functions. Note that
# this is only a cosmetic change. It doesn't prevent the use of the API calls
# for inviting or messaging users.
ENABLE_INVITE = True
ENABLE_MESSAGE = True
