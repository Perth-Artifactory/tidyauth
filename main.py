#!/usr/bin/python3
import hashlib
import io
import json
import logging

import flask
import mutagen.mp3
import requests
from flask import jsonify, request
from slack_logger import SlackFormatter, SlackHandler

with open("config.json","r") as f:
    config = json.load(f)

# Set up logging

if config["server"]["debug"]:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

if config["slack_webhook"]:
    sh = SlackHandler(config["slack_webhook"])
    sh.setFormatter(SlackFormatter())
    sh.setLevel(logging.ERROR)
    logging.getLogger('').addHandler(sh)

tokens = config["tokens"]

app = flask.Flask(__name__)

def backup(zone, mode, k=None):
    if mode == "r":
        with open("backup.{}.json".format(zone), mode) as f:
            logging.debug("Loading keys from file cache...")
            try:
                k = json.load(f)
            except FileNotFoundError:
                return {}
            except json.decoder.JSONDecodeError:
                logging.warning(f"backup.{zone}.json has invalid JSON. Has it been edited by something else?")
                return {}
            logging.debug(f"Loaded keys, {len(k)} keys found")
            return k
    
    elif mode == "w":
        with open("backup.{}.json".format(zone), mode) as f:
            json.dump(k,f, indent=4)
            logging.debug(f"{len(k)} keys written to backup file: backup.{zone}.json")
            return True
    return False

def pull(contact_id=None):
    if contact_id:
        logging.debug(f"Attempting to get contact/{contact_id} info from TidyHQ...")
        try:
            r = requests.get(f"{config['urls']['contacts']}/{contact_id}",params={"access_token":config["tidytoken"]})
            contact = r.json()
            return contact
        except requests.exceptions.RequestException as e:
            logging.error("Could not reach TidyHQ")
            return False
    # Get all contact information from TidyHQ
    logging.debug("Attempting to get contact dump from TidyHQ...")
    try:
        r = requests.get(config["urls"]["contacts"],params={"access_token":config["tidytoken"]})
        contacts = r.json()
    except requests.exceptions.RequestException as e:
        logging.error("Could not reach TidyHQ")
        return False
    return contacts

def process(zone, contacts=None, contact_id=None):
    if not contacts and zone[-4:] == "keys":
        contacts = pull()

    keys = {}

    # Door specifc processing
    if zone == "door.keys":
        for person in contacts:
            key = False
            id = ""
            door_sound = ""
            for field in person["custom_fields"]:
                if field["id"] == config["ids"]["status"]:
                    for value in field["value"]:
                        if value["id"] == config["ids"]["enabled"]:
                            key = True
                elif field["id"] == config["ids"]["tag"]:
                    id = field["value"]
                elif field["id"] == config["ids"]["sound"]:
                    door_sound = field["value"]
            if key and id:
                keys[id] = {
                "door": 1,
                "groups": [],
                "name": "{first_name} {last_name}".format(**person),
                "tidyhq": person["id"]}
                if door_sound:
                    if door_sound != '/file_values/original/missing.png':
                        h = fingerprint_sound(url=door_sound, contact_id=person["id"])
                        if h:
                            keys[id]["sound"] = h

    # Vending machine specific processing
    elif zone == "vending.keys":
        for person in contacts:
            drink = ""
            id = ""
            for field in person["custom_fields"]:
                if field["id"] == config["ids"]["tag"]:
                    id = field["value"]
                elif field["id"] == config["ids"]["drink"]:
                    drink = field["value"]["id"]
            if id:
                keys[id] = {"name": "{first_name} {last_name}".format(**person),
                            "tidyhq": person["id"]}
            if drink:
                keys[id]["drink"] = drink
    
    elif zone == "vending.data":
        # Get drink information
        logging.debug("Attempting to get option data from TidyHQ...")
        try:
            r = requests.get(f"{config['urls']['fields']}/{config['ids']['drink']}",params={"access_token":config["tidytoken"]})
            d = r.json()
        except requests.exceptions.RequestException as e:
            logging.error("Could not reach TidyHQ")
            return False
        drinks = {}
        for drink in d["choices"]:
            drinks[drink["id"]] = {"name": drink["title"].strip(),
                                   "sugar": True}
            if drink["title"][-1] == " ":
                drinks[drink["id"]]["sugar"] = False
        return drinks

    elif zone == "sound.data" and contact_id:
        person = pull(contact_id=contact_id)
        if person:
            sound = False
            for field in person["custom_fields"]:
                if field["id"] == config["ids"]["sound"]:
                    if field["value"] != '/file_values/original/missing.png':
                        sound = field["value"]
            if sound:
                return {"url":sound,
                        "hash":fingerprint_sound(url=sound, contact_id=contact_id)}
        return False
    # Generic notification and saving
    logging.debug(f"Updated keys for zone:{zone}, {len(keys)} keys processed")
    backup(zone=zone, mode="w", k=keys)
    return keys

def fingerprint_sound(url,contact_id):
    filename = url.split("/")[-1]
    r = requests.get(url)
    sound = r.content
    if r.status_code == 200:
        try:
            check = mutagen.mp3.MP3(fileobj=io.BytesIO(r.content))
        except mutagen.mp3.HeaderNotFoundError:
            check = False
        if check:
            logging.debug(f"{filename} appears to be a valid mp3")
            return hashlib.md5(sound).hexdigest()
        else:
            logging.error(f"Could not verify {filename} is a valid mp3\nDownload: {url}\nContact: {contact_id}")
            return False
    else:
        logging.error(f"Couldn't download sound: {url}")
        return False

@app.route('/api/v1/<type>/<item>', methods=['GET'])
def send(type,item):
    global data
    zone = f"{item}.{type}"
    if zone not in zones:
        return jsonify({'message':f"{zone} is not a valid zone"}), 401
    token = request.args.get('token')
    up = request.args.get('update')
    contact_id = request.args.get('tidyhq_id')
    if token not in tokens:
        return jsonify({'message':'Send a valid token'}), 401

    if zone == "sound.data":
        if not contact_id:
            logging.debug(f"{request.environ['REMOTE_ADDR']} using token:<{token}> requested a sound without an ID")
            return jsonify({'message':'Pass a TidyHQ contact id as tidyhq_id'}), 401
        s = process(zone=zone, contact_id=contact_id)
        if s:
            logging.info(f"{request.environ['REMOTE_ADDR']} using token:<{token}> requested a sound for {contact_id}")
            return jsonify(s)
        logging.debug(f"{request.environ['REMOTE_ADDR']} using token:<{token}> requested a sound for a contact without one assigned")
        return jsonify({'message':"This contact doesn't have a sound"}), 401

    if up == "tidyhq":
        logging.info(f"{request.environ['REMOTE_ADDR']} using token:<{token}> requested a pull from TidyHQ for {zone}")
        k = process(zone=zone)
        if not k:
            return jsonify({'message':'Could not reach TidyHQ'}), 502
        data[zone] = k
    elif up == "file":
        logging.info(f"{request.environ['REMOTE_ADDR']} using token:<{token}> requested a pull from file for {zone}")
        data[zone] = backup(zone=zone, mode="r")
    else:
        logging.info(f"{request.environ['REMOTE_ADDR']} using token:<{token}> requested cached data for {zone}")

    if data[zone]:
        return jsonify(data[zone])
    else:
        logging.debug("No keys in cache, pulling from TidyHQ")
        data[zone] = process(zone=zone)
        return jsonify(data[zone])

@app.route('/', methods=['GET'])
def home():
    token = request.args.get('token')
    if config["server"]["debug"]:
        if token not in tokens:
            logging.info(f"Invalid token <{token}> from {request.environ['REMOTE_ADDR']}")
            return jsonify({'message':"You've successfuly reached the auth service but need to provide a token to continue"}), 401
        logging.debug(f"Valid token <{token}> from {request.environ['REMOTE_ADDR']} received to test endpoint")
        return jsonify({'message':"You're good to go!"}), 200
    return jsonify({'message':"You're good to go!"}), 200

if __name__ == "__main__":
    logging.info("Starting pre-queries")
    zones = ["door.keys", "vending.keys", "vending.data", "sound.data"]
    data = {}
    c = pull()
    for zone in zones:
        if zone[-4:] == "keys":
            logging.debug(f"Initial pull for {zone}")
            data[zone] = process(zone=zone, contacts=c)
        else:
            data[zone] = process(zone=zone)
        if not data[zone] and zone != "sound.data":
            logging.error("Could not pull from TidyHQ, loading file backup")
            data[zone] = backup(zone=zone, mode="r")
        
    from waitress import serve
    if config["server"]["debug"]:
        logging.warning("Debug mode enabled. Do not use in production!")
    if "DEMO CLIENT" in tokens:
        logging.warning("Demo client token active. Do not use in production!")
    if "List of authentication tokens" in tokens:
        logging.error("Placeholder token active. Do not use in production!")
    serve(app, host=config["server"]["address"], port=config["server"]["port"])
