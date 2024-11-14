#!/usr/bin/python3

import json
import logging
import sys
from datetime import datetime
from pprint import pprint

import requests
import util
from tabulate import tabulate


def chain():
    global s
    return s


try:
    with open("./config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    with open("../config.json") as f:
        config = json.load(f)

if __name__ != "__main__":
    output_format = "internal"
elif len(sys.argv) < 2:
    output_format = "string"
elif sys.argv[1] not in ["json", "html", "html_embed", "mrkdwn", "string"]:
    output_format = "string"
else:
    output_format = sys.argv[1]

try:
    r = requests.get(
        config["urls"]["memberships"], params={"access_token": config["tidytoken"]}
    )
    memberships = r.json()
except requests.exceptions.RequestException as e:
    logging.error("Could not reach TidyHQ")
    sys.exit(1)

contacts = util.pull(config=config, restructured=True)
if not contacts:
    sys.exit(1)

problems = []
meeting_format = [["Date", "Name", "Class of membership"]]
for membership in memberships:
    if membership["state"] == "expired":
        continue

    if membership["membership_level"]["name"] == "Visitor":
        continue

    contact = contacts[membership["contact_id"]]  # type: ignore
    a = util.find(contact=contact, field_id=config["ids"]["membership status"])
    if not a:
        problems.append(
            {
                "name": util.prettyname(
                    contact_id=membership["contact_id"], contacts=contacts
                ),
                "problem": "Active membership but no indication of approval",
                "level": membership["membership_level"]["name"],
            }
        )
        meeting_format.append(
            [
                membership["created_at"],
                f"[{util.prettyname(contact_id=membership['contact_id'], contacts=contacts)}](https://artifactory.tidyhq.com/contacts/{membership['contact_id']})",
                membership["membership_level"]["name"],
            ]
        )
    elif len(a) > 1:
        problems.append(
            {
                "name": util.prettyname(
                    contact_id=membership["contact_id"], contacts=contacts
                ),
                "problem": "Active membership and too many statuses",
                "level": membership["membership_level"]["name"],
            }
        )
    elif a[0]["id"] != config["ids"]["membership approval"]:
        problems.append(
            {
                "name": util.prettyname(
                    contact_id=membership["contact_id"], contacts=contacts
                ),
                "problem": f"Active membership but status is: {a[0]['title']}",
                "level": membership["membership_level"]["name"],
            }
        )
        if a[0]["id"] == config["ids"]["membership waiting"]:
            meeting_format.append(
                [
                    membership["created_at"],
                    f"[{util.prettyname(contact_id=membership['contact_id'], contacts=contacts)}](https://artifactory.tidyhq.com/contacts/{membership['contact_id']})",
                    membership["membership_level"]["name"],
                ]
            )

if problems:
    d = [["Name", "Status", "Level"]]
    for problem in problems:
        d.append([problem["name"], problem["problem"], problem["level"]])
    if output_format == "json":
        pprint(d[1:])
    elif output_format in ["html", "mrkdwn", "internal"]:
        s = [
            {
                "title": "Memberships that need attention",
                "explainer": f"This table has been generated from data stored in TidyHQ. It only includes contacts with memberships not marked as expired. It was retrieved at: {datetime.now()}",
                "table": d,
            }
        ]
        if output_format != "internal":
            print(util.report_formatter(data=s, dtype=output_format))
    elif output_format == "string":
        for person in d[1:]:
            print(f"{person[0]}: {person[1]}")
    elif output_format == "html_embed":
        # Format meeting_format for pasting into meeting minutes

        print(
            util.report_formatter(
                data=[
                    {
                        "table": d,
                        "explainer": f"The following table is preformatted for pasting into meeting minutes. It only includes people with an active membership but no indication of approval.\n{tabulate(meeting_format, headers='firstrow', tablefmt='github')}",
                        "pre": True,
                    },
                ],
                dtype=output_format,
            )
        )
