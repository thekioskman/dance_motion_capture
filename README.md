# dance_motion_capture
FYDP - Proj

# Project Setup Guide

This guide explains how to set up a Python virtual environment and manage dependencies using `requirements.txt`.

## Table of Contents

- [Creating a Virtual Environment](#creating-a-virtual-environment)
- [Activating the Virtual Environment](#activate-the-virtual-environment)
- [Installing Packages](#installing-packages)
- [Updating requirements.txt](#updating-requirementstxt)
- [Running video comparison analysis](#running-video-comparison-analysis)

## Creating a Virtual Environment
1. python -m venv env
2. Navigate to your project directory:
   ```bash
   cd path\to\your\project

## Activate The Virtual Environment
### Windows
1. .\venv\Scripts\activate 
### macOS / Linux
1. source env/bin/activate

## Installing packages
1. pip install -r requirements.txt

## Updating requirements.txt
1. pip freeze > requirements.txt

## Running video comparison analysis
1. python compare_videos.py

## Run FAST API server
1. Run the FastAPI app using a compatible ASGI server like uvicorn
2. Command to run: `uvicorn main:app --reload`


## Running with Docker
To start the DB and the API run
```
docker compose up
```
You can attach your VS code to the running instance of the API container to develope live. The container's /dance_motion_capture directory is binded to /api on your local machine, so any changes to one will reflect in the other.

Tables for the database are declared on first startup in the init.sql in /postgres. Please run:
```
docker compose down
docker compose up --build
```
If you add any changes, because some things might be cached, so running compose up without --build might not work.

## A note on updating the DB

The actual "data" of the database is stored in a docker volume, this data will not be cleared. If you want to make changes to any Postgres Schemas, please tear down the volumes without

```
docker-compose down -v
```

and then rebuild. Note: you will lose all your DB data in this case

If you would like to look at the database on the cmd line, you can exec into the db container with the following:

```
---on your machine---
docker exec -it <container_name>

---inside the docker container---
psql -U brian -d dance_motion_db
```

## A note on adding packages
Whatever is in the requirements.txt will be installed into the container. If you want to add a package, just exec into the container, and use pip to install it. (This will ensure the package will play well with everything else we have installed) You can then pip freeze and copy that into the requirements.txt
```
---on your machine---
docker exec -it <container_name>

---inside the docker container---
pip install <package_name>
pip freeze
```

## Editing the code
You can either work locally or use the docker container as a developement enviorment. But make sure the code still works after you docker compose up. You can test the endpoint using Postman or your browser. At localhost:8000, because the docker container just binds to a host port. (in this case set to 8000)

