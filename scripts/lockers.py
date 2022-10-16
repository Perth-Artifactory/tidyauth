#!/usr/bin/python3

import itertools
import json
import sys
from pprint import pprint

import util

if len(sys.argv) < 2:
    output_format = "json"
elif sys.argv[1] not in ["json","html"]:
    output_format = "json"
else:
    output_format = sys.argv[1]

try:
    with open("./config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    with open("../config.json") as f:
        config = json.load(f)

contacts = util.pull(config=config)

lockers = {}
for contact in contacts:
    locker = util.find(contact=contact, field_id=config["ids"]["locker"])
    if locker:
        lockers[contact["id"]] = locker

locations = {}
for locker in lockers:
    s = ["".join(x) for _, x in itertools.groupby(lockers[locker], key=str.isdigit)]
    if s[0] not in locations:
        locations[s[0]] = {}
    locations[s[0]][s[1]] = locker

if output_format == "json":
    pprint(locations)
    sys.exit(0)
elif output_format == "html":
    print("I'm not ready yet!")
    sys.exit(0)
for location in sorted(locations):
    print(f"Area: {location}")
    l = 1
    for locker in sorted(locations[location]):
        lp = int(locker)
        while lp > l+1:
            l += 1
            print(f"{l:0{len(str(locker))}}: NO DATA")
        l = int(locker)
        contact_id = locations[location][locker]
        name = util.prettyname(contact_id=contact_id, config=config, contacts=contacts)
        member_status = util.check_membership(contact_id=locations[location][locker], config=config)
        print(f"{locker}: {name} ({contact_id}) - Member: {member_status}")