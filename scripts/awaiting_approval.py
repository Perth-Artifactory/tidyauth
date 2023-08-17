#!/usr/bin/python3

import json
import logging
import sys
from datetime import datetime
from pprint import pprint

import requests
import util


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
for membership in memberships:
    if membership["state"] != "expired":
        contact = contacts[membership["contact_id"]]  # type: ignore
        a = util.find(contact=contact, field_id=config["ids"]["membership status"])
        if not a:
            problems.append(
                {
                    "name": util.prettyname(
                        contact_id=membership["contact_id"], contacts=contacts
                    ),
                    "problem": "Active membership but no membership groups",
                    "level": membership["membership_level"]["name"],
                }
            )
        elif len(a) > 1:
            problems.append(
                {
                    "name": util.prettyname(
                        contact_id=membership["contact_id"], contacts=contacts
                    ),
                    "problem": "Active membership and multiple membership groups",
                    "level": membership["membership_level"]["name"],
                }
            )
        elif a[0]["id"] != config["ids"]["membership approval"]:
            problems.append(
                {
                    "name": util.prettyname(
                        contact_id=membership["contact_id"], contacts=contacts
                    ),
                    "problem": "Active membership and has not had membership approved yet",
                    "level": membership["membership_level"]["name"],
                }
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
        print(util.report_formatter(data=[{"table": d}], dtype=output_format))
