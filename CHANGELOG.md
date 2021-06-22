# Changelog

## 2021-06-22
* The host user of a headless client is now treated specially on session pages. The headless user's name now shows in bold, has a hoverable info icon explaining its purpose, and has had its action buttons removed.

## 2021-06-21
* Resolved a variable name conflict in `HeadlessClientInstance` where `name`, the attribute for the name of the client, was overriding `name()`, the function to get the name of a session.
  * The client's name can now be obtained through the `client_name` attribute.

## 2021-06-19
* The following API endpoints have been added, accessible at `/api/v1/<client_id>`:
  * `/<session_id>/close` - Close a session/world
  * `/<session_id>/silence` - Silence a user
  * `/<session_id>/unsilence` - Unsilence a user
  * `/unban` - Unban a user
  * `/list_bans` - List all active bans
  * `/unban_by_name` - Unban a user by username
  * `/ban_by_id` - Ban a user by user ID
  * `/unban_by_id` - Unban a user by user ID
  * `/<session_id>/role` - Change a user's role
  * `/<session_id>/name` - Change the name of a session/world
  * `/<client_id>/<session_id>/description` - Change the description of a session/world

## 2021-06-16
* Fixed a bug that caused global actions to return HTTP 500 errors in production environments.

## 2021-06-12
* Added several new "global actions" that can be perfomed on all sessions across all headless clients at once. There are new API endpoints for these, as well as a new dropdown menu and search bar in the navigation bar of every page. These new actions include:
  * **Kick everywhere:** Find and kick a user from every session they are in, whether they are present or not.
  * **Ban everywhere:** Ban a user from every headless client, and optionally kick them from every session they're in as well.
  * **Find user:** Use the search bar to find a user and immediately jump to the session that they are in. This defaults to the session they're currently present in. If they're not present in any session, it will instead find the first session that they're connected to, but not present in. If they're not found at all, an error will be shown.
* OAuth endpoints have been moved into the configuration file, so they are no longer hard-coded. The OAuth "app name" as displayed on the login page is now customizable as well.

## 2021-06-09
* Improved handling of headless clients that are still starting up, and headless clients/sessions that do not exist. API calls that produce errors will now respond with JSON objects instead of returning uncaught exceptions.
  * Headless clients that are still starting up will not be listed in the API (`/api/v1/list`) until they are ready to accept commands. They will also be hidden from the dashboard until they have finished starting up.
  * Attempting to use API calls on, or pull up a client or session page for a headless client that has not fully started using its ID will return an error stating that the client is not ready yet, and to try again later.
  * Attempting API calls on a headless client ID or session ID that doesn't exist will return an error, whereas the web interface will show a 404 page.

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
