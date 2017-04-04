#!/usr/bin/env python3
"""
    anti_banner.py
    Author: Joel Gomez
    Date created: 2017/03/28
    Python Version 3.5.2

    Various helper functions for Anti-Banner utils
"""
from datetime import datetime
from getpass import getpass
from subprocess import run
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

TODAY = datetime.now()

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

    if year is None or not int(year) >= min_year and int(year) <= \
            int(TODAY.year):
        # Get year
        while True:
            # A simple check for a realistic year. Banner doesn't seem to have
            # anything before 2016...
            if year is not None and int(year) >= min_year and \
            int(year) <= int(TODAY.year):
                break;
            else:
                print('Choose a year between {} and {} (default).'
                        .format(min_year, TODAY.year))

            try:
                year = input('{} {}?\n'.format(decode_quarter(quarter), 
                    TODAY.year) + '(enter to accept, type new year to change) '
                        )
            except KeyboardInterrupt:
                print('\nBye Felicia!')
                quit()

            # Check if user just pressed "return" key with no input
            if len(year) == 0:
                year = str(TODAY.year)

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
        err_file = os.path.join(LOG_DIR, '{}_error.log'.format(
            TODAY.strftime('%Y-%m-%d')))
        with open(err_file, 'a') as dump:
            dump.write(TODAY.strftime('### %Y-%m-%d : %H:%M'))
            dump.write(str(response))
            dump.write('\n\n')

        exit(1)

    return parsed_json['data']['registrations']

def get_cached(key):
    """
    Gets last banner data from local cache, if available

    Args:
        quarter (string)    the academic quarter being requested
        year (string)       the academic year being requested
    Returns:
        The cached data if available, False if it's not
    """

    with shelve.open(os.path.join(DATA_DIR, data_file)) as cache:
        if key in cache:
            reg_data = cache[key]
            if not SILENT:
                print('Cached data available from {}'.format(
                    cache[key]['dumpDate']))
            return reg_data
        else:
            return None

def cache_data(key, data):
    """
    Stores data into local cache

    Args:
        key (string)    a key to index the data under in the cache
        data (?)        the data to store in the cache
    """
    with shelve.open(os.path.join(DATA_DIR, data_file)) as cache:
        record = { key : '' }
        record[key] = { 'dumpDate' : TODAY.strftime('%Y-%m-%d %H:%M'), 
                'data' : data }
        cache[key] = record[key]

def run_process(process):
    run(process.split())
