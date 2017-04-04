from __future__ import print_function
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from anti_banner import parser
from anti_banner import PROJ_ROOT

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser, parser], 
            conflict_handler='resolve').parse_args()
except ImportError:
    flags = None

# TODO: cleanup and comment this whole thing...

# If modifying these scopes, delete previously saved credentials
SCOPES = 'https://www.googleapis.com/auth/calendar'
APPLICATION_NAME = 'Anti-Banner Google Calendar API'
try:
    from secret import cs_build
    from secret import cs_finish
    CLIENT_SECRET_FILE = cs_build()
except ImportError:
    CLIENT_SECRET_FILE = 'client_secret.json'

def get_credentials():
    """Gets valid user credentials from storage.
    
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    
    Returns:
        Credentials, the obtained credential.
    """
    # PROJ_ROOT = os.path.dirname(os.path.abspath(__file__))
    credential_dir = os.path.join(PROJ_ROOT, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
            'calendar-anti-banner.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        try:
            cs_finish()
        except:
            pass
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def auth():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('calendar', 'v3', http=http)

def get_calendar_list():
    calendar_list = {}
    service = auth()

    page_token = None
    while True:
        calendar_list = service.calendarList().list(
                pageToken=page_token).execute()
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return calendar_list

def calendar_exists(calendar, calendarList):
    calendars = []

    for calendar_list_entry in calendarList['items']:
        if calendar_list_entry['summary'] == calendar:
            calendars.append(calendar_list_entry['id'])

    if len(calendars) > 0:
        return calendars
    else:
        return False

def delete_calendar(calendar):
    service = auth()
    return service.calendars().delete(calendarId=calendar).execute()

def create_calendar(calendar, calendarList):
    service = auth()

    new_calendar = {
            'summary' : calendar,
            }

    return service.calendars().insert(body=new_calendar).execute()

def create_calendar_event(calendar, event):
    service = auth()
    return service.events().insert(calendarId=calendar, body=event).execute()

def delete_calendar_event(calendar, event):
    """
    Deletes a calendar event.

    Args:
        calendar (string):  the id of the calendar to delete from
        event (string):     the id of the event to delete
    """

    service = auth()
    return service.events().delete(calendarId=calendar, eventId=event).execute()

# TODO: test this...
def get_events_by_day(calendar, stopDay):
    """
    Gets all of the calendar events on a specific day.

    Args:
        calendar (string):  the calendar id of the calendar to retrieve from
        stopDay (string):  the day of the calendar to retrieve events from

    Returns:
        A list of events.
    """

    stopDay += 'T00:00:00-07:00'
    print(stopDay)
    service = auth()
    # page_token = None
    # while True:
    #     events = service.events().list(calendarId=calendar, 
    #             pageToken=page_token, timeMax=stopDay).execute()
    #     for event in events['items']:
    #         print(event['summary'])
    #     page_token = events.get('nextPageToken')
    #     if not page_token:
    #         break
    # return events
    return service.events().list(calendarId=calendar, timeMax=stopDay).execute()

def get_event_instances(calendar, event):
    service = auth()
    return service.events().instances(calendarId=calendar, 
            eventId=event).execute()
