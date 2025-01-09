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

