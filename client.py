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

# Get all keys fresh from TidyHQ
# Due to upstream API delays this will take a few seconds
t = time.time()
r = requests.get("http://localhost:8080/api/v1/keys/door", params={"token":"DEMO CLIENT", "update": "tidyhq"})
keys = r.json()
print(f"Loaded {len(keys)} keys from TidyHQ for door auth")
print(f"Timing: {round(time.time() - t,3)}s")

pprint(keys, indent=2)