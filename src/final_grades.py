#!/usr/bin/env python3
"""
    final_grades.py
    Author: Joel Gomez
    Date created: 2017/12/09
    Python Version 3.5.2

    Anti-Banner Grades Fetcher - Fetches final grades from RWeb.
"""
import anti_banner as app
import grades
from lxml import html
from banner_connect import get_session

app_name = 'Final Grades Fetcher'
version = '1.0'

def get_final_grades(quarter, year):
    """
    Connects to RWeb and requests the grades of a for a particular 
    quarter and year.

    Args:
        quarter (string):    The academic quarter for the request.
        year (string):       The academic year for the request.

    Returns:
        An object containing course info for the given search data.

    Examples:
        >>> get_final_grades('spring','2017')
    """
    login_url = 'https://bannersso.ucr.edu:443/ssomanager/c/SSB'
    grades_url = 'https://banweb.ucr.edu/banprod/bwskogrd.P_ViewGrde' + \
            '?term_in=' + year + app.encode_quarter(quarter)

    session, response = get_session(login_url)
    response = session.get(grades_url)
    return extract_course_info(response.content)

def extract_course_info(content):
    """
    Parses a requests.response.content object for a grade data. The parsing 
    is a very primative selection method and may not be the most reliable 
    but it works for now.

    Args:
        content (requests.response.content):    The HTML content to parse.

    Returns:
        A list of courses, with structured course data available from the 
        parse.
    """
    courses = []
    tree = html.fromstring(content)
    # table[5] has grades
    course_table = tree.xpath('//table')[5]
    for i, data in enumerate(course_table[2:]):
        course = {}
        course['courseReferenceNumber'] = data[0].text
        course['subject'] = data[1].text
        course['courseNumber'] = data[2].text 
        course['sequenceNumber'] = data[3].text
        course['courseTitle'] = data[4].text
        course['grade'] = data[6].text
        courses.append(course)
    return courses

def main():
    """
    Prompts the user for a schedule of registered classes to retrieve, then 
    attempts to retrieve grades.
    """

    try:
        quarter,year = app.get_user_input()
        class_schedule = '{} {}'.format(quarter, year)
        courses = get_final_grades(quarter, year)
        # Check that we have received something worthwhile
        if len(courses) > 0:
            print('\n{} Available Grades:'.format(class_schedule))

            result = grades.print_grades(courses)
            if result is None:
                print('No grades available yet...')
            print('All Done!')
        else:
            print('Oops, there is nothing available for {} {}!'.format(
                app.decode_quarter(quarter), year
                ))
    # Catch a ctrl+c interrupt and print an exit message
    except KeyboardInterrupt:
        print('\nBye Felicia!')
        quit()

if __name__ == "__main__":
    app.print_greeting(app_name, version)
    main()
