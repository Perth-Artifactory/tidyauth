#!/usr/bin/python3

import json

from util import pull as pull

try:
    with open("./config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    with open("../config.json") as f:
        config = json.load(f)

contacts = pull(config=config)
print(f"There are {len(contacts)} contacts in our member database")


