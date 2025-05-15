from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
from mastodon import Mastodon
import os
import requests

access_token = os.getenv("MASTODON_ACCESS_TOKEN")

mastodon = Mastodon(
    access_token=access_token,

    api_base_url="https://mastodon.brown-silva.social",
    user_agent="kevin-brown/python-sprints-mastodon-bot",
)

conference_request = requests.get("https://us.pycon.org/2025/schedule/conference.json")
conference_data = conference_request.json()

open_space_data = conference_data["open-spaces"]

current_time = datetime(
    year=2025,
    month=5,
    day=17,
    hour=13,
    minute=30,
    second=0,
    tzinfo=timezone(timedelta(hours=-4)),
)

open_spaces = []

for open_space in open_space_data:
    space_start = parse(open_space["start"])
    space_end = parse(open_space["end"])

    time_until_start = space_start - current_time
    time_until_end = space_end - current_time

    starting_soon = timedelta(minutes=-1) < time_until_start <= timedelta(minutes=30)
    currently_happening = space_start < current_time and space_end > current_time and time_until_end >= timedelta(minutes=30)

    if True:#starting_soon or currently_happening:
        summary = f"{open_space["room"]}: {open_space["title"]}"
        start_time = space_start.strftime("%I:%M %p")

        open_spaces.append({
            "summary": summary,
            "details": open_space["description"],
            "start_time": start_time,
            "start_day": space_start.strftime("%A"),
            "sort_time": space_start
        })

open_spaces = sorted(open_spaces, key=lambda x: x["sort_time"])

for open_space in open_spaces:
    post = f"A new open space was announced for {open_space["start_day"]} at {open_space["start_time"]}" + "\n\n"
    post += open_space["summary"] + "\n\n"
    post += open_space["details"]

    print(post)
