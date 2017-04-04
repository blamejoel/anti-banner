#!/usr/bin/env python3
"""
    anti_banner.py
    Author: Joel Gomez
    Date created: 2017/03/28
    Python Version 3.5.2

    Various helper functions for Anti-Banner utils
"""
from robobrowser import RoboBrowser
from datetime import datetime
from getpass import getpass
import json
import argparse
import os
import shelve

parser = argparse.ArgumentParser()
parser.add_argument('-q', nargs='?', metavar='academic quarter', 
        help='fall, spring, winter, summer, etc.')
parser.add_argument('-y', nargs='?', metavar='academic year', 
        help='2017, etc.')
parser.add_argument('-c', nargs='?', metavar='credentials file', 
        help='path/to/your/credentials_file.json')
parser.add_argument('--silent', action='store_true', help='suppresses output')
parser.add_argument('--debug', action='store_true', 
        help='store dumps for debugging')
parser.add_argument('--cached', action='store_true', 
        help='use cached data, if available')
args = vars(parser.parse_args())

data_file = 'reg.db'
PROJ_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(PROJ_ROOT, '.logs')
DATA_DIR = os.path.join(PROJ_ROOT, '.data')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
SILENT = args['silent']
DEBUG = args['debug']
CACHED = args['cached']

def print_greeting(module, version):
    """
    Prints a fancy greeting with the version number.
    """

    print('Anti-Banner {} v{}\n'.format(module, version))

def get_login():
    """
    Gets the CAS login info from credentials.json file in project root or from 
    user via CLI input.

    Returns:
        A tuple with the user's netID and password.
    """

    credentials = {}

    if args['c']:
        try:
            with open(args['c']) as cas:
                credentials = json.loads(cas.read())
        except:
            print('{} is not a valid path.'.format(args['c']))
            exit(1)
    else:
        try:
            with open(os.path.join(PROJ_ROOT, 'credentials.json')) as cas:
                credentials = json.loads(cas.read())
        except:
            credentials = {'netID' : '', 'password' : ''}

    while True:
        # Simple check for netID at least 5 characters long
        if len(credentials['netID']) < 5:
            credentials['netID'] = input('Enter UCR netID: ')
        # Next check is to make sure something has been entered for password
        elif len(credentials['password']) < 1:
            credentials['password'] = getpass('Enter UCR CAS password: ')
        else:
            break

    return (credentials['netID'], credentials['password'])

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

def parse_response(response):
    """
    Parses a JSON response from Banner

    Args:
        response (string):  The JSON response from Banner that needs to be 
                            parsed.
    Returns:
        A parsed object of the course registration data.
    """
    try:
        parsed_json = json.loads(response)
        term = parsed_json['data']['registrations'][0]['termDescription'] \
            .replace(' ','_').lower()
        if DEBUG:
            dump_file = os.path.join(LOG_DIR, '{}_dump.json'.format(term))
            with open(dump_file, 'w') as dump:
                dump.write(response)
    except json.decoder.JSONDecodeError:
        # Error parsing JSON data, login probably failed?
        print('Something went wrong... Did you enter the correct password?')
        print('Check error log. Banner may also be unavailable right now.')
        now = datetime.now()
        err_file = os.path.join(LOG_DIR, '{}_error.log'.format(
            now.strftime('%Y-%m-%d')))
        with open(err_file, 'a') as dump:
            dump.write(now.strftime('### %Y-%m-%d : %H:%M'))
            dump.write(str(response))
            dump.write('\n\n')

        exit(1)

    return parsed_json['data']['registrations']

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
    term = '_' + year + quarter
    if CACHED:
        with shelve.open(os.path.join(DATA_DIR, data_file)) as data:
            if term in data:
                reg_data = data[term]['data']
                if not SILENT:
                    print('Cached data available from {}'.format(
                        data[term]['dumpDate']))
                return reg_data

    sched_url = 'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb' + \
            '/registrationHistory/reset?term=' + year + encode_quarter(quarter)

    # Get RoboBrowser instance, set BeautifulSoup parser to default HTML 
    # parser for Python
    browser = RoboBrowser(parser='html.parser')

    # Navigate to schedule url
    if not SILENT:
        print('Connecting to Banner...')
    browser.open(sched_url)

    # Get a reference to the CAS login form from the login redirect
    form = browser.get_forms()[0]

    credentials = {}
    credentials['netID'], credentials['password'] = get_login()

    # Fill out the CAS form programmatically
    form['username'].value = credentials['netID']
    form['password'].value = credentials['password']

    # Submit the CAS login form
    form.serialize()
    browser.submit_form(form)

    with shelve.open(os.path.join(DATA_DIR, data_file)) as data:
        now = datetime.now()
        record = { term : '' }
        record[term] = { 'dumpDate' : now.strftime('%Y-%m-%d'), 
                'data' : str(browser.parsed) }
        data[term] = record[term]

    return str(browser.parsed)

def main():
    quarter = decode_quarter(args['q']).title()
    year = args['y']
    parse_response(get_schedule(quarter, year))

if __name__ == "__main__":
    if args['q'] and args['y'] and int(args['y']) >= 2015 and int(args['y']) \
            <= int(datetime.now().year):
        main()
    exit(0)
