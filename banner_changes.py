#!/usr/bin/env python3
"""
    banner_changes.py
    Author: Joel Gomez
    Date created: 2017/03/28
    Python Version 3.5.2

    Checks for changes to Banner registration info for a given academic 
    quarter and year.
"""
import requests
import anti_banner as app

app_name = 'Changes'
version = '1.0'
# app.parser.add_argument('-s', action='store_true', help='suppresses output')
SILENT = app.args['silent']

def new_changes(quarter, year):
    """
    Connects to Banner and retrieves latest registration data and compares 
    it to a previous dump.

    Args:
        quarter (string):   the academic quarter to check
        year (string):      the academic year to check
    Returns:
        The new dump if there are changes, False if there are no changes
    """
    changes = False
    try:
        reg = app.get_schedule(quarter, year)

        courses = app.parse_response(reg)
        # Check that we have received something worthwhile
        if len(courses) > 0:
            try:
                with open('{}_{}_dump.json'.format(quarter.lower(), year)) as dump:
                    if dump.read() != reg:
                        changes = reg
            except IOError:
                # File was not available, create it
                with open('{}_{}_dump.json'.format(quarter.lower(), year), 
                        'w') as dump:
                    dump.write(reg)

        else:
            print('Oops, there is nothing available for {} {} yet!'.format(
                app.decode_quarter(quarter), year
                ))
    # Catch a ctrl+c interrupt and print an exit message
    except KeyboardInterrupt:
        print('\nBye Felicia!')
        quit()

    return changes

def update_changes(quarter, year, data):
    """
    Updates the last dump for a given academic term.

    Args:
        quarter (string):   the academic quarter for the dump
        year (string):      the academic year for the dump
        data (string):      the new dump data
    """
    if data:
        with open('{}_{}_dump.json'.format(quarter.lower(), year), 'w') as dump:
            dump.write(data)

def notify(data):
    """
    Sends a POST request with data to trigger a notification.

    Args:
        data (string):  The data to include in the notification (i.e. the 
        new changes)
    """
    ifttt_channel = 'banner_changes'
    url = 'https://maker.ifttt.com/trigger/' + ifttt_channel + '/with/key/'
    credentials = {}
    payload = { 'value1' : data }
    try:
        with open(app.os.path.join(app.PROJ_ROOT, 'cas_login.json')) as cas:
            credentials = app.json.loads(cas.read())
    except:
        print("Error finding API key!")
        exit(1)

    requests.post(url + credentials['ifttt'], data=payload)

def log_entry(data):
    """
    Creates a log entry with a timestamp and data.
    
    Args:
        data (string): the data to accompany the log entry.
    """
    now = app.datetime.now()
    timestamp = now.strftime('%Y-%m-%d-%H:%M')
    with open('changes.log', 'a') as log:
        log.write('{}: {}\n'.format(timestamp, data))

def main():
    """
    Checks for a change in Banner registration data since last GET
    """

    if not SILENT:
        app.print_greeting(module=app_name, version=version)

    quarter,year = app.get_user_input()

    if not SILENT:
        print('Connecting to Banner...')
    changes = new_changes(quarter, year)
    if changes:
        log_entry('New changes')
        if not SILENT:
            print('New changes!')
        notify(False)
        update_changes(changes)
    else:
        log_entry('')
        if not SILENT:
            print('Nothing new for {} {}'.format(quarter, year))

if __name__ == "__main__":
    main()
