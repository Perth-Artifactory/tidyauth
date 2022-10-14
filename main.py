#!/usr/bin/python3

import json
import logging

import flask
import requests
from flask import jsonify, request

with open("config.json","r") as f:
    config = json.load(f)

if config["server"]["debug"]:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

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

def pull():
    # Get all contact information from TidyHQ
    logging.debug("Attempting to refresh keys from TidyHQ...")
    try:
        r = requests.get(config["urls"]["contacts"],params={"access_token":config["tidytoken"]})
        contacts = r.json()
    except requests.exceptions.RequestException as e:
        logging.error("Could not reach TidyHQ")
        return False
    return contacts

def process(zone, contacts=None):
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
                    keys[id]["groups"].append("csound")
                    keys[id]["sound"] = door_sound.split(",")

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

    # Generic notification and saving
    logging.debug(f"Updated keys for zone:{zone}, {len(keys)} keys processed")
    backup(zone=zone, mode="w", k=keys)
    return keys

@app.route('/api/v1/<type>/<item>', methods=['GET'])
def config_vending(type,item):
    global data
    zone = f"{item}.{type}"
    if zone not in zones:
        return jsonify({'message':f"{zone} is not a valid zone"}), 401
    token = request.args.get('token')
    up = request.args.get('update')
    if token not in tokens:
        return jsonify({'message':'Send a valid token'}), 401

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
    zones = ["door.keys", "vending.keys", "vending.data"]
    data = {}
    c = pull()
    for zone in zones:
        if zone[-4:] == "keys":
            logging.debug(f"Initial pull for {zone}")
            data[zone] = process(zone=zone, contacts=c)
        else:
            data[zone] = process(zone=zone)
        if not data[zone]:
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
