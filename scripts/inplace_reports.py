#!/usr/bin/python3

import sys
import util

if len(sys.argv) != 3:
    print("inplace_reports.py [restricted|meeting] file.md")
    sys.exit(1)
else:
    otype = sys.argv[1]
    file = sys.argv[2]

try:
    with open(file, "r") as f:
        page = f.read()
except FileNotFoundError:
    print(f"Could not find/access: {file}")
    sys.exit(1)

print("Generating reports...")
import awaiting_approval
import locker_utilisation
import members
import invoices_owed

print("Reports generated")

placeholders = []
placeholders.append(
    {"string": "### Membership Storage Officer", "report": locker_utilisation}
)
placeholders.append({"string": "### Current Status", "report": members})
placeholders.append(
    {"string": "### New Memberships for approval", "report": awaiting_approval}
)
placeholders.append({"string": "### Due invoices", "report": invoices_owed})


changed = False
for p in placeholders:
    if p["report"].chain():
        print(f'Adding to {p["string"]}')
        s = []
        for section in p["report"].chain():
            section.pop("title", None)
            # section.pop('explainer', None)
            s.append(section)
        string = util.report_formatter(data=s, dtype="mrkdwn")
        string = p["string"] + "\n\n" + string
        page = page.replace(p["string"], string)
        changed = True

if changed:
    with open(file, "w") as f:
        f.write(page)
else:
    print("No reports added")
