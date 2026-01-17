# Entropia GpnMgr

Django based web application for management of LDAP groups and more for Gulaschprogrammiernacht.

## Logo and Badges

![GitHub last commit](https://img.shields.io/github/last-commit/entropia/gpnmgr)
![GitHub License](https://img.shields.io/github/license/entropia/gpnmgr)
![GitHub repo size](https://img.shields.io/github/repo-size/entropia/gpnmgr)


![GitHub forks](https://img.shields.io/github/forks/entropia/gpnmgr)
![GitHub Repo stars](https://img.shields.io/github/stars/entropia/gpnmgr)
![GitHub watchers](https://img.shields.io/github/watchers/entropia/gpnmgr)


## GPN Team-Manager

Project of Entropia e.V.


## Project description

With GPN Team-Manager you can manage LDAP groups and users.


## Who this project is for

This project is intended for non-profit organisations who want to easily manage their members.

## Project dependencies

Before using GPN Team-Manager, ensure you have:

* Docker installed
* an OIDC Provider (like Keycloak)
* a LDAP

## Instructions for using GPN Team-Manager

Try out GPN Team-Manager.

The docker-compose file has everything you need to get a first glance including demo data.

### Install & Run GPN Team-Manager

1. Clone this repository

```sh
git clone https://github.com/entropia/gpnmgr.git && cd gpnmgr
```

2. Start it

```sh
sudo docker compose up -d
```

Everything should be working now, so you can have a look around.

3. Visit it in the browser

The Manager should be reachable in the browser:

[http://localhost:8000](http://localhost:8000)

You can login with the following accounts:

| Username | Password | Role               |
|----------|----------|--------------------|
| admin    | admin    | full-access        |
| teamer   | teamer   | team-manager       |
| fedi     | fedi     | federation-manager |
| user     | user     |                    |


With `admin` you can set and see everything, including audit logs.

With `teamer` you can create and manage teams.

With `fedi` you can manage Mastodon Accounts.

For information on how to configure it for production, visit the additional documentation.

## Additional documentation

WIP


## Terms of use

GPN Team-Manager is licensed under [AGPL v.3](LICENSE.md).

---

ReadMe Template by [The Good Docs Project](https://thegooddocsproject.dev/).
