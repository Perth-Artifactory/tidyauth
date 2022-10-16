#!/usr/bin/python3

import itertools
import json
from pprint import pprint

import util

try:
    with open("./config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    with open("../config.json") as f:
        config = json.load(f)

contacts = util.pull(config=config)

lockers = {}
for contact in contacts:
    locker = util.find(contact = contact, field_id=config["ids"]["locker"])
    if locker:
        lockers[contact["id"]] = locker

locations = {}
for locker in lockers:
    s = ["".join(x) for _, x in itertools.groupby(lockers[locker], key=str.isdigit)]
    if s[0] not in locations:
        locations[s[0]] = {}
    locations[s[0]][s[1]] = locker
pprint(locations)
print(f"found {len(lockers)} locker assignments")