from datetime import datetime
import requests
import logging

def pull(contact_id=None, config=None):
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

def find(contact, field_id):
    for field in contact["custom_fields"]:
        if field["id"] == field_id:
            if field["value"] != '/file_values/original/missing.png':
                return field["value"]
    return False

def check_membership(contact_id=None, config=None):
    logging.debug(f"Attempting to get contact/{contact_id} info from TidyHQ...")
    try:
        r = requests.get(f"{config['urls']['contacts']}/{contact_id}/memberships",params={"access_token":config["tidytoken"]})
        if r.status_code == 200:
            memberships = r.json()
        else:
            return False
    except requests.exceptions.RequestException as e:
        logging.error("Could not reach TidyHQ")
        return False
    newest = 60000
    for membership in memberships:
        try:
            date = datetime.strptime(membership["end_date"], "%Y-%m-%d")
        except ValueError:
            date = datetime.strptime(membership["end_date"], "%d-%m-%Y")
        since = int((datetime.now()-date).total_seconds()/86400)
        if since < newest:
            newest = int(since)
    if newest < 0:
        return True
    else:
        return False

def prettyname(contact_id, config, contacts=None):
    if not contacts:
        contact = pull(contact_id = contact_id, config = config)
        return "{first_name} {last_name} ({nick_name})".format(**contact)
    contact = False
    for c in contacts:
        if str(c["id"]) == str(contact_id):
            contact = c
    if contact:
        s = f'{contact["first_name"]} {contact["last_name"]}'
        if contact["nick_name"]:
            s += f' ({contact["nick_name"]})'
        return s
    return False