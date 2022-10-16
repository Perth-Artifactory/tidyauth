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