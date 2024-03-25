#!/usr/bin/env python3

import argparse
import os
import re
import requests

import rosters

TITLE_ART = """
         ____                    ___  __ 
        /  _/_ _  ___ ____ ____ / _ \/ / 
       _/ //  ' \/ _ `/ _ `/ -_) // / /__
      /___/_/_/_/\_,_/\_, /\__/____/____/
                     /___/               
                     """

YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
END = "\033[0m"

def multiline_input():
    lines = []
    while True:
        inpt = input()
        if len(inpt) > 0:
            lines.append(inpt)
        else:
            return lines


def parse_curl(curl):
  url = re.search("'([^']*)'", curl[0]).group(1)

  headers = {}
  for line in curl[1:]:
      if line.strip().startswith('-H'):
          header_name, header_value = re.search("'([^']*)'", line).group(1).split(': ')
          headers[header_name] = header_value

  return url,headers

def do_dl(url_prefix, headers, unis, output_dir):
    counter = 0
    uni_count = len(unis)
    for uni in unis:
        url = url_prefix+uni+'.jpg'
        
        counter += 1
        percentage = f"{round(counter/uni_count*100, 1)}%"
        print("Downloading", url, f"({counter}/{uni_count} -- {percentage})")
        response = requests.get(url, headers=headers)

        with open(os.path.join(output_dir, uni+'.jpg'), 'wb') as f:
            f.write(response.content)
        
last_step_number = 0
def step(instruction):
    global last_step_number

    print(f'[{last_step_number}]', instruction)
    last_step_number += 1
    input()

def run_guide(output_dir, unis=None, roster_filepath=None, skip_existing=False):
    print(TITLE_ART)
    print("Python utility to download student images automatically")

    if not os.path.exists(output_dir):
        print("Output directory does not exist. Creating...")
        os.mkdir(output_dir)

    if unis is None and roster_filepath is not None:
        print("Loading roster...")
        students = rosters.load_roster(roster_filepath)
        print(f"Loaded {len(students)} from roster.")
        unis = set(map(lambda student: student[0], students))

        if skip_existing:
            skipped_unis = set(map(lambda file: file.split('.')[0], os.listdir(output_dir))).intersection(unis)
            unis = unis.difference(skipped_unis)
            print(f"{YELLOW}{len(skipped_unis)} UNIs already have images in the output directory and will be skipped.{END}")

    else:
        raise Exception("unis and roster_filepath cannot both be None")
  
    uni_count = len(unis)
    print(f"Found {uni_count} UNIs")

    print(YELLOW + "The instructions were designed for chromium based browsers and might differ on other browsers.\n" + END)
    print(LIGHT_BLUE + "This utility will guide you through a series of steps. Once you complete a step, press ENTER" + END)
    step("Press ENTER to begin")
    step("Open canvas/courseworks and go to the relevant course, then open your browser's developer tools. Find the network tab and press 'clear'")
    step("Navigate to 'Photo Roster' section on the course canvas page and wait for images to load (this can take a while)")
    step("The network tab should fill with requests to images named named after student's unis. Right click one of these requests and select 'Copy as cURL (bash)'. Be careful NOT to select the option saying 'Copy ALL'")
    print(LIGHT_BLUE + "Paste the copied text in this window. If the script doesn't continue automatically, press ENTER." + END)

    curl = multiline_input()

    url, headers = parse_curl(curl)
    url_prefix = "/".join(url.split('/')[:-1])+'/'

    print("Extracted URL prefix:", url_prefix)
    print(f"Extracted {len(headers)} headers:", headers)
    print(f"\n{LIGHT_BLUE}The script will now pretend to be your browser and download {uni_count} images to the '{output_dir}' directory.{END}")

    if input("Are you ready to begin? (Y/n) ") not in ['Y','y','']:
        print('Aborted.')
        exit(0)

  
    do_dl(url_prefix,headers,unis,output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
    description="Download student images")

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
    run_guide(output_dir=args.outdir, roster_filepath=args.roster, skip_existing=args.skip_existing)
