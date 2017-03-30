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

    app.print_greeting(app_name, version)

    try:
        quarter,year = app.get_user_input()
        class_schedule = '{} {}'.format(quarter, year)

        print('Connecting to Banner...')
        courses = app.parse_response(app.get_schedule(quarter, year))

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
    main()
