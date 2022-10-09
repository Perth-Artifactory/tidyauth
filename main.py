#!/usr/bin/python3

import json
import requests
import flask
from flask import request, jsonify

with open("config.json","r") as f:
    config = json.load(f)

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def pull_from_tidyhq():
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
    for person in contacts:
        info = {"bond":0,"note":""}
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
    print("Updated keys, {} keys found".format(len(keys)))
    with open(config["backup"],"w") as f:
        json.dump(keys,f, indent=4)
        print("Keys written to backup file")
    return keys

@app.route('/api/v1/keys/door', methods=['GET'])
def api_id():
    global keys
    token = request.args.get('token')
    up = request.args.get('update')
    if token not in tokens:
        return jsonify({'message':'Send a valid token'}), 401
    if up == "tidyhq":
        k = pull_from_tidyhq()
        if not k:
            return jsonify({'message':'Could not reach TidyHQ'}), 502
        keys = k
    elif up == "file":
        with open(config["backup"],"r") as f:
        keys = json.load(f)
    if keys:
        return jsonify(keys)
    else:
        print("No keys in cache, pulling from TidyHQ")
        keys = pull_from_tidyhq()
        return jsonify(keys)

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
