#!/usr/bin/python3

import json

import util

try:
    with open("./config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    with open("../config.json") as f:
        config = json.load(f)

contacts = util.pull(config=config)
print(f"There are {len(contacts)} contacts in our member database")