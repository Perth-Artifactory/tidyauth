#!/usr/bin/python3

import requests
import time
from pprint import pprint

# Get all cached active door keys
t = time.time()
r = requests.get("http://localhost:8080/api/v1/keys/door", params={"token":"DEMO CLIENT"})
keys = r.json()
print(f"Loaded {len(keys)} cached keys for door auth")
print(f"Timing: {round(time.time() - t,3)}s")

# Get all fresh door keys from TidyHQ
# Due to upstream API delays this will take a few seconds
t = time.time()
r = requests.get("http://localhost:8080/api/v1/keys/door", params={"token":"DEMO CLIENT", "update": "tidyhq"})
keys = r.json()
print(f"Loaded {len(keys)} keys from TidyHQ for door auth")
print(f"Timing: {round(time.time() - t,3)}s")

# Get all fresh vending keys from TidyHQ
# Due to upstream API delays this will take a few seconds
t = time.time()
r = requests.get("http://localhost:8080/api/v1/keys/vending", params={"token":"DEMO CLIENT", "update": "tidyhq"})
keys = r.json()
print(f"Loaded {len(keys)} keys from TidyHQ for vending machine billing")
print(f"Timing: {round(time.time() - t,3)}s")

# Get drink options from TidyHQ
# Due to upstream API delays this will take a few seconds
t = time.time()
r = requests.get("http://localhost:8080/api/v1/data/vending", params={"token":"DEMO CLIENT", "update": "tidyhq"})
drinks = r.json()
print(f"Loaded {len(keys)} drinks from TidyHQ for vending")
print(f"Timing: {round(time.time() - t,3)}s")