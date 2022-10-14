#!/usr/bin/python3

import hashlib
import random
import time
from pprint import pprint

import requests

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

# Look for contacts with assigned door sounds
contacts_with_sounds = []
for key in keys:
    k = keys[key]
    if "sound" in k.keys():
        contacts_with_sounds.append(k["tidyhq"])
print(f"Found {len(contacts_with_sounds)} contacts with uploaded sounds")

# Get a sound (if there is one)
if contacts_with_sounds:
    id = random.choice(contacts_with_sounds)
    t = time.time()
    r = requests.get("http://localhost:8080/api/v1/data/sound", params={"token":"DEMO CLIENT", "tidyhq_id": str(id)})
    if r.status_code == 200:
        d = r.json()
        print(f"TidyHQ contact <{id}> still has a door sound assigned, attempting download")
        r = requests.get(d["url"])
        h = hashlib.md5(r.content).hexdigest()
        if h == d["hash"]:
            print(f"Downloaded file matches expected hash ({h})")
        else:
            print(f"Expected file with hash {d['hash']} but got {h} instead")
    elif r.status_code == 401:
        print(f"Queried for door sound for contact <{id}> but it's no longer there")
    print(f"Timing: {round(time.time() - t,3)}s")
else:
    print("No contacts with sounds were found, skipping")

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