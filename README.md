# anti-banner
Anti-Banner is a set of simple tools to enhance or improve the UCR Banner 
system.

## Utilities
* `add_to_gcal.py` - Gets a class schedule by academic quarter and year and adds 
the schedule to Google Calendar.  
* `grades.py` - Gets course grades from the registration info on Banner. Often 
times, grades are available here before they are officially posted.  
* `banner_changes.py` - Checks Banner for changes in registration data. 
Could be scheduled to run on a timed interval and send notifications of any 
changes.

## Binaries
Packaged binaries are also available for Linux for the following utilities!
* grades
* add_to_gcal

The prepackaged binaries are ready to go with no installation required 
(hopefully). Again, nothing is promised to be working, report any bugs to the 
issues tracker.

These are the available optional arguments for the binaries:  
`-q [quarter]` - the academic you'd like to use in your query
`-y [year]` - the academic year you'd like to use in your query
`-c [path/to/credentials]` - the path to your credentials.json

Example: `./grades -q winter -y 2017 -c /home/bob/credentials.json`

These tools are a work in-progress and although they may work "good-enough", 
there may still be some bugs. Please report any such findings to the issue 
tracker!

**NOTE:** You still need a valid `client_secret.json` file in the same 
directory as the add_to_gcal binary! (see Google API Client ID in Preparation 
section)

## Dependencies
Python 3.5.2+  
Robobrowser  
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

### Other prep
You may create a JSON file, `credentials.json`, to store CAS credentials to 
automate the process, otherwise you will be prompted for CAS credentials at 
runtime.  

credentials.json file structure should be  
```
{
    "netID" : "your_net_id_here",
    "password" : "your_CAS_password_here"
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
