#!/usr/bin/env python3
import csv

with open("roster_clean_complete.csv", "r") as s_l:
    students = [tuple(s) for s in csv.reader(s_l)][3:]
with open("left.csv", "r") as l:
    lefty = set([tuple(s)[3].lower() for s in csv.reader(l)][2:])
print(lefty)
with open("lefty_roster.csv", "w+") as l_s:
    output = csv.writer(l_s)
    for student in students:
        if student[2] in lefty:
            output.writerow(student)
