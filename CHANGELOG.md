# Changelog

## 2021-05-26
* Added this changelog
* Split `dashboard.html` into [base.html](neosvr_headless_webui/templates/base.html) and [dashboard.html](neosvr_headless_webui/templates/dashboard.html). `dashboard.html` was a full HTML document with minimal templating, so some features such as the navbar, sidebar, and general layout have been moved into a base template to allow their use site-wide.
* Added [manager_server.py](manager_server.py) or the "headless client manager" which is a separate process that manages various headless client instances and facilitates communication between the web application and headless clients. It should be started before the web application is started. The web application can be restarted independently of the manager server without inhibiting the headless clients in any way.
* Added API endpoints, mainly meant for asynchronous requests from web pages.

## 2021-02-22
* Updated the README to point to the required API library.

## 2021-02-21
* Initial commit
* Switched from plain Bootstrap to the [AdminLTE](https://github.com/ColorlibHQ/AdminLTE) admin template.
