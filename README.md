# anti-banner
Anti-Banner is a set of simple tools to enhance or improve the UCR Banner 
system.  

`main.py` is the standalone CLI  

These are two required arguments:  
`-q [quarter]` - the academic you'd like to use in your query  
`-y [year]` - the academic year you'd like to use in your query  

Additionally, the following optional arguments are also available:  
`-c [path/to/credentials]` - the path to your credentials.json  
`--cached` - use locally cached data instead of downloading the latest data 
from Banner
--test - test push notification system

Example: `./main.py -q winter -y 2017 -c /home/bob/credentials.json`

## Utilities
* `add_to_gcal.py` - Gets a class schedule by academic quarter and year and adds 
the schedule to Google Calendar.  
* `grades.py` - Gets course grades from the registration info on Banner. Often 
times, grades are available here before they are officially posted.  
* `final_grades.py` - Gets final grades posted on RWeb. This is useful for
quarters that predate Banner. If `grades.py` cannot find grade info, it will 
fallback to using this tool.  
* `banner_changes.py` - Checks Banner for changes in registration data. 
Could be scheduled to run on a timed interval and send notifications of any 
changes.

These tools are a work in-progress and although they may work "good-enough", 
there may still be some bugs. Please report any such findings to the issue 
tracker!

## Dependencies
Python 3.5.2+ (Python2.7 should work too)  
requests  
Google API Client Library

## Prerequisites
Google API Client ID (required for add_to_gcal.py)

## Preparation
To use the add_to_gcal.py script, you'll need a Google API Client ID. Follow 
the instructions at Step 1,
[here](https://developers.google.com/google-apps/calendar/quickstart/python)
and download the JSON file with your client id, rename it
`client_secret.json`, and place it in the project root.

You will also need to install the Google Client Library for Python  
`pip install --upgrade google-api-python-client` 
or 
`pip3 install --upgrade google-api-python-client`

### Other prep
You may create a JSON file, `credentials.json`, to store CAS credentials to 
automate the process, otherwise you will be prompted for CAS credentials at 
runtime.  

credentials.json file structure should be  
```
{
    "netID" : "your_net_id_here",
    "password" : "your_CAS_password_here",
    "pushbullet" : "your_pushbullet_api_key",
    "ifttt" : "your_IFTTT_maker_channel_api_key"
}
```

## Get Started
Run the scripts!  

You may specify the academic quarter with the optional `-q` flag, and year 
with the optional `-y` flag. The scripts will default to CLI prompts if no 
arguments are passed for each respective argument or if there is no 
credentials.json file.  

`./add_to_gcal.py -q winter -y 2017`  

`./grades.py -q winter -y 2017`

`./banner_changes.py -q winter -y 2017`

If it's your first time running the add_to_gcal.py script, your browser will be 
opened to obtain OAuth credentials for your Google Account. Login to the Google 
account you'd like to import the schedule into.
