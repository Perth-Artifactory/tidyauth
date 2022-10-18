#!/usr/bin/python3

from datetime import datetime
import itertools
import json
import sys
import requests
import logging
from pprint import pprint

import util

def chain():
    global s
    return s

if __name__ != "__main__":
    output_format = "internal"
elif len(sys.argv) < 2:
    output_format = "string"
elif sys.argv[1] not in ["json","html","mrkdwn","string"]:
    output_format = "string"
else:
    output_format = sys.argv[1]

try:
    with open("./config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    with open("../config.json") as f:
        config = json.load(f)

contacts = util.pull(config=config)
if not contacts:
    sys.exit(1)

try:
    r = requests.get(config["urls"]["memberships"],params={"access_token":config["tidytoken"]})
    memberships = r.json()
except requests.exceptions.RequestException as e:
    logging.error("Could not reach TidyHQ")
    sys.exit(1)

try:
    r = requests.get(config["urls"]["membership_levels"],params={"access_token":config["tidytoken"]})
    levels = r.json()
except requests.exceptions.RequestException as e:
    logging.error("Could not reach TidyHQ")
    sys.exit(1)

membership_levels = {}

for level in levels:
    if not level['deleted']:
        membership_levels[level['id']] = {"name": level['name'],
                                          "count": 0}

total_memberships = 0
for membership in memberships:
    if membership['state'] != "expired" and membership['membership_level_id'] in membership_levels.keys():
        membership_levels[membership['membership_level_id']]["count"] += 1
        total_memberships += 1

membership_levels = sorted(membership_levels.items(), key=lambda i: i[1]['count'], reverse=True)

if output_format == "json":
    pprint(membership_levels)
    sys.exit(0)
elif output_format in ["html", "mrkdwn","internal"]:
    d = [["Membership", "#", "%"]]
    for m in membership_levels:
        m = m[1]
        d.append([m["name"], m["count"], f'{round(m["count"] / total_memberships*100)}%'])  # type: ignore
    d.append(["Total", total_memberships])  # type: ignore
    s = {"title":"Membership stats",
         "explainer": f"This table has been generated from data stored in TidyHQ. It was retrieved at: {datetime.now()}",
         "table": d}
    if output_format != "internal":
        print(util.report_formatter(data=[s], dtype=output_format))

elif output_format == "string":
    for m in membership_levels:
        m = m[1]
        print(m["name"], m["count"], f'{round(m["count"] / total_memberships*100)}%')