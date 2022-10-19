#!/usr/bin/python3

import sys
from pprint import pprint

import util

if len(sys.argv) != 3:
    print("inplace_reports.py [restricted|meeting] file.md")
    sys.exit(1)
else:
    otype = sys.argv[1]
    file = sys.argv[2]

try:
    with open(file,'r') as f:
        page = (f.read())
except FileNotFoundError:
    print(f"Could not find/access: {file}")

print("Generating reports...")
import awaiting_approval
import locker_utilisation
import members
print("Reports generated")

placeholders = []
placeholders.append({"string":"**Membership Storage Officer**",
                     "report": locker_utilisation})
placeholders.append({"string":"## Membership Report",
                     "report": members})
placeholders.append({"string":"**New Memberships for approval**",
                     "report": awaiting_approval})

changed = False
for p in placeholders:
    if p["report"].chain():
        print(f'Adding to {p["string"]}')
        s = dict(p["report"].chain()[0]) # Format set is to make pyright behave
        s.pop('title', None)
        #s.pop('explainer', None)
        string = util.report_formatter(data=[s],dtype="mrkdwn")
        string = p["string"] + "\n\n" + string
        page = page.replace(p["string"], string)
        changed = True

if changed:
    with open(file,'w') as f:
        f.write(page)
else:
    print("No reports added")