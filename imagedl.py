#!/usr/bin/env python3

import argparse
import re
import requests
from pathlib import Path
import shlex
import sys
import rosters

TITLE_ART = r"""
         ____                    ___  __
        /  _/_ _  ___ ____ ____ / _ \/ /
       _/ //  ' \/ _ `/ _ `/ -_) // / /__
      /___/_/_/_/\_,_/\_, /\__/____/____/
                     /___/
"""

RED = "\033[1;31m"
GREEN = "\033[92m"
YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
END = "\033[0m"
LINE_CLEAR = "\x1b[2K"
LINE_UP = "\033[1A"

# Headers that make the server answer "304 Not Modified" (no image data), or that requests should compute itself.
DROP_HEADERS = {"if-none-match", "if-modified-since", "content-length", "host"}

# Stop early if this many downloads in a row fail
MAX_CONSECUTIVE_FAILURES = 5

def decode_ansi_c(match):
    """Turn bash $'...' quoting (which Chrome uses for cookies) into a plain
    shell-quoted string, decoding escape sequences"""
    body = match.group(1)

    def replace(m):
        esc = m.group(0)
        c = esc[1]
        if c in "uU":
            return chr(int(esc[2:], 16))
        if c == "x":
            return chr(int(esc[2:], 16))
        return {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", "'": "'", '"': '"'}.get(c, esc)

    decoded = re.sub(r"\\(u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|x[0-9a-fA-F]{1,2}|.)", replace, body)
    return shlex.quote(decoded)

def parse_curl(text):
    """Extract the image URL, headers, and cookies from a copied command.
    Handles both -H 'cookie: ...' and -b $'...'."""
    text = text.replace("\\\r\n", " ").replace("\\\n", " ")
    text = re.sub(r"\$'((?:[^'\\]|\\.)*)'", decode_ansi_c, text)
    tokens = shlex.split(text)

    url = None
    headers = {}
    cookie = None
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if tok == "curl":
            pass
        elif tok == "--url":
            url, i = nxt, i + 1
        elif tok in ("-H", "--header"):
            name, _, value = nxt.partition(":")
            name, value = name.strip(), value.strip()
            if name.lower() == "cookie":
                cookie = value
            elif name.lower() not in DROP_HEADERS:
                headers[name] = value
            i += 1
        elif tok in ("-b", "--cookie"):
            cookie, i = nxt, i + 1
        elif tok in ("-X", "--request", "-A", "--user-agent", "-e", "--referer",
                     "-d", "--data", "--data-raw", "--data-binary", "-u", "--user"):
            if tok in ("-A", "--user-agent"):
                headers["user-agent"] = nxt
            elif tok in ("-e", "--referer"):
                headers["referer"] = nxt
            i += 1
        elif tok.startswith("http://") or tok.startswith("https://"):
            url = tok
        i += 1

    if not url:
        raise ValueError("Couldn't find the image URL in the copied curl command")
    if cookie:
        headers["cookie"] = cookie
    return url, headers

def do_dl(url_prefix, headers, unis, output_dir):
    session = requests.Session()
    uni_count = len(unis)
    succeeded, failed = [], []
    consecutive_failures = 0

    for counter, uni in enumerate(sorted(unis), start=1):
        url = f'{url_prefix}{uni}.jpg'
        
        counter += 1
        percentage = round(counter / uni_count * 100, 1)
        print(f"Downloading {uni}.jpg ({counter}/{uni_count} -- {percentage}%)")
        print(LINE_UP, end=LINE_CLEAR) # CLear previous line

        try:
            response = session.get(url, headers=headers, timeout=30)
            content_type = response.headers.get("content-type", "")
            ok = response.status_code == 200 and content_type.startswith("image/")
            reason = f"HTTP {response.status_code}, {content_type or 'no content-type'}"
        except requests.RequestException as e:
            ok, reason = False, str(e)

        if ok:
            (output_dir / f"{uni}.jpg").write_bytes(response.content)
            succeeded.append(uni)
            consecutive_failures = 0
        else:
            failed.append((uni, reason))
            consecutive_failures += 1
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES and not succeeded:
                print(f"{RED}The first {consecutive_failures} downloads all failed ({reason}). Stopping.{END}")
                return False

    print(f"{GREEN}Downloaded {len(succeeded)} of {uni_count} images.{END}")
    if failed:
        print(f"{YELLOW}{len(failed)} failed (nothing was saved for these):{END}")
        for uni, reason in failed:
            print(f"  {uni}: {reason}")
        print("Rerun with --skip-existing to retry only the missing UNIs.")
    return not failed
        
last_step_number = 0
def step(instruction, await_input=True):
    global last_step_number

    (input if await_input else print)(f'[{last_step_number}] {instruction}')
    last_step_number += 1

def run_guide(output_dir, roster_filepath, curl_filepath, skip_existing=False, keep_curl_file=False):
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
    if uni_count == 0:
        print("Nothing to download.")
        return

    print(YELLOW + "The instructions were designed for Chromium-based browsers and might differ on other browsers.\n" + END)
    print(YELLOW + "This utility reads a sample curl from a file, so you'll want a second CLAC tab or window to create that file.\n" + END)
    print(LIGHT_BLUE + "This utility will guide you through a series of steps. Once you complete a step, press ENTER" + END)
    step("Press ENTER to begin")
    step("Open canvas/courseworks and go to the relevant course, then open your browser's developer tools. Find the network tab and press 'clear'")
    step("Navigate to 'Photo Roster' section on the course canvas page and wait for images to load (this can take a while)")
    step("The network tab should fill with requests to images named named after students' unis. Right click one of these requests and select 'Copy as cURL (bash)'. Be careful NOT to select the option saying 'Copy ALL'", await_input=False)
    step(f"Paste the copied text into a plaintext file at '{curl_filepath.as_posix()}' and save it (don't paste it here—the terminal cuts off long lines). Then press ENTER")

    if not curl_filepath.exists():
        print(f"{RED}Couldn't find '{curl_filepath.as_posix()}'. Save the cURL command there and rerun.{END}")
        sys.exit(1)

    url, headers = parse_curl(curl_filepath.read_text())

    if not keep_curl_file:
        curl_filepath.unlink()
        print(f"Deleted '{curl_filepath.as_posix()}' containing your session cookie.")

    # Remove the file name from the url
    # i.e. "hostname/path/uni.jpg" -> "hostname/path/"
    url_prefix = url.rsplit("/", 1)[0] + "/"

    print("Extracted URL prefix:", url_prefix)
    print(f"Extracted {len(headers)} headers:", ", ".join(headers))
    if "cookie" not in {h.lower() for h in headers}:
        print(f"{RED}No cookies were found in the curl command, so the server will reject every request.{END}")
        print("Make sure you used 'Copy as cURL (bash)' on a single image request while signed in.")
        sys.exit(1)

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

    parser.add_argument("--curl-file",
                        type=str,
                        default="curl.txt",
                        metavar="<file>",
                        help="Text file holding the command from 'Copy as cURL (bash)'")

    parser.add_argument("--skip-existing",
                        action='store_true',
                        default=False)

    parser.add_argument("--keep-curl-file",
                        action="store_true",
                        default=False,
                        help="Don't delete the curl file after reading it")

    args = parser.parse_args()
    run_guide(output_dir=Path(args.outdir), roster_filepath=Path(args.roster), curl_filepath=Path(args.curl_file), skip_existing=args.skip_existing, keep_curl_file=args.keep_curl_file)
