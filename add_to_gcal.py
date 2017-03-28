#!/usr/bin/env python3
"""
    anti-banner.py
    Author: Joel Gomez
    Date created: 2017/03/08
    Python Version 3.5.2

    Anti-Banner Class Schedule Fetcher - Fetches a schedule of registered 
    classes for a specific quarter and year.
"""
from robobrowser import RoboBrowser
from datetime import datetime
from datetime import timedelta
from getpass import getpass
import json
import gcal
import argparse
import os

version = '1.0'
timeZone = 'America/Los_Angeles'
tzOffset = '-07:00'

parser = argparse.ArgumentParser()
parser.add_argument('-q', nargs='?', metavar='academic quarter', 
        help='fall, spring, winter, summer, etc.')
parser.add_argument('-y', nargs='?', metavar='academic year', help='2017, etc.')
args = vars(parser.parse_args())

PROJ_ROOT = os.path.dirname(os.path.abspath(__file__))

def print_greeting():
    """
    Prints a fancy greeting with the version number.
    """

    print('Anti-Banner Class Schedule v{}\n'.format(version))

def get_login():
    """
    Gets the CAS login info from cas_login.json file in project root or from 
    user via CLI input.

    Returns:
        A tuple with the user's netID and password.
    """

    cas_login = {}

    try:
        with open(os.path.join(PROJ_ROOT, 'cas_login.json')) as cas:
            cas_login = json.loads(cas.read())
    except:
        cas_login = {'netID' : '', 'password' : ''}

    while True:
        # Simple check for netID at least 5 characters long
        if len(cas_login['netID']) < 5:
            cas_login['netID'] = input('Enter UCR netID: ')
        # Next check is to make sure something has been entered for password
        elif len(cas_login['password']) < 1:
            cas_login['password'] = getpass('Enter UCR CAS password: ')
        else:
            break

    return (cas_login['netID'], cas_login['password'])

def get_user_input():
    """
    Gets the quarter and year info from the user through CLI prompts.

    Returns:
        A tuple with the quarter and year as Strings.
    """

    # Attempt to load CLI args
    quarter = args['q']
    year = args['y']

    now = datetime.now()
    min_year = 2015

    if quarter is None:
        # Get quarter
        while True:
            print('Select a quarter (1-4): ')
            print('\t1. Fall')
            print('\t2. Winter')
            print('\t3. Spring')
            print('\t4. Summer')
            try:
                select = input()
            except KeyboardInterrupt:
                print('\nBye Felicia!')
                quit()
            if select >= '1' and select <= '4':
                if select == '1':
                    quarter = 'Fall'
                elif select == '2':
                    quarter = 'Winter'
                elif select == '3':
                    quarter = 'Spring'
                elif select == '4':
                    quarter = 'Summer'
                break;
            else:
                print('Please select a valid quarter.')

    if year is None or not int(year) >= min_year and int(year) <= int(now.year):
        # Get year
        while True:
            # A simple check for a realistic year. Banner doesn't seem to have
            # anything before 2016...
            if year is not None and int(year) >= min_year and \
            int(year) <= int(now.year):
                break;
            else:
                print('Choose a year between {} and {} (default).'
                        .format(min_year, now.year))

            try:
                year = input('{} {}?\n'.format(decode_quarter(quarter), 
                    now.year) + '(enter to accept, type new year to change) '
                        )
            except KeyboardInterrupt:
                print('\nBye Felicia!')
                quit()

            # Check if user just pressed "return" key with no input
            if len(year) == 0:
                year = str(now.year)

    return (decode_quarter(quarter).title(), year)

def decode_quarter(quarter):
    """
    Helper function to format a quarter for output from a numeric value or 
    English form.

    Args:
        quarter (string):   The academic quarter to decode, could be English 
                            term i.e. "Spring" or a numeric representation of 
                            the quarter i.e. "3" for Spring.
    Returns:
        A formatted string representing the academic quarter in English.
    """
    if quarter.lower() == 'fall' or quarter == '1':
        return 'Fall'
    if quarter.lower() == 'winter' or quarter == '2':
        return 'Winter'
    if quarter.lower() == 'spring' or quarter == '3':
        return 'Spring'
    if quarter.lower() == 'summer' or quarter == '4':
        return 'Summer'
    else:
        return None

def encode_quarter(quarter):
    """
    Helper function to encode a quarter from English to a numeric value 
    that Banner understands.

    Args:
        quarter (string):    The academic quarter to encode.

    Returns:
        A numeric representation of the quarter that Banner understands:
            Spring = 20, Winter = 10, Fall = 40, Summer = 30
    """

    term = '40' # default quarter is Fall
    if quarter.lower() == 'fall':
        term = '40'
    elif quarter.lower() == 'winter':
        term = '10'
    elif quarter.lower() == 'spring':
        term = '20'
    elif quarter.lower() == 'summer':
        term = '30'

    return term

def get_schedule(quarter, year):
    """
    Connects to Banner and returns a JSON object of a student class schedule 
    for a particular quarter and year.

    Args:
        quarter (string):    The academic quarter for the schedule request.
        year (string):       The academic year for the schedule request.

    Returns:
        A JSON object containing registered classes for the given search data.

    Examples:
        >>> get_schedule('spring','2017')
    """

    sched_url = 'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb' + \
            '/registrationHistory/reset?term=' + year + encode_quarter(quarter)

    # Get RoboBrowser instance, set BeautifulSoup parser to default HTML 
    # parser for Python
    browser = RoboBrowser(parser='html.parser')

    # Navigate to schedule url
    browser.open(sched_url)

    # Get a reference to the CAS login form from the login redirect
    form = browser.get_forms()[0]

    cas_login = {}
    cas_login['netID'], cas_login['password'] = get_login()

    # Fill out the CAS form programmatically
    form['username'].value = cas_login['netID']
    form['password'].value = cas_login['password']

    # Submit the CAS login form
    form.serialize()
    browser.submit_form(form)

    try:
        parsed_json = json.loads(str(browser.parsed))
        with open('{}_{}_dump.json'.format(quarter.lower(), year), 'w') as dump:
            dump.write(str(browser.parsed))
    except json.decoder.JSONDecodeError:
        # Error parsing JSON data, login probably failed?
        print('Something went wrong... Did you enter the correct password?')
        print('netID: {}'.format(cas_login['netID']))
        print('password: hidden')
        print('Last page fetched:')
        print(browser.find('title').string)

        # Dump full HTML source of the last page fetched
        # print(browser.parsed)
        exit(1)

    return parsed_json['data']['registrations']

def get_days(meetingTimes):
    """
    Creates a string for the days of the week the course is on.

    Args:
        meetingTimes (dict):    The meetingTimes key from the JSON output of 
                                get_schedule()

    Returns:
        A string consisting of the days of the week the course is scheduled 
        on.
    """

    day_strings = ''

    if meetingTimes['monday']:
        day_strings = day_strings + 'MO,'
    if meetingTimes['tuesday']:
        day_strings = day_strings + 'TU,'
    if meetingTimes['wednesday']:
        day_strings = day_strings + 'WE,'
    if meetingTimes['thursday']:
        day_strings = day_strings + 'TH,'
    if meetingTimes['friday']:
        day_strings = day_strings + 'FR,'
    if meetingTimes['saturday']:
        day_strings = day_strings + 'SA,'

    return day_strings[:-1]

def get_instructor(faculty):
    """
    Gets the instructor info for the given course.

    Args:
        faculty (dict): The faculty key from the JSON output of get_schedule()

    Returns:
        A tuple with the instructor name and email address.
    """

    if len(faculty) >= 1:

        # Iterate through all faculty entries (sometimes there are multiple)
        for i in faculty:

            # Return the primary instructor for the course
            if i['primaryIndicator']:
                if i['emailAddress']:
                    return (i['displayName'], i['emailAddress'])
                else:
                    return (i['displayName'], 'Unavailable')

    return ('Unavailable','Unavailable')

def print_course_info(course):
    """
    Prints all of the relevant info for a course.

    Args:
        course (dict):  A dict of all the course info returned from a single 
                        entry of the JSON output of get_schedule()
    """

    # TODO: handle multiple meeting times
    times = course['meetingTimes'][0]

    print('CRN: {}'.format(course['courseReferenceNumber']))
    print('Subject: {}'.format(course['subjectDescription']))
    print('Course: {} {}'.format(course['subject'], course['courseNumber']))
    print('Course Description: {}'.format(course['courseTitle']))
    print('Course start: {}'.format(times['startDate']))
    print('Course end: {}'.format(times['endDate']))
    print('Instructor: {}'.format(get_instructor(course['faculty'])[0]))
    print('Instructor email: {}'.format(get_instructor(course['faculty'])[1]))
    print('Course Category: {}'.format(course['scheduleDescription']))
    print('Start time: {}'.format(times['beginTime']))
    print('End time: {}'.format(times['endTime']))
    print('Room: {}, {} {}'.format(times['buildingDescription'], times['building'], times['room']))
    print('Days: {}\n'.format(get_days(times)))

def decrement_day(startDate):
    """
    Returns a day previous to a relative date.

    Args:
        startDate (string): the reference date (YYYY-MM-DD)

    Returns:
        A new date, exactly one day behind the original date.
    """

    new_date = datetime.strptime(startDate, '%Y-%m-%d') - timedelta(days=1)
    return new_date.strftime('%Y-%m-%d')

def format_date(unformatted):
    """
    Creates an international-date formatted date string from a course start 
    date.

    Args:
        unformatted (string): The unformatted date (MM/DD/YYYY)
    Returns:
        The same date formatted in ISO format YYYY-MM-DD
    """

    return datetime.strptime(unformatted, '%m/%d/%Y').strftime('%Y-%m-%d')

def format_time(unformatted):
    """
    Creates a time that is formatted for an event start or end time.

    Args:
        unformatted (string): The unformatted time (hhmm)
    Returns:
        the same time, formatted in hh:mm:ss.000-tz:of
    """
    if unformatted:
        hour = unformatted[:2]
        minute = unformatted[2:]
        return '{}:{}:00.000{}'.format(hour, minute, tzOffset)
    else:
        return '00:00:00.000{}'.format(tzOffset)

def course_to_event(course):
    """
    Creates a Calendar-friendly event object that can be inserted into a 
    calendar.

    Args:
        course (dict): The course object to create an event from.
    Returns:
        A calendar event representation of the course.
    """

    # TODO: handle multiple meeting times
    times = course['meetingTimes'][0]

    dayBehind = decrement_day(format_date(times['startDate']))
    hardEnd = format_date(times['endDate']).replace('-', '') + 'T000000Z'
    endTime = dayBehind + 'T' + format_time(times['endTime'])
    startTime = dayBehind + 'T' + format_time(times['beginTime'])

    location = times['building'] + ' ' + times['room']

    course_info = course['subject'] + '-' + course['courseNumber'] + '-' + \
            course['sequenceNumber'] + ' - ' + course['courseTitle'].title()

    other_info = 'Instructor: ' + get_instructor(course['faculty'])[0] + '\n' + \
            'Instructor email: ' + get_instructor(course['faculty'])[1] + \
            '\n' + course['scheduleDescription']

    event = {
            'summary' : course_info,
            'location' : location,
            'description' : other_info,
            'start' : {
                'dateTime' : startTime,
                'timeZone': timeZone,
                },
            'end': {
                'dateTime' : endTime,
                'timeZone': timeZone,
                },
            'recurrence' : [
                'RRULE:FREQ=WEEKLY;UNTIL=' + hardEnd + ';BYDAY=' + \
                        get_days(times)
                ],
            # 'attendees' : [
            #     ],
            # 'reminders' : {
            #     'useDefault' : False,
            #     'overrides' : [
            #         {'method' : 'popup', 'minutes' : 10},
            #         ],
            #     },
            }
    return event

def import_to_gcal(calendar, events):
    """
    Imports a courses object into Google Calendar using gcal.py

    Args:
        events (obj): the events to import.
    """

    calendar_list = gcal.get_calendar_list()
    calendars = gcal.calendar_exists(calendar=calendar, 
            calendarList=calendar_list)
    if calendars:
        for cal_id in gcal.calendar_exists(calendar=calendar, 
                calendarList=calendar_list):
            while True:
                confirm = input('{} calendar exists, id: {}. Delete? (y/n)'
                        .format(calendar, cal_id))
                if confirm.lower() == 'n':
                    print('Okay. Please resolve the conflict and try ' + \
                            'again.')
                    exit(1)
                elif confirm.lower() == 'y':
                    print('Deleting {}'.format(calendar))
                    gcal.delete_calendar(calendar=cal_id)
                    break;
    cal = gcal.create_calendar(calendar=calendar, 
            calendarList=calendar_list)
    print('Calendar created, id: {}'.format(cal['id']))

    for course in events:
        if course['meetingTimes'][0]['beginTime']:
            # Course has a valid start time
            class_event = course_to_event(course)
            print('Adding {} to {} calendar'.format(class_event['summary'], 
                calendar))
            event = gcal.create_calendar_event(calendar=cal['id'],event=class_event)

            # Delete first (dummy) instance of course
            clean_up_events(calendar=cal['id'], event=event['id'], 
                    capDate=class_event['start']['dateTime'])
        elif course['instructionalMethodDescription'].lower() == 'online':
            # Check if course is online
            class_event = course_to_event(course)
            print('CAUTION! {} is ONLINE, skipping calendar'.format(
                class_event['summary']))

def clean_up_events(calendar, event, capDate):
    """
    Deletes the first instance of an event on calendar for a date. This is 
    mostly a band-aid for some glitch that causes recurring events to also be 
    inserted on the day the recurrence begins.

    Args:
        calendar (string):  calendar to nuke
        event   (string);   event id to look for
        capDate (string):   date to nuke all events off
    """

    # Get all instances of the given course
    instances = gcal.get_event_instances(calendar=calendar, event=event)
    
    for instance in instances['items']:
        # Double check that the we have the correct date
        if instance['start']['dateTime'][:10] == capDate[:10]:
            gcal.delete_calendar_event(calendar=calendar, event=instance['id'])
            break

def main():
    """
    Prompts the user for a schedule of registered classes to retrieve and adds 
    it to their Google Calendar.
    """

    print_greeting()

    try:
        quarter,year = get_user_input()
        class_schedule = '{} {}'.format(quarter, year)

        print('Connecting to Banner...')
        courses = get_schedule(quarter, year)

        # Check that we have received something worthwhile
        if len(courses) > 0:
            print('\n{} Schedule:'.format(class_schedule))

            # print_course_info(courses[7]) # print the first course only
            # pprint(course_to_event(courses[7]))
            # test_course = [courses[7]]
            # import_to_gcal(calendar=class_schedule, events=test_course)
            # for course in courses:
            #     print_course_info(course) # print raw course info (debug)

            import_to_gcal(calendar=class_schedule, events=courses)
            print('All Done!')
        else:
            print('Oops, that schedule is not available!')
    # Catch a ctrl+c interrupt and print an exit message
    except KeyboardInterrupt:
        print('\nBye Felicia!')
        quit()

if __name__ == "__main__":
    main()
