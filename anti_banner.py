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
from pprint import pprint

version = '0.5'
timeZone = 'America/Los_Angeles'
tzOffset = '-07:00'

# Hardcoding CAS login is only required for automation
cas_login = {
        'netID':'',
        'password':''
        }

def print_greeting():
    """
    Prints a fancy greeting with the version number.
    """

    print('Anti-Banner Class Schedule v{}\n'.format(version))

def get_login():
    """
    Gets the CAS login info from the user through command line prompts.

    Returns:
        A tuple with the user's netID and password.
    """

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
    Gets the quarter and year info from the user through command line prompts.

    Returns:
        A tuple with the quarter and year as Strings.
    """

    quarter = ''
    year = ''
    now = datetime.now()

    # Get quarter
    while True:
        print('Select a quarter (1-4): ')
        print('\t1. Fall')
        print('\t2. Winter')
        print('\t3. Spring')
        print('\t4. Summer')
        select = input()
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

    # Get year
    while True:
        year = input('{} {}?\n(enter to accept, type new year to change) '
                .format(quarter, now.year)
                )

        # Check if user just pressed "return" key with no input
        if len(year) == 0:
            year = str(now.year)

        # A simple check for a realistic year. Banner doesn't seem to have
        # anything before 2016...
        if int(year) >= int(2016) and int(year) <= int(now.year):
            break;
        else:
            print('Let\'s try that again...')

    return (quarter,year)

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

    # Get the netID info if the global values aren't set
    if len(cas_login['netID']) == 0 or len(cas_login['password']) == 0:
        cas_login['netID'], cas_login['password'] = get_login()

    # Fill out the CAS form programmatically
    form['username'].value = cas_login['netID']
    form['password'].value = cas_login['password']

    # Submit the CAS login form
    form.serialize()
    browser.submit_form(form)

    try:
        parsed_json = json.loads(str(browser.parsed))
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
                return (i['displayName'], i['emailAddress'])

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

    hour = unformatted[:2]
    minute = unformatted[2:]
    return '{}:{}:00.000{}'.format(hour, minute, tzOffset)

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
            course['sequenceNumber'] + ' - ' + course['courseTitle']

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
        class_event = course_to_event(course)
        print('Adding {} to {} calendar'.format(class_event['summary'], 
            calendar))
        gcal.create_calendar_event(calendar=cal['id'],event=class_event)

def clean_up_events(calendar, capDate):
    """
    Deletes all events on the created calendar for the start date. This is 
    mostly a band-aid for some glitch that causes recurring events to also be 
    inserted on the day the recurrence begins.

    Args:
        calendar (string):  calendar to nuke
        capDate (string):   date to nuke all events off
    """

    events = gcal.get_events_by_day(calendar=calendar, stopDay=capDate)
    for event in events['items']:
        print('{} {}'.format(event['summary'], event['id']))
        gcal.delete_calendar_event(calendar=calendar, event=event['id'])
    # TODO: finish this... get events, delete events, etc.

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
            start_date = format_date(courses[0]['meetingTimes'][0]['startDate'])
            cal = gcal.calendar_exists(calendar=class_schedule, 
                    calendarList=gcal.get_calendar_list())
            print(cal)
            clean_up_events(calendar=cal[0], capDate=start_date)
            print('All Done!')
        else:
            print('Oops, that schedule is not available!')
    # Catch a ctrl+c interrupt and print an exit message
    except KeyboardInterrupt:
        print('\nBye Felicia!')
        quit()

if __name__ == "__main__":
    main()
