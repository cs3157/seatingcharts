
# coding: utf-8

# In[40]:

# This "tool" takes 3 inputs:
# 1) a list of seats, in order of preference, with optionally ignored blank lines and repeats allowed
#    basically tab/newline separated, with no difference between them
SEATS_IN_ORDER_LIST = ["pupin301_ordered.txt"]

# 2) a CSV list of students, one per line. assumed that the key is the first column, name second. 
# ie what you get if you download a gradebook from courseworks
STUDENT_LIST_LIST = ["roster_3157.csv"]

# two lists, of students to assign first and last
ASSIGN_FIRST = "assign_first.txt"
ASSIGN_LAST = "assign_last.txt"

# 3) a HTML page matching the courseworks print as single column roster feature, with student pictures
ROSTER_PAGE = "Roster Pictures.html"

# 4) a tsv file containing the format of the room
LAYOUT = "pupin301.txt"


##outputs:
# a CSV student id ordered list of assigned seats
OUTPUT_CSV = "assigned_seats.csv"

# a pretty HTML version of uni <->seats
OUTPUT_HTML = "assigned_seats.html"

# an html page with seat, student, and photo
OUTPUT_CHART = "assigned_seats_chart.html"


# In[41]:

import pandas
import numpy
import itertools
import csv
import random
from bs4 import BeautifulSoup


# In[42]:

assignments = {}
lustudents = {}
for SEATS_IN_ORDER, STUDENT_LIST in itertools.izip(SEATS_IN_ORDER_LIST, STUDENT_LIST_LIST):
    seats = file(SEATS_IN_ORDER).readlines()
    seats = list(itertools.chain.from_iterable([z.strip().split("\t") for z in seats]))


# In[43]:

    assign_last = [x.strip() for x in open(ASSIGN_LAST).readlines()]
    assign_first = [x.strip() for x in open(ASSIGN_FIRST).readlines()]


# In[44]:

    students = [tuple(s) for s in csv.reader(open(STUDENT_LIST))][1:]
    random.shuffle(students)
    for s in students:
        lustudents[s[0]] = s

    reassign = [x for x in students if x[0] in assign_last]
    for x in reassign:
        students.remove(x)
    students.extend(reassign)
    students.reverse()

    reassign = [x for x in students if x[0] in assign_first]
    for x in reassign:
        students.remove(x)
    students.extend(reassign)



# In[45]:

    for seat in seats:
        if seat and seat not in assignments:
            try:
                assignments[seat] = students.pop()
            except:
                break
            print "assigned", assignments[seat], "to", seat
    print "Leaving unassigned:", students


# In[46]:

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
            </style>
    <body><div class="assignments">\n\n""")
    for seat, student in sorted(assignments.iteritems(), key=lambda x: x[1]):
        html.write("""<div><span class="uni">%s</span> <span class="seat">%s</span></div>"""
                   % (student[0], seat))
    html.write("""</div></body>\n""")


# In[47]:

print len(assignments)
print len(set(seats))

output = csv.writer(open(OUTPUT_CSV, "w"))
for seat, uni in assignments.iteritems():
    output.writerow(list(uni)[:2] + [seat])


# In[48]:

soup = BeautifulSoup(open(ROSTER_PAGE))


# In[49]:

photos = {}
for img in soup.findAll(class_="rosterImage"):
    url = img["src"]
    uni = img.findParent().findNextSibling().findNextSibling().string
    photos[uni] = url


# In[50]:

room = [s for s in csv.reader(open(LAYOUT), delimiter="\t")]
maxrow = max([len(x) for x in room])


# In[51]:

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

            
            



