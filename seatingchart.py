"""
Seating Chart script. See https://github.com/cs3157/seatingcharts
"""

# 1) a list of seats, in order of preference, with optionally ignored blank lines and repeats allowed
#    basically tab/newline separated, with no difference between them
SEATS_IN_ORDER_LIST = ["pupin301_ordered.txt"]

# 2) a CSV list of students, one per line. assumed that the key is the first column, name second. 
# ie what you get if you download a gradebook from courseworks
STUDENT_LIST_LIST = ["roster_demo.csv"]

# two lists, of students to assign first and last
ASSIGN_FIRST = "assign_first.demo.txt"
ASSIGN_LAST = "assign_last.demo.txt"

# 3) a HTML page matching the courseworks print as single column roster feature, with student pictures
ROSTER_PAGE = "Roster Pictures.demo.html"

# 4) a tsv file containing the format of the room
LAYOUT = "pupin301.txt"


##outputs:
NAME = "3157 Exam"

# a CSV student id ordered list of assigned seats
OUTPUT_CSV = "assigned_seats.demo.csv"

# a pretty HTML version of uni <->seats
OUTPUT_HTML = "assigned_seats.demo.html"

# an html page with seat, student, and photo
OUTPUT_CHART = "assigned_seats_chart.demo.html"


import itertools
import csv
import random
from bs4 import BeautifulSoup


assignments = {}
lustudents = {}
for SEATS_IN_ORDER, STUDENT_LIST in itertools.izip(SEATS_IN_ORDER_LIST, STUDENT_LIST_LIST):
    seats = file(SEATS_IN_ORDER).readlines()
    seats = list(itertools.chain.from_iterable([z.strip().split("\t") for z in seats]))

    assign_last = [x.strip() for x in open(ASSIGN_LAST).readlines()]
    assign_first = [x.strip() for x in open(ASSIGN_FIRST).readlines()]


    students = [tuple(s) for s in csv.reader(open(STUDENT_LIST))][1:]
    random.shuffle(students)
    for s in students:
        lustudents[s[0]] = s

    #the assign_first/last students are shuffled randomly, so we need to pull them to the front/back
    reassign = [x for x in students if x[0] in assign_last]
    for x in reassign:
        students.remove(x)
    students.extend(reassign)
    students.reverse() #i know, i know

    reassign = [x for x in students if x[0] in assign_first]
    for x in reassign:
        students.remove(x)
    students.extend(reassign)

    #now loop over ordered seats until we run out of students
    for seat in seats:
        if seat and seat not in assignments:
            try:
                assignments[seat] = students.pop()
            except:
                break
            print "assigned", assignments[seat], "to", seat
    print "Leaving unassigned:", students


#Write out the HTML roster
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
    for seat, student in sorted(assignments.iteritems(), key=lambda x: x[1]):
        html.write("""<div><span class="uni">%s</span> <span class="seat">%s</span></div>"""
                   % (student[0], seat))
    html.write("""</div></body>\n""")


print len(assignments)
print len(set(seats))

#dump to CSV as well
output = csv.writer(open(OUTPUT_CSV, "w"))
for seat, uni in assignments.iteritems():
    output.writerow(list(uni)[:2] + [seat])


#Load picture files
soup = BeautifulSoup(open(ROSTER_PAGE))
photos = {}
for img in soup.findAll(class_="rosterImage"):
    url = img["src"]
    uni = img.findParent().findNextSibling().findNextSibling().string
    photos[uni] = url



#Write the chart
room = [s for s in csv.reader(open(LAYOUT), delimiter="\t")]
maxrow = max([len(x) for x in room])

with open(OUTPUT_CHART, "w") as html:
    html.write("""<style>
            img {
                width: 60px;
                vertical-align: text-bottom;
                
            }
            .seat {
                font-weight: bold;
                font-size: 14pt;
                                vetical-align: top;
            } 
            .name {
                font-size: 9pt;
            }
            td {
                text-align: center;
                vertical-align: baseline;
            }
            </style>
    <body><table border=1>\n\n""")
    for row in room:
        html.write("<tr>")
        for seat in row:
            html.write("<td>\n")
            try:
                student = assignments[seat]
                uni = student[0]
                name = student[1]
                try:
                    photo = photos[uni]
                    html.write("""<span class="seat">%s</span><br> %s<br> <span class="name">%s</span><br> <img src="%s">"""
                           % (seat, uni, name, photo))
                except KeyError:
                    html.write("""<span class="seat">%s</span><br> %s<br> <span class="name">%s</span><br> """
                           % (seat, uni, name))
            except KeyError:
                html.write("""<span class="seat">%s</span>""" % (seat))
            html.write("</td>\n")
        html.write("</tr>\n\n")
    html.write("</table></body>")

            
            



