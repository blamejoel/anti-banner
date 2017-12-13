#!/usr/bin/env python3
"""
    banner_connect.py
    Author: Joel Gomez
    Date created: 2017/04/03
    Python Version 3.5.2

    Utils for connecting to banner and retreiving data
"""
import anti_banner as app
import requests
import re
import json
from sys import exit

def get_session(url='https://auth.ucr.edu/cas/login'):
    """
    Connects to ucr.edu and returns an authenticated session.

    Args:
        url (string):   A url to an authentication portal or that redirects 
                        to an authentication portal.

    Returns:
        A tuple containing a requests Session object for the session, 
        and the POST response.

    Examples:
        >>> get_session('rweb.ucr.edu')
    """
    auth_url = 'https://auth.ucr.edu'
    session = requests.Session()

    # Navigate to schedule url
    response = session.get(url)

    # construct POST URL from form action url
    auth_url += find_action(parse_html(response.text, 'action'))

    credentials = {}
    credentials['netID'], credentials['password'] = app.get_login()

    payload = {
            'username' : credentials['netID'],
            'password' : credentials['password'],
            'lt' : find_lt(parse_html(response.text, 'name="lt"')),
            'execution' : 'e1s1',
            '_eventId' : 'submit',
            'submit.x' : 45,
            'submit.y' : 16,
            'submit' : 'LOGIN'
            }

    # Submit the CAS login form
    response = session.post(auth_url, data=payload)
    return (session, response)


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
    if app.CACHED:
        data = app.get_cached(term)
        if data:
            return data['data']

    sched_url = 'https://registrationssb.ucr.edu/StudentRegistrationSsb/' + \
            'ssb/registrationHistory/reset?term=' + year + \
            app.encode_quarter(quarter)

    session, response = get_session(sched_url)

    # update cache
    app.cache_data(term, response.text)

    return response.text

def parse_html(html, term):
    pattern = r'\"(.+?)\"'
    start = html.find(term)
    end = html.find('>', start)
    return re.findall(pattern, html[start:end])

def find_action(ls):
    for item in ls:
        if 'cas' in item:
            return item
    return None

def find_lt(ls):
    for item in ls:
        if 'LT-' in item:
            return item
    return None

def main():
    quarter = app.decode_quarter(app.args['q']).title()
    year = app.args['y']
    app.parse_response(get_schedule(quarter, year))

if __name__ == "__main__":
    if app.args['q'] and app.args['y'] and int(app.args['y']) >= 2015 and \
            int(app.args['y']) <= int(app.TODAY.year):
        main()
    exit(0)
