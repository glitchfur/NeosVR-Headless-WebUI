# Changelog

## 2021-06-26
* Fixed a bug that caused the `/api/v1/list` API endpoint to return HTTP 500 errors in production environments.
* Fixed a bug that caused "ghost" sessions/worlds to remain visible in the web interface after they were closed.

## 2021-06-25
* The following API endpoints have been added, accessible at `/api/v1/<client_id>`:
  * `/<session_id>/access_level` - Change the access level of a session/world
  * `/<session_id>/hide_from_listing` - Show or hide a session/world from Neos' public world listing
  * `/<session_id>/max_users` - Set the max user limit of a session/world
  * `/<session_id>/away_kick_interval` - Set the away kick interval (in minutes) of a session/world
* A new menu has been added to session pages (in the header of the session status card) that allows for performing the following actions: Editing the session name, editing the session description, changing the session's access level, hiding the session from the public listing, setting the session's max user limit, and setting the session's away kick interval.
* The access level of a session can also be changed by clicking its current access level in the session status card.
* Similarly, the visibility of a session in the public listing can be changed by clicking the "True" or "False" badge displayed next to "Hidden from Listing" in the session status card.
* The role of any connected user can now be changed by clicking on their current role in the user list.
* Dark mode has been added, thanks to contributor **Schuyler Cebulskie (Gawdl3y)**. It can be toggled with the sun/moon icon in the top-right corner of any page.

## 2021-06-24
* A new card has been added to client pages showing additional information about the headless client. Specifically: Neos version, compatibility hash, machine ID, and supported network protocols.
* The version of the headless client has been added to all session pages as well, in the header of the session status card.

## 2021-06-23
* Added a functional sidebar. A link to the dashboard is provided at the top, with collapsible menus underneath for currently running clients and sessions. Custom links to external sites can also be displayed in the sidebar by adding them to `config.py`. See the comments in `config_example.py` for more information.
* The app name and app logo have been moved into the configuration file to allow for customization. The app name/logo are displayed on every page across the web application. For instance, if you are running an event, you can set the app name to the name of the event. See `config_example.py` for more information.
* API endpoint `/api/v1/start` now accepts a `config` value to specify the location of a configuration file for the headless client. If it is not specified, Neos will use the default configuration location.
* Added two new variables `ENABLE_INVITE` and `ENABLE_MESSAGE` to the configuration file, which will show or hide the "Invite" and "Message" buttons on session pages. It may be desirable to hide these buttons when hosting a public session, where the Neos account hosting the session may not be friends with the people to be invited or messaged, or if there is not a Neos account logged into the headless client at all.
* Added an argument parser to the manager server. It now accepts the following arguments:
  * `--host`: Specify the host or IP to bind to. Defaults to `127.0.0.1` (previously `0.0.0.0`).
  * `-p` or `--port`: Specify the TCP port to bind to. Defaults to `16882`.

## 2021-06-22
* The host user of a headless client is now treated specially on session pages. The headless user's name now shows in bold, has a hoverable info icon explaining its purpose, and has had its action buttons removed.
* Other visual tweaks have been made to session pages. The session name, description, and tags are now displayed more prominently. A button has been added that will allow you to join the session in Neos.
* Updated [AdminLTE](https://github.com/ColorlibHQ/AdminLTE) from 3.0.5 to 3.1.0.
* Fixed button groups on client and session pages causing JavaScript errors in Bootstrap.

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
