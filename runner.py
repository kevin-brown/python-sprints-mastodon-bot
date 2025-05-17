from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
from mastodon import Mastodon
import html
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

mastodon_posts_by_day = {
    "Friday": 114512945743943792,
    "Saturday": 114513045657865732,
    "Sunday": 114513077119524653,
}

mastodon_already_posted = {
    "Friday": [],
    "Saturday": [],
    "Sunday": [],
}

for day, post_id in mastodon_posts_by_day.items():
    mastodon_already_posted[day] = mastodon.status_context(post_id).descendants

for open_space in open_spaces:
    posts = []

    details = open_space["details"]
    extra_details = ""
    continuation = ""

    opener = f"A new open space at #PyConUS was announced for {open_space["start_day"]} at {open_space["start_time"]}"
    tags = "#PyConUSOpenSpaces #PyConUS2025"
    continuation = ""

    max_description = 500 - len(opener) - len(tags) - 10

    if  len(details) >= max_description:
        continuation = " ... (cont.)"
        details = open_space["details"][:max_description - len(continuation)].rsplit(" ", 1)[0].strip()
        extra_details = open_space["details"][len(details):].strip()

    post = f"""
{opener}

{open_space["summary"]}

{details}{continuation}

{tags}
""".strip()

    posts.append(post)

    if extra_details:
        continued = f"""
{open_space["summary"]} (continued)

... {extra_details}
""".strip()

        posts.append(continued)

    should_post = True

    for post in mastodon_already_posted[open_space["start_day"]]:
        if open_space["summary"] in html.unescape(post.content):
            should_post = False
            break

    if should_post:
        print("\n\n---\n\n".join(posts))

        mastodon_post = mastodon.status_post(
            status=posts[0],
            visibility="unlisted",
            in_reply_to_id=mastodon_posts_by_day[open_space["start_day"]],
        )

        mastodon_already_posted[open_space["start_day"]].append(mastodon_post)

        if len(posts) > 1:
            mastodon.status_post(
                status=posts[1],
                visibility="unlisted",
                in_reply_to_id=mastodon_post.id,
            )

        break
