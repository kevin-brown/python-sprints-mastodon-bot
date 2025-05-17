from collections import defaultdict
from datetime import timedelta, timezone
from dateutil.parser import parse
import os
import requests
import sys

access_token = os.getenv("MASTODON_ACCESS_TOKEN")

conference_request = requests.get("https://us.pycon.org/2025/schedule/conference.json")
conference_data = conference_request.json()

open_space_data = conference_data["open-spaces"]

current_time = parse(sys.argv[1]).replace(
    tzinfo=timezone(timedelta(hours=-4)),
)

open_spaces = []

for open_space in open_space_data:
    space_start = parse(open_space["start"])
    space_end = parse(open_space["end"])

    time_until_start = space_start - current_time
    time_until_end = space_end - current_time

    starting_soon = timedelta(minutes=-1) < time_until_start <= timedelta(minutes=45)
    currently_happening = space_start < current_time and space_end > current_time and time_until_end >= timedelta(minutes=30)

    if starting_soon or currently_happening:
        summary = f"{open_space["room_display"]}: {open_space["title"]}"
        start_time = space_start.strftime("%I:%M %p")

        open_spaces.append({
            "summary": summary,
            "details": open_space["description"],
            "start_time": start_time,
            "start_day": space_start.strftime("%A"),
            "sort_time": space_start
        })

open_spaces = sorted(open_spaces, key=lambda x: x["sort_time"])

spaces_at_time = defaultdict(list)

for open_space in open_spaces:
    spaces_at_time[open_space["sort_time"]].append(open_space)

for start_time, open_spaces in spaces_at_time.items():
    open_spaces = sorted(open_spaces, key=lambda x: x["summary"])

    if start_time < current_time:
        print(f"\nContinued from {start_time.strftime("%I:%M %p")}:\n")
    elif start_time > current_time:
        print(f"\nStarting at {start_time.strftime("%I:%M %p")}:\n")
    else:
        print(f"\nStarting at {start_time.strftime("%I:%M %p")}:\n")

    for open_space in open_spaces:
        print(open_space["summary"])