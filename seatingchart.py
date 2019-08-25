#!/usr/bin/env python2

"""
Seating Chart script. See https://github.com/cs3157/seatingcharts
"""

import argparse
import itertools
import csv
import os
import random
import sys


def assert_file_exists(path):
    if not os.path.isfile(path):
        print("Missing required file: {}".format(path))
        exit(1)


def working_dir_path(name, slug, extension):
    """
    generates paths in the format:
    out/3157-2017-9-final/roster_3157-2017-9-final.html
    """
    filename = "{}_{}.{}".format(name, slug, extension)
    return os.path.join("out", slug, filename)


parser = argparse.ArgumentParser(
        description="Generate a seating chart based on the course roster")

parser.add_argument("slug",
        type=str,
        help="the \"out\" subdirectory to use as the working directory",
        metavar='<working-directory>')

parser.add_argument("layout",
        type=str,
        help="the seating chart layout (classroom name) to use",
        metavar="<layout>")

parser.add_argument("-t", "--title",
        default=None, type=str,
        help="human-readable name that will be written the top of seating chart",
        metavar="<title>")

parser.add_argument("-d", "--debug",
        action="store_true",
        help="print debug messages")

args = parser.parse_args()


# 1) a list of seats, in order of preference, with optionally ignored blank lines and repeats allowed
#    basically tab/newline separated, with no difference between them
layout_ordered_path = os.path.join("layouts", args.layout + "_ordered.txt")
SEATS_IN_ORDER_LIST = [ layout_ordered_path ]

# 2) a CSV list of students, one per line. assumed that the key is the first column, name second.
# ie what you get if you download a gradebook from courseworks
roster_text_path = working_dir_path("roster", args.slug, "csv")
assert_file_exists(roster_text_path)
STUDENT_LIST_LIST = [ roster_text_path ]

# two lists, of students to assign first and last
assign_first_path = working_dir_path("assign-first", args.slug, "txt")
assign_last_path  = working_dir_path("assign-last",  args.slug, "txt")

ASSIGN_FIRST = assign_first_path if os.path.isfile(assign_first_path) else "/dev/null"
ASSIGN_LAST  = assign_last_path  if os.path.isfile(assign_last_path)  else "/dev/null"

photos_path = os.path.join("out", args.slug, args.slug + "_files")

# 3) a tsv file containing the format of the room
layout_path = os.path.join("layouts", args.layout + ".txt")
assert_file_exists(layout_path)
LAYOUT = layout_path

# outputs:
NAME = args.title if args.title != None else "{} Seating".format(args.slug)

# a CSV student id ordered list of assigned seats
OUTPUT_CSV = working_dir_path("list", args.slug, "csv")

# a pretty HTML version of uni <-> seats
OUTPUT_HTML = working_dir_path("list", args.slug, "html")

# an html page with seat, student, and photo
OUTPUT_CHART = working_dir_path("map", args.slug, "html")

# Now we're ready to assign seats
assignments = {}

for SEATS_IN_ORDER, STUDENT_LIST in itertools.izip(SEATS_IN_ORDER_LIST, STUDENT_LIST_LIST):
    seats = file(SEATS_IN_ORDER).readlines()
    seats = [s for s in seats if s[0] != '#']  # Strip comments
    seats = list(itertools.chain.from_iterable([z.strip().split() for z in seats]))

    assign_last = [x.strip() for x in open(ASSIGN_LAST).readlines()]
    assign_first = [x.strip() for x in open(ASSIGN_FIRST).readlines()]

    students = [tuple(s) for s in csv.reader(open(STUDENT_LIST))][2:]  # Skip two header rows
    random.shuffle(students)

    # the assign_first/last students are shuffled randomly, so we need to pull them to the front/back
    reassign = [x for x in students if x[0] in assign_last]
    for x in reassign:
        students.remove(x)
    students.extend(reassign)
    students.reverse()

    reassign = [x for x in students if x[0] in assign_first]
    for x in reassign:
        students.remove(x)
    students.extend(reassign)

    # now loop over ordered seats assigning students
    for seat in seats:
        if seat and seat not in assignments:
            try:
                assignments[seat] = students.pop()
            except:
                break
            if args.debug:
                print "assigned", assignments[seat], "to", seat
    if students:
        print "WARNING: unassigned students", students


# Write out the HTML roster
with open(OUTPUT_HTML, "w") as html:
    html.write("""<style>
            .seat {
                padding-left: 1em;
                margin-bottom: .2em;
            }
            .name {
                font-size: 9pt;
            }
            .assignments {
                -webkit-column-count: 4; /* Chrome, Safari, Opera */
                -moz-column-count: 4; /* Firefox */
                column-count: 4;
            }
            h3 {
                text-align: center;
            }
            </style>
    <body>
    <h3>%s</h3>
    <div class="assignments">\n\n""" % NAME)
    for seat, student in sorted(assignments.iteritems(), key=lambda x: x[1][2]):  # sort by uni
        html.write("""<div><span class="uni">%s</span> <span class="seat">%s</span></div>"""
                   % (student[2], seat))
    html.write("""</div></body>\n""")



# dump to CSV as well
output = csv.writer(open(OUTPUT_CSV, "w"))
for seat, uni in assignments.iteritems():
    output.writerow(list(uni)[:2] + [seat])


# Write the chart
room = [s for s in csv.reader(open(LAYOUT), delimiter="\t")]
maxrow = max([len(x) for x in room])

with open(OUTPUT_CHART, "w") as html:
    html.write("""<style>
            table {
                table-layout: fixed;
                width: 100%;
            }
            img {
                width: 60px;
                vertical-align: text-bottom;
            }
            .seat {
                font-weight: bold;
                font-size: 14pt;
                vertical-align: top;
            }
            .name {
                font-size: 9pt;
            }
            td {
                text-align: center;
                vertical-align: baseline;
                width: 70px;
            }
            </style>
    <body><table border=1>\n\n""")
    for row in room:
        html.write("<tr>")
        row_count = 0

        for seat in row:
            row_count = row_count + 1
            html.write("<td>\n")

            try:
                student = assignments[seat]
                uni = student[2]
                name = student[0]
                img_path = os.path.join(photos_path, uni + ".jpg")  # Used to check if file exists
                img_rel_path = os.path.join(args.slug + "_files", uni + ".jpg")  # Inserted into HTML
                if os.path.isfile(img_path):
                    html.write("""<span class="seat">%s</span><br> %s<br> <span class="name">%s</span><br> <img src="%s">"""
                           % (seat, uni, name, img_rel_path))
                else:
                    print "WARNING: no img found for %s" % (uni)
                    html.write("""<span class="seat">%s</span><br> %s<br> <span class="name">%s</span><br> """
                           % (seat, uni, name))
            except KeyError:
                html.write("""<span class="seat">%s</span>""" % (seat))
            html.write("</td>\n")

        for i in range(maxrow - row_count):
            html.write("<td></td>\n")

        html.write("</tr>\n\n")
    html.write("</table></body>")
