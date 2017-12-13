#!/usr/bin/env python3
"""
    gpa.py
    Author: Joel Gomez
    Date created: 2017/12/13
    Python Version 3.5.2

    Anti-Banner GPA Fetcher - Fetches GPA from RWeb student profile.
"""
import sys
import json
import anti_banner as app
from banner_connect import get_session

app_name = 'GPA Fetcher'
version = '1.0'

def sid_from_cred():
    """
    Gets SID from credentials.json file.

    Returns:
        The SID number (string) if present, None otherwise.
    """
    if app.args['c']:
        try:
            with open(app.args['c']) as cas:
                sid = json.loads(cas.read())['sid']
            return sid
        except:
            pass
    else:
        return None

def get_gpa(sid=sid_from_cred(), session=get_session()[0]):
    """
    Connects to RWeb and requests the overall GPA a for a particular sid.

    Args:
        sid (string):               The student id to retreive the GPA for.
        session (requests.Session)  An optional requests.Session that has 
                                    already been authenticated.

    Returns:
        The overall GPA as a string if the SID is valid and the user is 
        authorized to view it. Otherwise, return is None.

    Examples:
        >>> get_gpa('861230987')
    """
    if sid is None:
        return None
    profile_url = 'https://studentssb.ucr.edu/StudentSelfService/ssb/studentProfile'
    gpa_endpoint = '/viewGPAHoursList?studentId=' + sid

    # need to load student profile first before API is active
    response = session.get(profile_url)
    response = session.get(profile_url+gpa_endpoint)
    try:
        gpa = json.loads(response.text)['overallGpa']
    except:
        gpa = None
    return gpa

def main(sid):
    """
    """

    try:
        gpa = get_gpa(sid)
        print(gpa)
    # Catch a ctrl+c interrupt and print an exit message
    except KeyboardInterrupt:
        print('\nBye Felicia!')
        quit()

if __name__ == "__main__":
    sid = sid_from_cred()
    if app.args['c'] and sid is not None:
        if sid is not None:
            app.print_greeting(app_name, version)
            main(sid)
        else:
            print('Could not find SID in credentials.json')
            exit(1)
    else:
        print('Usage: {} -c /path/to/credentials.json'.format(sys.argv[0]), file=sys.stderr)
