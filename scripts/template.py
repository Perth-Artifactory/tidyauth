#!/usr/bin/python3

from datetime import datetime
import json

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
s = {"title":"Total contacts",
     "explainer": f"This stat was generated from data stored in TidyHQ. It was retrieved at: {datetime.now()}",
     "table": [["Total contacts"],[len(contacts)]]}
if __name__ == "__main__":
    print(f"There are {len(contacts)} contacts in our member database")