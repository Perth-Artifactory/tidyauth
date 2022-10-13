#!/usr/bin/python3

import json
import requests
import flask
from flask import request, jsonify

with open("config.json","r") as f:
    config = json.load(f)
    
tokens = config["tokens"]

app = flask.Flask(__name__)

def backup(zone, mode, k=None):
    if mode == "r":
        with open("backup.{}.json".format(zone), mode) as f:
            print("Loading keys from file cache...")
            try:
                k = json.load(f)
            except FileNotFoundError:
                return {}
            except json.decoder.JSONDecodeError:
                return {}
            print("Loaded keys, {} keys found".format(len(k)))
            return k
    
    elif mode == "w":
        with open("backup.{}.json".format(zone), mode) as f:
            json.dump(k,f, indent=4)
            print("{} keys written to backup file: backup.{}.json".format(len(k),zone))
            return True
    return False

def pull():
    # Get all contact information from TidyHQ
    print("Attempting to refresh keys from TidyHQ...")
    try:
        print("Polling TidyHQ")
        r = requests.get(config["contacts_url"],params={"access_token":config["tidytoken"]})
        contacts = r.json()
    except requests.exceptions.RequestException as e:
        print("Could not reach TidyHQ")
        return False
    print("Received response from TidyHQ")
    return contacts

def process(zone, contacts=None):
    if not contacts:
        contacts = pull()

    keys = {}

    # Door specifc processing
    if zone == "door":
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
    elif zone == "vending":
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

    # Generic notification and saving
    print("Updated keys for zone:{}, {} keys processed".format(zone,len(keys)))
    backup(zone=zone, mode="w", k=keys)
    return keys

@app.route('/api/v1/keys/door', methods=['GET'])
def query_door():
    global data
    zone="door"
    token = request.args.get('token')
    up = request.args.get('update')
    if token not in tokens:
        return jsonify({'message':'Send a valid token'}), 401

    if up == "tidyhq":
        k = process(zone=zone)
        if not k:
            return jsonify({'message':'Could not reach TidyHQ'}), 502
        data[zone] = k
    elif up == "file":
        data[zone] = backup(zone=zone, mode="r")

    if data[zone]:
        return jsonify(data[zone])
    else:
        print("No keys in cache, pulling from TidyHQ")
        data[zone] = process(zone=zone)
        return jsonify(data[zone])

@app.route('/api/v1/keys/vending', methods=['GET'])
def api_id():
    global data
    zone="vending"
    token = request.args.get('token')
    up = request.args.get('update')
    if token not in tokens:
        return jsonify({'message':'Send a valid token'}), 401

    if up == "tidyhq":
        k = process(zone=zone)
        if not k:
            return jsonify({'message':'Could not reach TidyHQ'}), 502
        data[zone] = k
    elif up == "file":
        data[zone] = backup(zone=zone, mode="r")

    if data[zone]:
        return jsonify(data[zone])
    else:
        print("No keys in cache, pulling from TidyHQ")
        data[zone] = process(zone=zone)
        return jsonify(data[zone])

@app.route('/', methods=['GET'])
def home():
    return "<h1>Artifactory Auth</h1><p>Authentication for doors and such</p>"

if __name__ == "__main__":
    zones = ["door", "vending"]
    data = {}
    c = pull()
    for zone in zones:
        data[zone] = process(zone=zone, contacts=c)
        if not data[zone]:
            print("Could not pull from TidyHQ, loading file backup")
            data[zone] = backup(zone=zone, mode="r")
        
    from waitress import serve
    print("Auth server starting on {address}:{port}...".format(**config["server"]))
    serve(app, host=config["server"]["address"], port=config["server"]["port"])
