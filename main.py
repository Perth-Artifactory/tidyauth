#!/usr/bin/python3

import json
import requests
import flask
from flask import request, jsonify

with open("config.json","r") as f:
    config = json.load(f)
    
tokens = config["tokens"]

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def pull_from_tidyhq(zone):
    
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
                elif field["id"] == config["ids"]["drink"] or field["id"] == "6ad83ec447fc":
                    drink = field["value"]["id"]
            if id:
                keys[id] = {"name": "{first_name} {last_name}".format(**person),
                            "tidyhq": person["id"]}
            if drink:
                keys[id]["drink"] = drink

    # Generic notification and saving
    print("Updated keys for zone:{}, {} keys found".format(zone,len(door_keys)))
    with open(config["backup.{}.json".format(zone)],"w") as f:
        json.dump(keys,f, indent=4)
        print("Keys written to backup file: backup.{}.json".format(zone))
    return keys

@app.route('/api/v1/keys/door', methods=['GET'])
def query_door():
    global door_keys
    token = request.args.get('token')
    up = request.args.get('update')
    if token not in tokens:
        return jsonify({'message':'Send a valid token'}), 401
    if up == "tidyhq":
        k = pull_from_tidyhq(zone="door")
        if not k:
            return jsonify({'message':'Could not reach TidyHQ'}), 502
        door_keys = k
    elif up == "file":
        with open("backup.door.json","r") as f:
            door_keys = json.load(f)
    if door_keys:
        return jsonify(door_keys)
    else:
        print("No keys in cache, pulling from TidyHQ")
        keys = pull_from_tidyhq(zone="door")
        return jsonify(door_keys)

@app.route('/api/v1/keys/vending', methods=['GET'])
def api_id():
    global vend_keys
    token = request.args.get('token')
    up = request.args.get('update')
    if token not in tokens:
        return jsonify({'message':'Send a valid token'}), 401
    if up == "tidyhq":
        k = pull_from_tidyhq(zone="vending")
        if not k:
            return jsonify({'message':'Could not reach TidyHQ'}), 502
        vend_keys = k
    elif up == "file":
        with open("backup.vending.json","r") as f:
            vend_keys = json.load(f)
    if vend_keys:
        return jsonify(vend_keys)
    else:
        print("No keys in cache, pulling from TidyHQ")
        vend_keys = pull_from_tidyhq(zone="vending")
        return jsonify(vend_keys)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Artifactory Auth</h1><p>Authentication for doors and such</p>"

if __name__ == "__main__":
    from waitress import serve
    keys = {}
    print("Loading keys from file cache...")
    with open(config["backup"],"r") as f:
        keys = json.load(f)
    print("Updated keys, {} keys found".format(len(keys)))
    k = pull_from_tidyhq()
    if k:
        keys = k
    print("Auth server starting on {address}:{port}...".format(**config["server"]))
    serve(app, host=config["server"]["address"], port=config["server"]["port"])
