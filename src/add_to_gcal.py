#!/usr/bin/env python3
"""
    anti-banner.py
    Author: Joel Gomez
    Date created: 2017/03/08
    Python Version 3.5.2

    Anti-Banner Class Schedule Fetcher - Fetches a schedule of registered 
    classes for a specific quarter and year.
"""
import anti_banner as app
import gcal
from datetime import datetime
from datetime import timedelta
from banner_connect import get_schedule

app_name = 'Class Schedule'
version = '1.0'
UCR = 'University of California, Riverside'
timeZone = 'America/Los_Angeles'
tzOffset = '-07:00'

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
        day_strings = day_strings + 'MO,'
    if meetingTimes['tuesday']:
        day_strings = day_strings + 'TU,'
    if meetingTimes['wednesday']:
        day_strings = day_strings + 'WE,'
    if meetingTimes['thursday']:
        day_strings = day_strings + 'TH,'
    if meetingTimes['friday']:
        day_strings = day_strings + 'FR,'
    if meetingTimes['saturday']:
        day_strings = day_strings + 'SA,'

    return day_strings[:-1]

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
                if i['emailAddress']:
                    return (i['displayName'], i['emailAddress'])
                else:
                    return (i['displayName'], 'Unavailable')

    return ('Unavailable','Unavailable')

def print_course_info(course):
    """
    Prints all of the relevant info for a course.

    Args:
        course (dict):  A dict of all the course info returned from a single 
                        entry of the JSON output of get_schedule()
    """

    # TODO: handle multiple meeting times
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

def decrement_day(startDate):
    """
    Returns a day previous to a relative date.

    Args:
        startDate (string): the reference date (YYYY-MM-DD)

    Returns:
        A new date, exactly one day behind the original date.
    """

    new_date = datetime.strptime(startDate, '%Y-%m-%d') - timedelta(days=1)
    return new_date.strftime('%Y-%m-%d')

def format_date(unformatted):
    """
    Creates an international-date formatted date string from a course start 
    date.

    Args:
        unformatted (string): The unformatted date (MM/DD/YYYY)
    Returns:
        The same date formatted in ISO format YYYY-MM-DD
    """

    return datetime.strptime(unformatted, '%m/%d/%Y').strftime('%Y-%m-%d')

def format_time(unformatted):
    """
    Creates a time that is formatted for an event start or end time.

    Args:
        unformatted (string): The unformatted time (hhmm)
    Returns:
        the same time, formatted in hh:mm:ss.000-tz:of
    """
    if unformatted:
        hour = unformatted[:2]
        minute = unformatted[2:]
        return '{}:{}:00.000{}'.format(hour, minute, tzOffset)
    else:
        return '00:00:00.000{}'.format(tzOffset)

def course_to_event(course):
    """
    Creates a Calendar-friendly event object that can be inserted into a 
    calendar.

    Args:
        course (dict): The course object to create an event from.
    Returns:
        A calendar event representation of the course.
    """

    # TODO: handle multiple meeting times
    times = course['meetingTimes'][0]

    dayBehind = decrement_day(format_date(times['startDate']))
    hardEnd = format_date(times['endDate']).replace('-', '') + 'T000000Z'
    endTime = dayBehind + 'T' + format_time(times['endTime'])
    startTime = dayBehind + 'T' + format_time(times['beginTime'])

    location = '{} ({}) {}, {}'.format(times['buildingDescription'], 
            times['building'], times['room'], UCR)

    course_info = course['subject'] + '-' + course['courseNumber'] + '-' + \
            course['sequenceNumber'] + ' - ' + course['courseTitle'].title()

    other_info = 'Instructor: ' + get_instructor(course['faculty'])[0] + '\n' + \
            'Instructor email: ' + get_instructor(course['faculty'])[1] + \
            '\n' + course['scheduleDescription']

    event = {
            'summary' : course_info,
            'location' : location,
            'description' : other_info,
            'start' : {
                'dateTime' : startTime,
                'timeZone': timeZone,
                },
            'end': {
                'dateTime' : endTime,
                'timeZone': timeZone,
                },
            'recurrence' : [
                'RRULE:FREQ=WEEKLY;UNTIL=' + hardEnd + ';BYDAY=' + \
                        get_days(times)
                ],
            # 'attendees' : [
            #     ],
            # 'reminders' : {
            #     'useDefault' : False,
            #     'overrides' : [
            #         {'method' : 'popup', 'minutes' : 10},
            #         ],
            #     },
            }
    return event

def import_to_gcal(calendar, events):
    """
    Imports a courses object into Google Calendar using gcal.py

    Args:
        events (obj): the events to import.
    """

    calendar_list = gcal.get_calendar_list()
    calendars = gcal.calendar_exists(calendar=calendar, 
            calendarList=calendar_list)
    if calendars:
        for cal_id in gcal.calendar_exists(calendar=calendar, 
                calendarList=calendar_list):
            while True:
                confirm = input('{} calendar exists, id: {}. Delete? (y/n)'
                        .format(calendar, cal_id))
                if confirm.lower() == 'n':
                    print('Okay. Please resolve the conflict and try ' + \
                            'again.')
                    exit(1)
                elif confirm.lower() == 'y':
                    print('Deleting {}'.format(calendar))
                    gcal.delete_calendar(calendar=cal_id)
                    break;
    cal = gcal.create_calendar(calendar=calendar, 
            calendarList=calendar_list)
    print('Calendar created, id: {}'.format(cal['id']))

    for course in events:
        if course['meetingTimes'][0]['beginTime']:
            # Course has a valid start time
            class_event = course_to_event(course)
            print('Adding {} to {} calendar'.format(class_event['summary'], 
                calendar))
            event = gcal.create_calendar_event(calendar=cal['id'],event=class_event)

            # Delete first (dummy) instance of course
            clean_up_events(calendar=cal['id'], event=event['id'], 
                    capDate=class_event['start']['dateTime'])
        elif course['instructionalMethodDescription'].lower() == 'online':
            # Check if course is online
            class_event = course_to_event(course)
            print('CAUTION! {} is ONLINE, skipping calendar'.format(
                class_event['summary']))

def clean_up_events(calendar, event, capDate):
    """
    Deletes the first instance of an event on calendar for a date. This is 
    mostly a band-aid for some glitch that causes recurring events to also be 
    inserted on the day the recurrence begins.

    Args:
        calendar (string):  calendar to nuke
        event   (string);   event id to look for
        capDate (string):   date to nuke all events off
    """

    # Get all instances of the given course
    instances = gcal.get_event_instances(calendar=calendar, event=event)
    
    for instance in instances['items']:
        # Double check that the we have the correct date
        if instance['start']['dateTime'][:10] == capDate[:10]:
            gcal.delete_calendar_event(calendar=calendar, event=instance['id'])
            break

def main():
    """
    Prompts the user for a schedule of registered classes to retrieve and adds 
    it to their Google Calendar.
    """

    try:
        quarter,year = app.get_user_input()
        term = '_{}{}'.format(year, quarter)
        class_schedule = '{} {}'.format(quarter, year)

        if app.CACHED:
            cache = app.get_cached(term)
            print('Schedule as of {}'.format(cache['dumpDate']))

        else:
            get_schedule(quarter, year)

        cached_data = app.json.loads(app.get_cached(term)['data'])
        courses = cached_data['data']['registrations']

        # Check that we have received something worthwhile
        if len(courses) > 0:
            print('\n{} Schedule:'.format(class_schedule))

            # print_course_info(courses[7]) # print the first course only
            # pprint(course_to_event(courses[7]))
            # test_course = [courses[7]]
            # import_to_gcal(calendar=class_schedule, events=test_course)
            # for course in courses:
            #     print_course_info(course) # print raw course info (debug)

            import_to_gcal(calendar=class_schedule, events=courses)
            print('All Done!')
        else:
            print('Oops, that schedule is not available!')
    # Catch a ctrl+c interrupt and print an exit message
    except KeyboardInterrupt:
        print('\nBye Felicia!')
        quit()

if __name__ == "__main__":
    app.print_greeting(app_name, version)
    main()
