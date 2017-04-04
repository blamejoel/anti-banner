#!/usr/bin/env python3
"""
    main.py
    Author: Joel Gomez
    Date created: 2017/04/04
    Python Version 3.5.2

    Simple menu interface for anti-banner functions
"""
from anti_banner import print_greeting
from anti_banner import args
from grades import main as grades
from add_to_gcal import main as gcal
from sys import exit

options = [
        'Check grades', 
        'Add schedule to Google Calendar'
        ]

def main():
    print_greeting('', '1.5')

    while True:
        print('Select an option:\n')
        for i, option in enumerate(options):
            print('  {}. {}'.format(i+1, option))
        print('  ')
        try:
            sel = input()
        except KeyboardInterrupt:
            print('\nBye Felicia!')
            quit()

        if int(sel) >= 1 and int(sel) <= len(options):
            break
    
    if sel == '1':
        grades()
    elif sel == '2':
        gcal()

if __name__ == "__main__":
    if args['q'] is None or args['y'] is None:
        print('error: missing quarter and year arguments')
        print('usage:')
        print('./anti-banner -q [quarter] -y [year]\n')
        print('example:')
        print('./anti-banner -q winter -y 2017\n')
        exit(1)
    main()
