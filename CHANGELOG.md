# Changelog

## 2021-06-08
* Added support for multiple sessions per headless client.
  * Prior to now, headless clients and sessions were treated as the same, with only a headless client's first session being viewable/usable. Now it is possible to switch between more than one session and perform actions on them.
  * The headless client manager has been updated to support multiple sessions.
  * The client overview page (`client.html`) is now the session overview page (`session.html`). A new client overview page has been created, which shows information about the headless client as a whole, rather than a particular session.
  * API changes have been made. The URL for certain functions have been updated as follows:
    * Old: `/api/v1/<client_id>/status`
    * New: `/api/v1/<client_id>/<session_id>/status`
    * Session IDs are analogus to world numbers in the headless client. It must be specified in the URL for commands that take an action on a world or session (such as `status` or `users`). The URL for commands that don't interact with a world (such as `message` or `shutdown`) remains unchanged, with no session ID required.
* Fixed API endpoints to handle [NeosVR-Headless-API](https://gitlab.com/glitchfur/neosvr-headless-api)'s new method of dealing with errors.

## 2021-05-31
* Added function to the headless client manager to return information about the state of the headless client manager itself, including number of running headless clients, sessions, connected users, etc.
* Added functional dashboard page, which lists all running headless clients and displays combined statistics.
* Added API endpoint to list all running headless clients.
* Child templates can now change the content header in the base template.
* Dashboard logic moved to a separate file.
* Tweaks to the client page:
  * Name of client now shows in content header.
  * Actual max user setting now shows instead of "25".
  * Font Awesome icon changes.

## 2021-05-28
* Added `HeadlessClientInstance` class to the headless client manager which assigns some additional attributes to headless clients and caches the output of certain commands to decrease response times.

## 2021-05-26
* Added this changelog
* Split `dashboard.html` into [base.html](neosvr_headless_webui/templates/base.html) and [dashboard.html](neosvr_headless_webui/templates/dashboard.html). `dashboard.html` was a full HTML document with minimal templating, so some features such as the navbar, sidebar, and general layout have been moved into a base template to allow their use site-wide.
* Added [manager_server.py](manager_server.py) or the "headless client manager" which is a separate process that manages various headless client instances and facilitates communication between the web application and headless clients. It should be started before the web application is started. The web application can be restarted independently of the manager server without inhibiting the headless clients in any way.
* Added API endpoints, mainly meant for asynchronous requests from web pages.
* Added client page, for viewing info on a single headless client.

## 2021-02-22
* Updated the README to point to the required API library.

## 2021-02-21
* Initial commit
* Switched from plain Bootstrap to the [AdminLTE](https://github.com/ColorlibHQ/AdminLTE) admin template.
