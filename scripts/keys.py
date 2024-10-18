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

d = [["Name", "Key Status", "Bond", "Key"]]
for membership in memberships:
    if membership["state"] != "expired":
        contact = contacts[membership["contact_id"]]

        # Add the name
        current = [
            util.prettyname(contact_id=membership["contact_id"], contacts=contacts)
        ]

        status = ""
        bond = "Bond field empty"
        key = "No key"

        # Iterate over custom fields
        for field in contact["custom_fields"]:
            # Check whether they have a key _enabled_
            if field["id"] == config["ids"]["status"]:
                for value in field["value"]:
                    status += value["title"] + ", "
                status = status[:-2]

            # Check whether they have a bond
            elif field["id"] == config["ids"]["bond"]:
                bond = field["value"]

            # Check whether they have a key
            elif field["id"] == config["ids"]["tag"]:
                key = field["value"]

        if status == "":
            status = "No status set (disabled)"

        current += [status, "$" + bond, key]
        d.append(current)

if len(d) > 1:
    if output_format == "json":
        pprint(d[1:])
    elif output_format in ["html", "mrkdwn", "internal"]:
        s = [
            {
                "title": "Keyholder status",
                "explainer": f"This table has been generated from data stored in TidyHQ. It only includes contacts with memberships not marked as expired. It was retrieved at: {datetime.now()}",
                "table": d,
            }
        ]
        if output_format != "internal":
            print(util.report_formatter(data=s, dtype=output_format))
    elif output_format == "string":
        for person in d[1:]:
            print(person[0])
            print(person[1], person[2])
            print(person[3])
            print("")
    elif output_format == "html_embed":
        print(util.report_formatter(data=[{"table": d}], dtype=output_format))
