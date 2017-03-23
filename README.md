# anti-banner
Anti-Banner is a simple tool to retrieve a class schedule from Banner for a 
given academic quarter and add each class to Google Calendar.


This tool is a work in-progress and although it works "good-enough", it may 
still have some bugs. Please report any such findings to the issue tracker!

## Dependencies
Python 3.5.2+  
Robobrowser  
Google API Client Library

## Prerequisites
Google API Client ID

## Preparation
To use this script, you'll need a Google API Client ID. Follow the instructions
at Step 1,
[here](https://developers.google.com/google-apps/calendar/quickstart/python)
and download the JSON file with your client id, rename it
`client_secret.json`, and place it in the project root.

You will also need to install the Google Client Library for Python  
`pip install --upgrade google-api-python-client`

### Other prep
You may edit the script before running to hardcode CAS credentials to automate
the process, otherwise you will be prompted for CAS credentials at runtime.

## Get Started
Run the script!  
`./anti-banner.py`

If it's your first time running the script, your browser will be opened to
obtain OAuth credentials for your Google Account. Login to the Google account
you'd like to import the schedule into.
