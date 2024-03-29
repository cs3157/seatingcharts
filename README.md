seatingcharts
=============

Originally written by Chris Mulligan (clm2186) for COMS W3157 Advanced Programming.

This python script takes a class roster, classroom layout, and some helper files to produce a random set of seating assignments. The best documentation may be comments in the script itself.


Usage
-----
Update 10/2/2022:
Thing's changed! We regularly get a huge class size (over 300 students.) So XXXurxo wrote a helper script to handle multiple rooms in one shot; here is how to use it:

1. Download the roster from the Grades tab of courseworks; save it as roster.csv, which contains three columns: Student ID, Student Name, and blank. NO HEADER!!!!! (see sample_roster.csv)

2. Download all the images from the photo roster in coursworks by chrome extensions, and save them in the images folder

3. modify the rooms file in this format: 
	<p>[layout-1] [number of students]</p>
	<p>[layout-2] [number of students]</p>
	(see sample_room)

4. run python3 go_brr.py rooms roster.csv

You can find the output in the out folder :)

### ### ### ### ### ### ### ### ### ### ### ### 
### Downloading the input files

For sample inputs, see the `out/demo/` directory.

*   In the `out` directory, create a working directory for storing files related
    to this exam.
    -   Example: `3157-2017-9-001_final`
    -   This string is the _slug_ for this exam.

*   Log into [CourseWorks](https://courseworks2.columbia.edu/) using Chrome
    or Firefox.

*   Find your class site.

*   Student roster
    -   Go to Grades > Export > CSV File.
    -   Move this file to the working directory.
    -   Rename it `roster_<slug>.csv`.

*   (Optional) Lefty roster
    -   Ensure that your classroom has a `<classroom>_lefty_ordered.txt` file.
    -   Move lefties from `roster_<slug>.csv` to a new file called
        `left_roster_<slug>.csv`. This file follows the same format as the normal roster.
    -   Run `seatingcharts.py` with the `-l` flag.

*   Photo roster
    -   Go to Photo Roster in the menu on the left and wait a minute.
    -   On Chrome, use File > Save Page As. In the Format drop-down, select
        "Web Page, complete".
    -   On Firefox, right-click inside the Photo Roster panel and select
        This Frame > Save Frame As. In the Format drop-down, select "Web Page,
        complete".
    -   Navigate to your working directory, name the file `<slug>.html`
        and press Save.
    -   You should now have an HTML page and a directory of files with all
        students' photos, along with some miscellaneous JS files. You do not
        need to delete the extra cruft.

*   If you want to put some students in the front/back of the classroom, also
    create files named `assign-first_<slug>.txt` and `assign-last_<slug>.txt`.
    -   Files should contain newline-separated lists of UNIs.
    -   `assign_first` can be used for students who need special accomodations,
        or those we want to keep an eye on.
    -   `assign_last` can be used for students who are unlikely to arrive, such
        as students with Office of Disability Services accomodations or some
        other reason to be absent.


### Running the `seatingchart.py` script

The usage of the command is as follows:

    usage: seatingchart.py [-h] [-t <title>] [-l] [-d] <slug> <layout>

    Generate a seating chart based on the course roster

    positional arguments:
      <slug>                the "out" subdirectory to use as the working directory
      <layout>              the seating chart layout (classroom name) to use

    optional arguments:
      -h, --help            show this help message and exit
      -t <title>, --title <title>
                            human-readable name that will be written the top of
                            seating chart
      -l, --lefty           assign seats to lefty students
      -d, --debug           print debug messages

Here are some examples:

    ./seatingchart.py demo pupin301
    ./seatingchart.py 3157-2017-9-002_m1 noco501 --title "3157-2017-9-002 Midterm 1"

Once the script runs, it will output:

*   `list_<slug>.html`: A nicely formatted list of students and seats that you can
    print and bring to the exam.

*   `chart_<slug>.html`: A map generated from the layout and assignments. Each box
    contains the student's name, seat number, and photo.
    -   Since the page can be very wide, this is best viewed in a browser.
    -   Use this to verify that students are sitting in their assigned seats.

*   `list_<slug>.csv`: A list of students and seats that can be fed into
    `mail.py`.


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

To create a new classroom layout, you need to make three files:

1.  `<classroom>.txt`, which specifies the layout of the room.
    -   This is best edited in Excel, where the grid is easier to see.

2.  `<classroom>_ordered.txt`, which specifies the order in which the script
    should fill seats.
    -   You can create this file by copying and rearranging the layout file.
    -   This file is pretty forgiving: it can have repeats and accepts any type
        of whitespace (newline, tabs, and spaces).
    -   For a strategy to determine the order, see commit
        [01d796c](https://github.com/cs3157/seatingcharts/commit/01d796ca3ed805d97b72be7f9024b3cd6564430f)
3.  `<classroom>_lefty_ordered.txt`, which specifies the order in which the script
    shouild fill lefty seats.
