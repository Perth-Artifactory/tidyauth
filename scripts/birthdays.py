#!/usr/bin/python3

from datetime import datetime
import json
from pprint import pprint
import logging
import sys

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

if type(contacts) != dict:
    sys.exit(1)

birthdays = {}
for membership in memberships:
    if membership["state"] != "expired":
        contact = contacts[membership["contact_id"]]
        if contact["birthday"]:
            birthdate = datetime.strptime(contact["birthday"], "%Y-%m-%d")

            # Calculate how long until the contacts birthday
            today = datetime.today()
            birth_md = birthdate.replace(year=today.year)
            days = (birth_md - today).days
            new_age = today.year - birthdate.year
            if days < 0:
                birth_md = birthdate.replace(year=today.year + 1)
                days = (birth_md - today).days
                new_age = today.year + 1 - birthdate.year

            # Add the contact to the list of birthdays
            birthdays[contact["id"]] = {
                "name": util.prettyname(contact_id=contact["id"], contacts=contacts),
                "days": days,
                "age": new_age,
                "birthday": birth_md.strftime("%Y-%m-%d"),
            }

# Sort the list of birthdays by how many days until their birthday
birthdays = sorted(birthdays.items(), key=lambda i: i[1]["days"])

d = [["Name", "Birthday", "Turning", "Days Until"]]
for birthday in birthdays:
    bday = birthday[1]
    d.append([bday["name"], bday["birthday"], bday["age"], bday["days"]])

if output_format == "json":
    pprint(d[1:])
elif output_format in ["html", "mrkdwn", "internal"]:
    s = [
        {
            "title": "Member birthdays",
            "explainer": f"This table has been generated from data stored in TidyHQ. It only includes contacts with memberships not marked as expired. It was retrieved at: {datetime.now()}",
            "table": d,
        }
    ]
    if output_format != "internal":
        print(util.report_formatter(data=s, dtype=output_format))
elif output_format == "string":
    for person in d[1:]:
        print(f"{person[0]} turns {person[2]} on {person[1]} ({person[3]} days)")
elif output_format == "html_embed":
    print(util.report_formatter(data=[{"table": d}], dtype=output_format))
