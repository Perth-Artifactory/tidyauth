#!/usr/bin/python3

import itertools
import json
import sys
from datetime import datetime
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

lockers = {}
for contact in contacts:
    locker = util.find(contact=contact, field_id=config["ids"]["locker"])
    if locker:
        lockers[contact["id"]] = locker

locations = {}
for person in lockers:
    s = ["".join(x) for _, x in itertools.groupby(lockers[person], key=str.isdigit)]
    if s[0] not in locations:
        locations[s[0]] = {}
    locations[s[0]][s[1]] = {"membership": util.check_membership(contact_id=person, config=config)}

counts = {"Active members":0,
          "Expired members": 0,
          "Blank": 0}
for location in sorted(locations):
    l = 1
    for locker in sorted(locations[location]):
        data = locations[location][locker]
        lp = int(locker)
        while lp > l+1:
            l += 1
            counts["Blank"] += 1
        l = int(locker)
        if data["membership"]:
            counts["Active members"] += 1
        else:
            counts["Expired members"] += 1

t = 0
for c in counts: t += counts[c]
counts["Total"] = t

if output_format == "json":
    pprint(counts)
    sys.exit(0)
elif output_format in ["html", "mrkdwn","internal"]:
    d = [["Type", "#", "%"]]
    for c in counts:
        d.append([c, counts[c], f'{round(counts[c] / counts["Total"]*100)}%'])  # type: ignore
        if c == "Total":
            d[-1].pop()

    s = [{"title":"Locker utilisation",
         "explainer": f"This table has been generated from data stored in TidyHQ. It was retrieved at: {datetime.now()}",
         "table": d}]
    if output_format != "internal":
        print(util.report_formatter(data=s, dtype=output_format))

elif output_format == "string":
    for c in counts:
        print(c, counts[c], f'{round(counts[c] / counts["Total"]*100)}%')