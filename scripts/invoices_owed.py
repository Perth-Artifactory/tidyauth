#!/usr/bin/python3

import json
import logging
import sys
from datetime import datetime
from pprint import pprint

import requests
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

if __name__ != "__main__":
    output_format = "internal"
elif len(sys.argv) < 2:
    output_format = "string"
elif sys.argv[1] not in ["json", "html", "html_embed", "mrkdwn", "string"]:
    output_format = "string"
else:
    output_format = sys.argv[1]

all = 0

contacts = util.pull(config=config, restructured=True)
if not contacts:
    logging.error("Could not reach TidyHQ")
    sys.exit(1)

try:
    r = requests.get(
        config["urls"]["invoices"], params={"access_token": config["tidytoken"]}
    )
    invoices = r.json()
except requests.exceptions.RequestException as e:
    logging.error("Could not reach TidyHQ")
    sys.exit(1)

dates = {}
close = {}
outstanding = {}
for invoice in invoices:
    if not invoice["paid"] and "Membership" in invoice["name"]:
        due = datetime.strptime(invoice["due_date"], "%Y-%m-%d")
        time_since = datetime.now() - due
        month = round(int(time_since.days) / 30)
        if month not in dates.keys():
            dates[month] = 0
        dates[month] += 1
        if time_since.days > 74:
            if invoice["contact_id"] not in close.keys():
                close[invoice["contact_id"]] = 0
            close[invoice["contact_id"]] += 1
        if time_since.days > 7:
            if invoice["contact_id"] not in outstanding.keys():
                outstanding[invoice["contact_id"]] = 0
            outstanding[invoice["contact_id"]] += 1

# Add names to close/outstanding
for person in close:
    name = util.prettyname(contact_id=person, contacts=contacts)
    if not name:
        name = person
    close[person] = {"name": name, "invoices": close[person]}
for person in outstanding:
    name = util.prettyname(contact_id=person, contacts=contacts)
    if not name:
        name = person
    outstanding[person] = {"name": name, "invoices": outstanding[person]}

# Compress data if the table would be too big
if len(dates) > 4:
    processing = {}
    for item in sorted(dates.keys())[4:]:
        processing[item] = dates[item]
    i = 1
    while len(processing) > 5:
        k = sorted(processing.keys())
        processing[sorted(k)[-(i + 1)]] += processing.pop(k[-i], 0)
        i += 1
        if i >= len(processing):
            i = 1
    squashed_dates = {}
    for item in sorted(dates.keys())[:4]:
        squashed_dates[item] = dates[item]
    squashed_dates.update(processing)
    dates = dict(squashed_dates)

s = []
if dates:
    d = [[], []]
    for c, f in zip(range(len(dates)), sorted(dates.keys())):
        if f == 0:
            d[0].append(f"<1")
        elif f == 1:
            d[0].append(f)
        elif c > 3:
            d[0].append(f"{f}+")
        else:
            d[0].append(f"{f}")
        d[1].append(dates[f])
    s.append(
        {
            "title": "Due membership invoices",
            "explainer": f"Breakdown of how many invoices are due by months due.",
            "table": d,
        }
    )

if outstanding:
    d = [["Name", "#"]]
    for p in sorted(outstanding.items(), key=lambda i: i[1]["invoices"], reverse=True):
        d.append([p[1]["name"], p[1]["invoices"]])
    s.append(
        {
            "title": "Invoices due 7+ days ago",
            "table": d,
            "explainer": "Members can appear on both lists",
        }
    )

if close:
    d = [["Name", "#"]]
    for p in sorted(close.items(), key=lambda i: i[1]["invoices"], reverse=True):
        d.append([p[1]["name"], p[1]["invoices"]])
    s.append(
        {
            "title": "Invoices due 74+ days ago",
            "table": d,
            "explainer": "Members can appear on both lists",
        }
    )

if s:
    if output_format == "json":
        pprint(dates)
        pprint(outstanding)
        pprint(close)
    elif output_format in ["html", "mrkdwn", "internal"]:
        if output_format != "internal":
            print(util.report_formatter(data=s, dtype=output_format))
    elif output_format == "string":
        pprint(dates)
        pprint(outstanding)
        pprint(close)
    elif output_format == "html_embed":
        print(util.report_formatter(data=s, dtype=output_format))
