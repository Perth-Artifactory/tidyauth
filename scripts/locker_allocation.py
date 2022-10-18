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
    locations[s[0]][s[1]] = {"contact_id":person,
                             "name": util.prettyname(contact_id=person, config=config, contacts=contacts),
                             "membership": util.check_membership(contact_id=person, config=config)}

if output_format == "json":
    pprint(locations)
    sys.exit(0)
elif output_format in ["html", "mrkdwn","internal"]:
    d = [["Locker #", "Name", "TidyHQ", "Membership status"]]
    for location in sorted(locations):
        l = 1
        for locker in sorted(locations[location]):
            data = locations[location][locker]
            lp = int(locker)
            while lp > l+1:
                l += 1
                d.append([f"{location}{l:0{len(str(locker))}}", "NO DATA"])
            l = int(locker)
            d.append([f'{location}{locker}', data["name"], data["contact_id"], data["membership"]])
    s = {"title":"Locker allocations",
         "explainer": f"This table has been generated from data stored in TidyHQ. It was retrieved at: {datetime.now()}",
         "table": d}
    if output_format != "internal":
        print(util.report_formatter(data=[s], dtype=output_format))

elif output_format == "string":
    for location in sorted(locations):
        l = 1
        for locker in sorted(locations[location]):
            data = locations[location][locker]
            lp = int(locker)
            while lp > l+1:
                l += 1
                print(f"{location}{l:0{len(str(locker))}}: NO DATA")
            l = int(locker)
            print(f'{location}{locker}: {data["name"]} ({data["contact_id"]}) - Member: {data["membership"]}')