seatingcharts
=============

Randomized Seating Chart Generator
See https://github.com/cs3157/seatingcharts 

Originally written by Chris Mulligan (clm2186) for COMS W3157 Advanced Programming. 

This python script takes a class roster, classroom layout, and some helper files to produce a random set of seating assignments. The best documentation may be comments in the script itself.

Note, there two types of files: files about seats are tab/whitespace separated. Files with student info are CSVs. This is because I'm dumb.

In general the script works by:
 1. Reading in a layout for a classroom
 2. reading in (an) ordered list(s) of seats from a classroom.
 3. Reading in (a) list(s) of students.
 4. Shuffling the list of students.
 5. Assigning students to seats in the order listed in the the ordered list of seats
 6. Outputting a CSV of assigned seats, an HTML of the seats, and a nice HTML visualization of the seating chart. 
 7. (Optionally) email students their assignment directly


How To Use
==========

 * Go to Courseworks, Import Grades, Download Template as CSV -- this is our list of students
 * Go to Courseworks, Roster, Print as Single Column. Do a Chrome, "Save as Webpage Complete" to save it to Roster Pictures.html (this also saves students pictures to a subdirectory)
 * Edit seatingchart.py to configure:
   * SEATS_IN_ORDER_LIST to be a list of all the ORDERED seats (ie pupin301_ordered.txt). This file is actually pretty forgiving -- it can have repeats, doesn’t care about newlines or tabs or spaces, etc. Other punctuation will probably cause problems.
   * STUDENT_LIST_LIST to be a list of all the csv files you want to do (in case it’s mixed exam seating). 
   * Set ASSIGN_FIRST and ASSIGN_LAST, if you want it, so you can control seating assignments for certain people. I've typically used it to ASSIGN_FIRST those we want to give a very specific seat to, like those who need special accomodations or we want to keep an eye on. ASSIGN_LAST I often use for students who are unlikely to arrive (eg if they're likely to do a makeup or ODS accomodation), but we want to assign a seat in case they do come, this just helps make sure the good seats aren't then left open. 
 * Set LAYOUT to be the layout of the classroom, ie (pupin301.txt). *this is best edited in Excel or similar, where the whitespace/grid is easiest to see*
 * Run seatingchart.py (no arguments, just configure the stuff at the top of seatingchart)

It will output:
 * assigned_seats.csv (will be fed to mail.py)
 * assigned_seats.html -- uni ordered list of suitable for printing (firefox prints best)
 * assigned_seats_chart.html -- this is the seating assignments in a table, where each student is placed in their assigned seat according to the layout + assignments. this should be printed in firefox with “Ignore scaling and shrink to page width”

You can then use mail.py to send individual emails to students with their seat assignment (edit to change subject/message)


