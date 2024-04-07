#!/usr/bin/env python3

import argparse
import re
import requests
from pathlib import Path

import rosters

TITLE_ART = """
         ____                    ___  __ 
        /  _/_ _  ___ ____ ____ / _ \/ / 
       _/ //  ' \/ _ `/ _ `/ -_) // / /__
      /___/_/_/_/\_,_/\_, /\__/____/____/
                     /___/               
"""

GREEN = "\033[92m"
YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
END = "\033[0m"
LINE_CLEAR = "\x1b[2K"
LINE_UP = "\033[1A"

def multiline_input():
    lines = []
    while (inpt := input()):
        lines.append(inpt)

    return lines

# Used to extract the image download URL and required headers
# from the cUrl string copied from the browser
def parse_curl(curl):
  # Extract the url by finding the content of the first single-quote pair
  url = re.search("'([^']*)'", curl[0]).group(1)

  headers = {}
  for line in curl[1:]:
      if line.strip().startswith('-H'):
          # Extract the header by once again finding the content of the single-quote pair 
          header_name, header_value = re.search("'([^']*)'", line).group(1).split(': ')
          headers[header_name] = header_value

  return url, headers

def do_dl(url_prefix, headers, unis, output_dir):
    counter = 0
    uni_count = len(unis)
    for uni in unis:
        url = f'{url_prefix}{uni}.jpg'
        
        counter += 1
        percentage = round(counter / uni_count * 100, 1)
        print(f"Downloading {uni}.jpg ({counter}/{uni_count} -- {percentage}%)")
        print(LINE_UP, end=LINE_CLEAR) # CLear previous line
        response = requests.get(url, headers=headers)

        (output_dir / f"{uni}.jpg").write_bytes(response.content)

    print(GREEN + "Download complete." + END)
        
last_step_number = 0
def step(instruction, await_input=True):
    global last_step_number

    (input if await_input else print)(f'[{last_step_number}] {instruction}')
    last_step_number += 1

def run_guide(output_dir, roster_filepath, skip_existing=False):
    print(TITLE_ART)
    print("Python utility to download student images automatically")

    if not output_dir.exists():
        print("Output directory does not exist. Creating...")
        output_dir.mkdir()

    print("Loading roster...")
    students = rosters.load_roster(roster_filepath)
    print(f"Loaded {len(students)} from roster.")
    unis = set(map(lambda student: student[0], students))

    if skip_existing:
        skipped_unis = {file.stem for file in output_dir.iterdir()}.intersection(unis)
        
        unis = unis.difference(skipped_unis)
        print(f"{YELLOW}{len(skipped_unis)} UNIs already have images in the output directory and will be skipped.{END}")
 
    uni_count = len(unis)
    print(f"Found {uni_count} UNIs")

    print(YELLOW + "The instructions were designed for Chromium-based browsers and might differ on other browsers.\n" + END)
    print(LIGHT_BLUE + "This utility will guide you through a series of steps. Once you complete a step, press ENTER" + END)
    step("Press ENTER to begin")
    step("Open canvas/courseworks and go to the relevant course, then open your browser's developer tools. Find the network tab and press 'clear'")
    step("Navigate to 'Photo Roster' section on the course canvas page and wait for images to load (this can take a while)")
    step("The network tab should fill with requests to images named named after students' unis. Right click one of these requests and select 'Copy as cURL (bash)'. Be careful NOT to select the option saying 'Copy ALL'", await_input=False)
    print(LIGHT_BLUE + "Paste the copied text in this window. If the script doesn't continue automatically, press ENTER." + END)

    curl = multiline_input()

    url, headers = parse_curl(curl)

    # Remove the file name from the url
    # i.e. "hostname/path/uni.jpg" -> "hostname/path/"
    url_prefix = "/".join(url.split('/')[:-1]) + '/'

    print("Extracted URL prefix:", url_prefix)
    print(f"Extracted {len(headers)} headers:", headers)
    print(f"\n{LIGHT_BLUE}The script will now pretend to be your browser and download {uni_count} images to the '{output_dir.as_posix()}' directory.{END}")

    if input("Are you ready to begin? (Y/n) ") not in ['Y','y','']:
        print('Aborted.')
        exit(0)
  
    do_dl(url_prefix, headers, unis, output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
    description="Download student images from Courseworks")

    parser.add_argument("--outdir",
                       type=str,
                       nargs='?',
                       metavar='<output-directory>',
                       default='images')

    parser.add_argument("--roster",
                        type=str,
                        nargs='?',
                        default='roster.csv',
                        metavar='<roster>')
    
    parser.add_argument("--skip-existing",
                        action='store_true',
                        default=False)


    args = parser.parse_args()
    run_guide(output_dir=Path(args.outdir), roster_filepath=Path(args.roster), skip_existing=args.skip_existing)
