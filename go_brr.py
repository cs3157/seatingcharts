#!/usr/bin/env python3

import argparse
import csv
import math
import os
import random
import shutil
import traceback
from pathlib import Path

import csv2pdf

import rosters
import seatingchart

OUT_PATH = Path.cwd() / "out"
HTML_PATH = Path.home() / "html" / "seating"
HTML_IMAGES_PATH = HTML_PATH / "images"
HTML_PDF_PATH = HTML_PATH / "seat.pdf"

# ANSI color codes
GREEN = "\033[01;92m"
RED = "\033[01;91m"
END = "\033[0m"

ASCII_ART = r"""
 ________  ________          ________  ________  ________     
|\   ____\|\   __  \        |\   __  \|\   __  \|\   __  \    
\ \  \___|\ \  \|\  \       \ \  \|\ /\ \  \|\  \ \  \|\  \   
 \ \  \  __\ \  \\\  \       \ \   __  \ \   _  _\ \   _  _\  
  \ \  \|\  \ \  \\\  \       \ \  \|\  \ \  \\  \\ \  \\  \| 
   \ \_______\ \_______\       \ \_______\ \__\\ _\\ \__\\ _\ 
    \|_______|\|_______|        \|_______|\|__|\|__|\|__|\|__|
                                                              
"""

def rename_images(img_path: Path) -> None:
    for img in img_path.glob("*"):
        if img.suffix == ".jpeg":
            img.rename(img.with_suffix('.jpg'))


def create_html_directory(html_path: Path) -> None:
    # Remove the directory if it exists
    if html_path.exists():
        shutil.rmtree(HTML_PATH)

    # Create the directory
    html_path.mkdir(parents=True, exist_ok=True)
    html_path.chmod(0o755)


def init_seat_csv(seat_csv_path: Path) -> None:
    seat_csv_path.write_text("Uni,Name,Seat,Room\n")
    seat_csv_path.chmod(0o744)


def main():
    print(ASCII_ART)

    parser = argparse.ArgumentParser(description="Go brrr with the seating charts")
    parser.add_argument("rooms", type=str, metavar='<rooms_file>')
    parser.add_argument("roster", type=str, metavar='<roster_file>')
    args = parser.parse_args()

    ROOM_FILE = Path(args.rooms)

    students = rosters.load_roster(args.roster)  
    print(f"Found {len(students)} students in the roster file")

    random.shuffle(students)
    student_count = len(students)
    seat_count = 0

    rename_images(Path("images"))

    create_html_directory(HTML_PATH)

    # Create the file
    seat_csv_path = HTML_PATH / "seat.csv"
    init_seat_csv(seat_csv_path)

    with ROOM_FILE.open('r') as f:
        rooms = [r.strip().split() for r in f.readlines() if r.strip()]

    print("Rooms:")

    for room_name, count in rooms:
        print(f"- {room_name}: {count} seats")
        seat_count += int(count)
    print(f"Total seats: {seat_count}")

    student_index = 0

    for room in rooms:
        rname, rcount = room[0], room[1]
        ROOM_OUT_PATH = Path(OUT_PATH) / rname
        ROOM_ROSTER_PATH = ROOM_OUT_PATH / f"roster_{rname}.csv"
        ROOM_LIST_PATH = ROOM_OUT_PATH / f"list_{rname}.csv"
        ROOM_CHART_PATH = ROOM_OUT_PATH / f"chart_{rname}.html"
        ROOM_IMAGES_PATH = ROOM_OUT_PATH / "images"

        HTML_ROOM_PATH = HTML_PATH / f"{rname}.html"

        shutil.rmtree(ROOM_OUT_PATH, ignore_errors=True)
        ROOM_OUT_PATH.mkdir(parents=True)
        ROOM_IMAGES_PATH.symlink_to(Path("images"))

        room_students = []
        num_seats = math.ceil(student_count / seat_count * int(rcount))
        for _ in range(num_seats):
            if student_index < student_count:
                student = students[student_index]
                student_index += 1
                room_students.append(student)

        rosters.save_roster(room_students, ROOM_ROSTER_PATH)

        try:
            seatingchart.run(slug=rname, layout=rname)
        except Exception as e:
            print(traceback.format_exc())
            print(RED + "Error: seatingchart.py failed" + END)
            exit(1)

        shutil.copy(ROOM_CHART_PATH, HTML_ROOM_PATH)

        with ROOM_LIST_PATH.open('r') as list_file:
            with seat_csv_path.open('a') as seat_file:
                for line in list_file:
                    modified_line = line.strip() + f",{rname}\n"
                    seat_file.write(modified_line)

        HTML_ROOM_PATH.chmod(0o644)

    shutil.copytree("images", HTML_IMAGES_PATH)
    HTML_IMAGES_PATH.chmod(0o711)
    for img in HTML_IMAGES_PATH.glob("*.*"):
        img.chmod(0o644)

    csv2pdf.convert(seat_csv_path, HTML_PDF_PATH)
    HTML_PDF_PATH.chmod(0o644)
    seat_csv_path.unlink()

    print(GREEN + "Success!" + END)

if __name__ == "__main__":
    main()

