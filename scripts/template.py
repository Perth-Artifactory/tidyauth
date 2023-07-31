#!/usr/bin/python3

import json
import sys
from datetime import datetime

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

contacts = util.pull(config=config)
if not contacts:
    sys.exit(1)
s = [
    {
        "title": "Total contacts",
        "explainer": f"This stat was generated from data stored in TidyHQ. It was retrieved at: {datetime.now()}",
        "table": [["Total contacts"], [len(contacts)]],
    }
]
if __name__ == "__main__":
    print(f"There are {len(contacts)} contacts in our member database")
