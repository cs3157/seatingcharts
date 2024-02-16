#!/usr/bin/env python3

import argparse
import csv
import glob
import os
import random
import shutil
import sys
import math
from pathlib import Path
from csv2pdf import convert

OUT_PATH = Path.cwd() / "out"
HTML_PATH = Path.home() / "html" / "seating"

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
    seat_csv_path.write_text("Uni, Name, Room, Seat\n")
    seat_csv_path.chmod(0o744)


def main():
    parser = argparse.ArgumentParser(description="Go brrr with the seating charts")
    parser.add_argument("rooms", type=str, metavar='<rooms>')
    parser.add_argument("roster", type=str, metavar='<roster>')
    args = parser.parse_args()

    ROOMS_IN_ORDER = Path(args.rooms)
    STUDENT_LIST = Path(args.roster)

    with STUDENT_LIST.open() as f:
        students = [tuple(s) for s in csv.reader(f)]

    random.shuffle(students)
    student_count = len(students)
    seat_count = 0

    rename_images(Path("images"))

    create_html_directory(HTML_PATH)

    # Create the file
    seat_csv_path = HTML_PATH / "seat.csv"
    init_seat_csv(seat_csv_path)

    with ROOMS_IN_ORDER.open('r') as f:
        rooms = [r.strip().split() for r in f.readlines() if r.strip()]

    print(f"rooms:{rooms}")
    for _, count in rooms:
        seat_count += int(count)
    print(f"Total seats:{seat_count}")

    for room in rooms:
        rname = room[0]
        path = Path(OUT_PATH) / rname
        shutil.rmtree(path, ignore_errors=True)
        path.mkdir(parents=True)
        (path / "images").symlink_to(Path("images"))

        with (path / f"roster_{rname}.csv").open("w", newline='') as csvfile:
            output = csv.writer(csvfile)
            output.writerow([""] * 2)
            for _ in range(math.ceil(student_count / seat_count * int(room[1]))):
                if students:
                    student = random.choice(students)
                    output.writerow(student)
                    students.remove(student)
            csvfile.flush()

        os.system(["./seatingchart.py", rname, rname])
        shutil.copy(path / f"chart_{rname}.html", HTML_PATH / f"{rname}.html")

        with (path / f"list_{rname}.csv").open('r') as list_file:
            with seat_csv_path.open('a') as seat_file:
                for line in list_file:
                    modified_line = line.replace(f"{room[0]},", f"{room[0]}, {rname},")
                    seat_file.write(modified_line)

        (HTML_PATH / f"{rname}.html").chmod(0o644)

    shutil.copytree("images", HTML_PATH / "images")
    (HTML_PATH / "images").chmod(0o711)
    for img in (HTML_PATH / "images").glob("*.*"):
        img.chmod(0o644)

    convert(seat_csv_path, HTML_PATH / "seat.pdf")
    (HTML_PATH / "seat.pdf").chmod(0o644)
    seat_csv_path.unlink()

    print("\033[01;92mSuccess!\033[0m")

if __name__ == "__main__":
    main()
