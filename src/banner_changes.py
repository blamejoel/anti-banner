#!/usr/bin/env python3
"""
    banner_changes.py
    Author: Joel Gomez
    Date created: 2017/03/28
    Python Version 3.5.2

    Checks for changes to Banner registration info for a given academic 
    quarter and year.
"""
import anti_banner as app
from banner_connect import get_schedule
import requests

app_name = 'Changes'
version = '1.0'

def notify(data):
    """
    Sends a POST request with data to trigger a notification.

    Args:
        data (string):  The data to include in the notification (i.e. the 
        new changes)
    """
    err = "Error finding API key!"
    ifttt_channel = 'banner_changes'
    ifttt = 'https://maker.ifttt.com/trigger/' + ifttt_channel + '/with/key/'
    pb = "https://api.pushbullet.com/v2/pushes"
    credentials = {}

    if app.args['c']:
        with open(app.args['c']) as cas:
            credentials = app.json.loads(cas.read())
        try:
            with open(app.args['c']) as cas:
                credentials = app.json.loads(cas.read())
        except:
            print(err)
            print('{} is not a valid path.'.format(app.args['c']))
            log_entry(err)
            exit(1)
    else:
        try:
            with open(os.path.join(PROJ_ROOT, 'credentials.json')) as cas:
                credentials = app.json.loads(cas.read())
        except:
            print(err)
            log_entry(err)
            exit(1)

    ifttt_payload = { 'value1' : data }
    pb_payload = { 
            'type' : 'note',
            'title' : 'New grades!',
            'body' : data
            }

    if not data:
        pb_payload['body'] = ''

    if credentials['pushbullet']:
        return requests.post(pb, auth=(credentials['pushbullet'], ''), 
                data=pb_payload)
    # if credentials['ifttt']:
    #     return requests.post(ifttt + credentials['ifttt'], data=ifttt_payload)
    else:
        print(err)
        log_entry(err)

def log_entry(data):
    """
    Creates a log entry with a timestamp and data.
    
    Args:
        data (string): the data to accompany the log entry.
    """
    now = app.datetime.now()
    timestamp = now.strftime('%Y-%m-%d-%H:%M')
    changes = app.os.path.join(app.LOG_DIR, 'changes.log')
    with open(changes, 'a') as log:
        log.write('{}: {}\n'.format(timestamp, data))

def grades_string(courses):
    """
    Creates a response string with all grades.

    Args:
        courses (object): a courses object returned from cached_data
    """
    grades = ''
    # Check that we have received something worthwhile
    if len(courses) > 0:
        no_grades = True
        for course in courses:
            if course['grade']:
                subject = '{}{}: '.format(course['subject'], 
                        course['courseNumber'])
                grades += '{0:<9}{1:2}\n'.format(subject, course['grade'])
                no_grades = False

        if no_grades:
            grades = 'No grades available yet...'

    return grades

def main():
    """
    Checks for a change in Banner registration data since last GET
    """

    if not app.SILENT:
        app.print_greeting(module=app_name, version=version)

    quarter,year = app.get_user_input()
    term = '_{}{}'.format(year, quarter)
    class_schedule = '{} {}'.format(quarter, year)

    try:
        cached_data = app.json.loads(app.get_cached(term)['data'])
    except:
        if not app.SILENT:
            print('First run...')
        reg = get_schedule(quarter, year)
        cached_data = app.json.loads(app.get_cached(term)['data'])
        pass

    if app.TEST:
        body = grades_string(cached_data['data']['registrations'])
        test_msg = '***TEST***\n{}***TEST***'.format(body)
        res = notify(test_msg)
        print(res.text)
        print(test_msg)
        exit(0)

    reg = get_schedule(quarter, year)
    new_data = app.json.loads(app.get_cached(term)['data'])

    if (cached_data != new_data):
        log_entry('New changes')
        if not app.SILENT:
            print('New changes!')
        body = grades_string(cached_data['data']['registrations'])
        res = notify(body)
        log_entry('Notification result: {}'.format(res.status_code))
        if res.status_code != 200:
            log_entry('Notification error: {}\n'.format(res.text))
    else:
        log_entry('')
        if not app.SILENT:
            print('Nothing new for {} {}'.format(quarter, year))

if __name__ == "__main__":
    main()
