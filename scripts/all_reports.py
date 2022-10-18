#!/usr/bin/python3

from pprint import pprint

import audit_emergency
import locker_allocation
import locker_utilisation
import template

reporters = [template, locker_allocation, locker_utilisation, audit_emergency]
reports = []
for reporter in reporters:
    reports.append(reporter.chain())
pprint(reports)