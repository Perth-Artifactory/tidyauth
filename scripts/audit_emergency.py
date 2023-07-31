#!/usr/bin/python3

from datetime import datetime
import json
from pprint import pprint
import logging
import sys

import phonenumbers
import requests

import util


def check_num(num):
    try:
        if phonenumbers.is_valid_number(phonenumbers.parse(num, "AU")):
            return True
        elif phonenumbers.is_valid_number(phonenumbers.parse("08" + num, "AU")):
            return True
    except phonenumbers.phonenumberutil.NumberParseException:
        return False
    return False


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

d = [["Name", "Emergency Contact Person", "Emergency Contact #", "Problem"]]
for membership in memberships:
    if membership["state"] != "expired":
        contact = contacts[membership["contact_id"]]  # type: ignore
        problems = []
        if contact["emergency_contact_person"] == None:
            problems.append("Emergency contact name missing")

        if contact["emergency_contact_number"] == None:
            problems.append("Emergency contact number missing")
        elif contact["emergency_contact_number"] == contact["phone_number"]:
            problems.append("Contact number and Emergency contact number match")
        elif contact["emergency_contact_number"][-9:] == contact["phone_number"][-9:]:
            problems.append("Contact number and Emergency contact number match")
        elif not check_num(contact["emergency_contact_number"]):
            problems.append("Emergency number is not a valid number")

        if problems:
            d.append(
                [
                    util.prettyname(contact_id=membership["contact_id"], contacts=contacts),  # type: ignore
                    str(contact["emergency_contact_person"]),
                    str(contact["emergency_contact_number"]),
                    "\n".join(problems),
                ]
            )
if len(d) > 1:
    if output_format == "json":
        pprint(d[1:])
    elif output_format in ["html", "mrkdwn", "internal"]:
        s = [
            {
                "title": "Invalid emergency contact data",
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
