#!/usr/bin/env python3

import argparse
import csv
import math
import os
import random
import shutil
from pathlib import Path

import csv2pdf

OUT_PATH = Path.cwd() / "out"
HTML_PATH = Path.home() / "html" / "seating"
HTML_IMAGES_PATH = HTML_PATH / "images"
HTML_PDF_PATH = HTML_PATH / "seat.pdf"

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
    parser = argparse.ArgumentParser(description="Go brrr with the seating charts")
    parser.add_argument("rooms", type=str, metavar='<rooms>')
    parser.add_argument("roster", type=str, metavar='<roster>')
    args = parser.parse_args()

    ROOM_FILE = Path(args.rooms)
    STUDENT_FILE = Path(args.roster)

    with STUDENT_FILE.open() as f:
        students = [tuple(s) for s in csv.reader(f)]

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

    print(f"Rooms: {rooms}")
    for _, count in rooms:
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

        with ROOM_ROSTER_PATH.open("w", newline='') as csvfile:
            output = csv.writer(csvfile)
            num_seats = math.ceil(student_count / seat_count * int(rcount))
            for _ in range(num_seats):
                if student_index < student_count:
                    student = students[student_index]
                    student_index += 1
                    output.writerow(student)
            csvfile.flush()

        # Check if the os.system call is successful
        if os.system(f"./seatingchart.py {rname} {rname}") != 0:
            print("\033[01;91mError: seatingchart.py failed\033[0m")
            return

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

    print("\033[01;92mSuccess!\033[0m")

if __name__ == "__main__":
    main()
