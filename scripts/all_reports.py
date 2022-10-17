#!/usr/bin/python3

from pprint import pprint
import lockers, template, audit_emergency

reporters = [template, lockers, audit_emergency]
reports = []
for reporter in reporters:
    reports.append(reporter.chain())
pprint(reports)