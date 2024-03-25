# seatingcharts

A collection of scripts to produce a randomized set of seating assignments.


## Scripts

* `seatingchart.py` - The core of this toolset. Creates seating assignments for a single room and produces HTML output. Originally written by Chris Mulligan (clm2186) for COMS W3157 Advanced Programming.
* `go_brr.py` - Splits a larger roster into sub-rosters, one per room, and calls `seatingchart.py` for each one. Written by XXXurxo.
* `mail.py` - Sends individual seating assignments to students by email
* `imagedl.py` - Downloads students' photos. Written by Carl.
* `rosters.py` - Downloads the student roster from Canvas. It is also used by other scripts to parse roster csv files. Writen by Carl.

## Usage

1. Download the roster CSV file. This can either be done manually by going into the 'Grades' tab on Courseworks and selecting Export > Export Entire Gradebook or by using `rosters.py --download roster_filename.csv` (this requires a Canvas API key)

2. Download the student images from the 'Photo Roster' tab. This can be achieved either with a browser extension, by using the "Save page as" functionality, or running the `imagedl.py` script.

3. If necessary, edit the `rooms` file (see 'Room format' below)

4. Run `./go_brr.py rooms roster_filename.csv`

5. Profit! The output can be found in `out/` and will also be placed in `~/html/seating/`

## Room format

### rooms file
This is the file passed to `go_brr.py`. It follows the following format
```
room1name room1seatcount
room2name room2seatcount
...
```
For each room, the `layouts` directory must contain two additional files:
1. The visual layout file, `room1name.txt`
This file determines the general layout of a room as it will be reflected on the HTML seating chart. Seats must be separated by a TAB character
```
SEAT1	SEAT2	SEAT3		SEAT4	SEAT5	SEAT6
SEAT7	SEAT8	SEAT9		SEAT10	SEAT11	SEAT12
...
```

2. The fill order file, `room1name_ordered.txt`
This file determines in what order to fill seats. Exact semantics don't matter much (i.e. spaces, tabs and line breaks are functionally identical) though lines starting with hash (#) symbols will be ignored.

## Additional features (not yet available with go_brr.py)
*   Lefty roster
    -   Ensure that your classroom has a `<classroom>_lefty_ordered.txt` file.
    -   Move lefties from `roster_<slug>.csv` to a new file called
        `left_roster_<slug>.csv`. This file follows the same format as the normal roster.
    -   Run `seatingcharts.py` with the `-l` flag.

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


### Emailing students their seating assignments

You can now use mail.py to send individual emails to students with their seat assignment.

* If you haven't already, [generate a new device password](https://uniapp.cc.columbia.edu/acctmanage/devicepass). Note that this will invalidate your existing sessions, so you will need to sign in again.
* `export LIONMAIL_DEVICE_PASS="abcdefg"`
* In Google account settings, [allow less secure apps](https://cuit.columbia.edu/lionmail-allow-less-secure-apps). "Less secure" is their terminology for IMAP/SMTP clients.
* Change the name and email in the script.


### Adding support for new classrooms

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
