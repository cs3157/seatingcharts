seatingcharts
=============

Randomized Seating Chart Generator
See https://github.com/cs3157/seatingcharts

Originally written by Chris Mulligan (clm2186) for COMS W3157 Advanced Programming.

This python script takes a class roster, classroom layout, and some helper files to produce a random set of seating assignments. The best documentation may be comments in the script itself. The only non-standard requirement is beautifulsoup4.


Usage
-----

### Downloading the input files

For sample inputs, see the `out/demo/` directory.

*   In the `out` directory, create a working directory for storing files related
    to this exam.
    -   Example: `3157-2017-9-001_final`
    -   This string is the _slug_ for this exam.

*   Log into [Old CourseWorks](https://courseworks.columbia.edu/) using Chrome
    or Firefox.

*   Find your class site by navigating to a URL in the format of
    `https://courseworks.columbia.edu/portal/site/COMSW3157_001_2016_3/`

*   Text roster
    -   Go to Gradebook > Import Grades > Download Template as CSV.
    -   Move this file to the working directory.
    -   Rename it `roster_your-slug.csv`.

*   Photo roster
    -   Go to Roster > Print as Single Column. Cancel the print dialog.
    -   Use File > Save Page As. In the Format drop-down, select "Web Page,
        complete".
    -   Navigate to your working directory.
    -   Name the file `roster_your-slug.html` and press Save. (This will also
        create a directory to store the photos.)

*   If you want to put some students in the front/back of the classroom, also
    create files named `assign-first_slug.txt` and `assign-last_slug.txt`.
    -   Files should contain newline-separated lists of UNIs.
    -   `assign_first` can be used for students who need special accomodations,
        or those we want to keep an eye on.
    -   `assign_last` can be used for students who are unlikely to arrive, such
        as students with Office of Disability Services accomodations or some
        other reason to be absent.


### Running the `seatingchart.py` script

The usage of the command is as follows:

    usage: seatingchart.py [-h] [-t <title>] <working-directory> <layout>

    Generate a seating chart based on the course roster

    positional arguments:
      <working-directory>   the "out" subdirectory to use as the working directory
      <layout>              the seating chart layout (classroom name) to use

    optional arguments:
      -h, --help            show this help message and exit
      -t <title>, --title <title>
                            human-readable name that will be written the top of
                            seating chart

Here are some examples:

    ./seatingchart.py demo pupin301
    ./seatingchart.py 3157-2017-9-002_m1 noco501 --title "3157-2017-9-002 Midterm 1"

Once the script runs, it will output:

*   `list_slug.csv`: A list of students and seats that can be fed into
    `mail.py`.

*   `list_slug.html`: A nicely formatted list of students and seats that you can
    print and bring to the exam.

*   `map_slug.html`: A map generated from the layout and assignments. Each box
    contains the student's name, seat number, and photo.
    -   Since the page can be very wide, this is best viewed in a browser.
    -   Use this to verify that students are sitting in their assigned seats.


Emailing students their seating assignments
-------------------------------------------

You can now use mail.py to send individual emails to students with their seat assignment.

* If you haven't already, [generate a new device password](https://uniapp.cc.columbia.edu/acctmanage/devicepass). Note that this will invalidate your existing sessions, so you will need to sign in again.
* `export LIONMAIL_DEVICE_PASS="abcdefg"`
* In Google account settings, [allow less secure apps](https://cuit.columbia.edu/lionmail-allow-less-secure-apps). "Less secure" is their terminology for IMAP/SMTP clients.
* Change the name and email in the script.


Adding support for new classrooms
---------------------------------

In general, the script works by:

*   Reading in a layout for a classroom
*   Reading in (an) ordered list(s) of seats from a classroom
*   Reading in (a) list(s) of students
*   Shuffling the list of students
*   Assigning students to seats in the order listed in the the ordered list of seats
*   Outputting a CSV of assigned seats, an HTML of the seats, and a nice HTML visualization of the seating chart

To create a new classroom layout, you need to make two files:

1.  `classroomname.txt`, which specifies the layout of the room.
    -   This is best edited in Excel, where the grid is easier to see.

2.  `classroomname_ordered.txt`, which specifies the order in which the script
    should fill seats.
    -   You can create this file by copying and rearranging the layout file.
    -   This file is pretty forgiving: it can have repeats and accepts any type
        of whitespace (newline, tabs, and spaces).
    -   Don't include leftie desks. It's easier to leave all of them open for
        left-handed students to move into, rather than figuring out who all
        the lefties are.
    -   For a strategy to determine the order, see commit
        [01d796c](https://github.com/cs3157/seatingcharts/commit/01d796ca3ed805d97b72be7f9024b3cd6564430f)
