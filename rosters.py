import argparse
import csv
import re

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
        if 'SIS Login ID' in first_line:
            reader = csv.DictReader(csvfile)
            return list(
                        map(lambda row: (row['SIS Login ID'], row['Student']),
                            filter(lambda row: len(row['SIS Login ID']) > 0 and row['Student'] != 'Student, Test',
                               reader
                            )
                        )
                    )
        else:
            students = list(map(tuple, map(discard_last_if_empty, csv.reader(csvfile))))

            for student in students:
                if len(student) != 2:
                    raise Exception(f"Invalid row format: {student}")

            return students

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Load Canvas generated student rosters")

    parser.add_argument("--read",
                        type=str,
                        required=True,
                        metavar='<file_path>')

    args = parser.parse_args()
    
    students = load_roster(args.read)
    print(students)
    print("Student count:", len(students))
