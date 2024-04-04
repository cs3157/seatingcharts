#!/usr/bin/env python3

import argparse
import csv
import os
import re
import requests
from getpass import getpass
from pathlib import Path

# ANSI color codes
GREEN = "\033[01;92m"
RED = "\033[01;91m"
END = "\033[0m"

def download_roster(course_id, canvas_api_key):
    response = requests.get(f'https://courseworks2.columbia.edu/api/v1/courses/{course_id}/students',
            headers={'Authorization': f'Bearer {canvas_api_key}'}).json()

    # Courseworks has a fake student called "Test Student" that we ignore here so as not to include
    # it in the roster
    response = [x for x in response if x['sortable_name'] != 'Student, Test']

    return [(user['login_id'], user['sortable_name']) for user in response]

# Turns ('abc', 'def', '') into ('abc','def')
def discard_last_if_empty(elements):
    if len(elements) == 0 or len(elements[-1]) > 0:
        return elements
    else:
        return elements[:-1]


def load_roster(csv_file_path):
    print(f"[rosters] Loading {csv_file_path}")
    csv_file_path = Path(csv_file_path) # Won't do anything if csv_file_path is already a Path

    with csv_file_path.open(newline='') as csvfile:
        return [(row['SIS Login ID'], row['Student']) for row in csv.DictReader(csvfile)
            if len(row['SIS Login ID']) > 0 and row['Student'] != 'Student, Test'] 

def save_roster(students, csv_file_path):
    csv_file_path = Path(csv_file_path)

    with csv_file_path.open('w') as f:
        # Write the header followed by the students
        csv.writer(f).writerows([('SIS Login ID', 'Student')] + students)

def print_table(students):
    # Store the maximum length of each column
    max_widths = [max(len(str(item)) for item in column) for column in zip(*students)]

    # Print the table header
    print("+" + "+".join(["-" * (width + 2) for width in max_widths]) + "+")
    print("|" + "|".join([f" {header:<{max_widths[i]}} " for i, header in enumerate(["UNI", "Name"])]) + "|")
    print("+" + "+".join(["-" * (width + 2) for width in max_widths]) + "+")

    # Print the rows
    for row in students:
        print("|" + "|".join([f" {str(item):<{max_widths[i]}} " for i, item in enumerate(row)]) + "|")
    
    # Close the table
    print("+" + "+".join(["-" * (width + 2) for width in max_widths]) + "+")

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
            save_roster(students, args.download)
            print(f"{GREEN}Roster saved successfully. (Found {len(students)} students){END}")
        except KeyboardInterrupt:
            print(f"{RED}Download cancelled.{END}")
        except Exception:
            print(f"{RED}Failed to download roster. Please check your API key and course ID{END}")

    if args.read:
        students = load_roster(args.read)
        print_table(students)
        print("Student count:", len(students))

    if args.read is None and args.download is None:
        print("No action specified.")
