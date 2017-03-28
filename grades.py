#!/usr/bin/env python3
"""
    grades.py
    Author: Joel Gomez
    Date created: 2017/03/24
    Python Version 3.5.2

    Anti-Banner Grades Preview Fetcher - Tries to fetch grade data before it's 
    available on Rweb.
"""
from robobrowser import RoboBrowser
from datetime import datetime
from datetime import timedelta
from getpass import getpass
import json
import argparse
import os

version = '1.0'

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

    print('Anti-Banner Grades Preview v{}\n'.format(version))

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


def print_course_grade_info(course):
    """
    Prints all of the relevant info for a course.

    Args:
        course (dict):  A dict of all the course info returned from a single 
                        entry of the JSON output of get_schedule()
    """

    print('Course: {} {} - {}'.format(course['subject'], 
        course['courseNumber'], course['courseTitle'].title()))
    print('Grade: {}\n'.format(course['grade']))


def main():
    """
    Prompts the user for a schedule of registered classes to retrieve, then 
    attempts to retrieve grades.
    """

    print_greeting()

    try:
        quarter,year = get_user_input()
        class_schedule = '{} {}'.format(quarter, year)

        print('Connecting to Banner...')
        courses = get_schedule(quarter, year)

        # Check that we have received something worthwhile
        if len(courses) > 0:
            print('\n{} Available Grades:'.format(class_schedule))

            no_grades = True
            for course in courses:
                if not (course['grade'] == None):
                    print_course_grade_info(course)
                    no_grades = False

            if no_grades:
                print('No grades available yet...')
            print('All Done!')
        else:
            print('Oops, there is nothing available for {} {} yet!'.format(
                decode_quarter(quarter), year
                ))
    # Catch a ctrl+c interrupt and print an exit message
    except KeyboardInterrupt:
        print('\nBye Felicia!')
        quit()

if __name__ == "__main__":
    main()
