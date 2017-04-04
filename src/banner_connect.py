#!/usr/bin/env python3
"""
    banner_connect.py
    Author: Joel Gomez
    Date created: 2017/04/03
    Python Version 3.5.2

    Utils for connecting to banner and retreiving data
"""
from robobrowser import RoboBrowser
from sys import exit
import anti_banner as app

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

    # Get RoboBrowser instance, set BeautifulSoup parser to default HTML 
    # parser for Python
    browser = RoboBrowser(parser='html.parser')

    # Navigate to schedule url
    if not app.SILENT:
        print('Connecting to Banner...')
    browser.open(sched_url)

    # Get a reference to the CAS login form from the login redirect
    form = browser.get_forms()[0]

    credentials = {}
    credentials['netID'], credentials['password'] = app.get_login()

    # Fill out the CAS form programmatically
    form['username'].value = credentials['netID']
    form['password'].value = credentials['password']

    # Submit the CAS login form
    form.serialize()
    browser.submit_form(form)

    app.cache_data(term, str(browser.parsed))

    return str(browser.parsed)

def main():
    quarter = app.decode_quarter(app.args['q']).title()
    year = app.args['y']
    app.parse_response(get_schedule(quarter, year))

if __name__ == "__main__":
    if app.args['q'] and app.args['y'] and int(app.args['y']) >= 2015 and \
            int(app.args['y']) <= int(app.TODAY.year):
        main()
    exit(0)
