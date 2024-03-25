#!/usr/bin/env python3

import argparse
import csv
import os
import re
import requests
from getpass import getpass

# ANSI color codes
GREEN = "\033[01;92m"
RED = "\033[01;91m"
END = "\033[0m"

def download_roster(course_id, canvas_api_key):
    response = requests.get(f'https://courseworks2.columbia.edu/api/v1/courses/{course_id}/students',
            headers={'Authorization': f'Bearer {canvas_api_key}'}).json()

    response = [x for x in response if x['sortable_name'] != 'Student, Test']

    return [(user['login_id'], user['sortable_name']) for user in response]

# Turns ('abc', 'def', '') into ('abc','def')
def discard_last_if_empty(elements):
    if len(elements) == 0 or len(elements[-1]) > 0:
        return elements
    else:
        return elements[:-1]


def load_roster(csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        # Check if the roster has the Canvas header
        first_line = csvfile.readline()
        csvfile.seek(0) # Reset cursor
        
        # Check if the file has a Courseworks header
        if 'SIS Login ID' in first_line:
            return [(row['SIS Login ID'], row['Student']) for row in reader
                    if len(row['SIS Login ID']) > 0 and row['Student'] != 'Student, Test'] 
        else:
            students = [tuple(discard_last_if_empty(row)) for row in csv.reader(csvfile)]

            for student in students:
                if len(student) != 2:
                    raise Exception(f"Invalid row format: {student}")

            return students

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Download and parse Canvas student rosters.")

    parser.add_argument("--read",
                        type=str,
                        default=None,
                        nargs='?',
                        metavar='<file_path>')

    parser.add_argument("--download",
                        type=str,
                        default=None,
                        nargs='?',
                        metavar='<file_path>')

    args = parser.parse_args()
 
    if args.download:
        canvas_api_key = os.getenv('CANVAS_API_KEY', None)
        if canvas_api_key is None:
            print("Environment variable 'CANVAS_API_KEY' not found.")
            canvas_api_key = getpass("Please paste your Canvas API key and press ENTER: ")

        canvas_course_id = os.getenv('CANVAS_COURSE_ID', None)
        if canvas_course_id is None:
            print("Environment variable 'CANVAS_COURSE_ID' not found.")
            print("Please open the class' courseworks page and copy the numeric ID from the URL")
            canvas_course_id = input('Course ID: ')

        print("Downloading student roster...")
        
        try:
            students = download_roster(canvas_course_id, canvas_api_key)
            with open(args.download, 'w') as f:
                csv.writer(f).writerows(students)

            print(GREEN + "Roster saved successfully." + END)
        except KeyboardInterrupt:
            print(RED + "Download cancelled." + END)
        except Exception:
            print(RED + "Failed to download roster. Please check your API key and course ID" + END)

    if args.read:
        students = load_roster(args.read)
        print(students)
        print("Student count:", len(students))

    if args.read is None and args.download is None:
        print("No action specified.")
