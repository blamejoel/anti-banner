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
from getpass import getpass
import json

version = '0.1'

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
        day_strings = day_strings + 'M '
    if meetingTimes['tuesday']:
        day_strings = day_strings + 'T '
    if meetingTimes['wednesday']:
        day_strings = day_strings + 'W '
    if meetingTimes['thursday']:
        day_strings = day_strings + 'TH '
    if meetingTimes['friday']:
        day_strings = day_strings + 'F '
    if meetingTimes['saturday']:
        day_strings = day_strings + 'S '

    return day_strings

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
        course (dict):  A dict of all the registered courses returned from the 
                        JSON output of get_schedule()
    """
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


if __name__ == "__main__":
    print_greeting()
    try:
        quarter,year = get_user_input()

        print('\n{} {} Schedule:'.format(quarter, year))
        courses = get_schedule(quarter, year)

        # Check that we have received something worthwhile
        if len(courses) > 0:
            # print_course_info(courses[0]) # print the first course only
            for course in courses:
                print_course_info(course)
        else:
            print('Oops, that schedule is not available!')
    # Catch a ctrl+c interrupt and print an exit message
    except KeyboardInterrupt:
        print('\nBye Felicia!')
        quit()
