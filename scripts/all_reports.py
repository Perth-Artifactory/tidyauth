#!/usr/bin/python3

from pprint import pprint
import locker_allocation, locker_utilisation, template, audit_emergency

reporters = [template, locker_allocation, locker_utilisation, audit_emergency]
reports = []
for reporter in reporters:
    reports.append(reporter.chain())
pprint(reports)