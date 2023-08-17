#!/usr/bin/python3

import sys
from pprint import pprint

import util

if len(sys.argv) < 2:
    output_format = "mrkdwn"
elif sys.argv[1] not in ["json", "html", "mrkdwn"]:
    output_format = "mrkdwn"
else:
    output_format = sys.argv[1]


import audit_emergency
import awaiting_approval
import locker_allocation
import locker_utilisation
import members
import invoices_owed
import template

reporters = [
    template,
    members,
    locker_allocation,
    locker_utilisation,
    audit_emergency,
    awaiting_approval,
    invoices_owed,
]
reports = []
for reporter in reporters:
    if type(reporter.chain()) == list:
        reports += reporter.chain()
    else:
        print(reporter)
        pprint(reporter.chain())

if output_format == "json":
    pprint(reports)
print(util.report_formatter(data=reports, dtype=output_format))
