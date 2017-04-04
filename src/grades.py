#!/usr/bin/env python3
"""
    grades.py
    Author: Joel Gomez
    Date created: 2017/03/24
    Python Version 3.5.2

    Anti-Banner Grades Preview Fetcher - Tries to fetch grade data before it's 
    available on RWeb.
"""
import anti_banner as app
from sys import exit
from banner_connect import get_schedule

app_name = 'Grades (Preview) Fetcher'
version = '1.0'

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

    try:
        quarter,year = app.get_user_input()
        term = '_{}{}'.format(year, quarter)
        class_schedule = '{} {}'.format(quarter, year)

        if app.CACHED:
            cache = app.get_cached(term)
            print('Grades as of {}'.format(cache['dumpDate']))

        else:
            get_schedule(quarter, year)

        cached_data = app.json.loads(app.get_cached(term)['data'])
        courses = cached_data['data']['registrations']

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
                app.decode_quarter(quarter), year
                ))
    # Catch a ctrl+c interrupt and print an exit message
    except KeyboardInterrupt:
        print('\nBye Felicia!')
        quit()

if __name__ == "__main__":
    app.print_greeting(app_name, version)
    main()
