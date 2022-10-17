from datetime import datetime
import requests
import logging
from typing import Dict, List, Tuple

def pull(contact_id: str =None, config: dict =None):
    if contact_id:
        logging.debug(f"Attempting to get contact/{contact_id} info from TidyHQ...")
        try:
            r = requests.get(f"{config['urls']['contacts']}/{contact_id}",params={"access_token":config["tidytoken"]})
            if r.status_code == 200:
                contact = r.json()
                return contact
            return False
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

def find(contact: dict, field_id: str):
    for field in contact["custom_fields"]:
        if field["id"] == field_id:
            if field["value"] != '/file_values/original/missing.png':
                return field["value"]
    return False

def check_membership(contact_id: str = None, config: dict = None) -> bool:
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

def prettyname(contact_id: str, config: dict = None, contacts:list = None) -> str:
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
    return ""

def report_formatter(data: List[dict],dtype: str) -> str:
    html = ""
    mrkdwn = ""

    for section in data:
        # Section title
        html += f'<h2>{section["title"]}</h2>\n'
        mrkdwn += f'## {section["title"]}\n'

        # Explainer paragraph
        html += f'<p>{section["explainer"]}</p>\n'
        mrkdwn += f'{section["explainer"]}\n'

        # Table head
        html += '<table class="table">\n<thead>\n<tr>\n'
        for h in section["table"][0]:
            html += f'<th scope="col">{h}</th>\n'
        html += '</tr>\n</thead>\n<tbody>\n'
        mrkdwn += f'\n|{" | ".join(section["table"][0])}|\n'
        mrkdwn += '|' + '-|' * len(section["table"][0]) + "\n"

        # Table body
        for line in section["table"][1:]:
            html += '<tr>\n'
            for item in line:
                html += f'<td>{item}</td>\n'
            html += '</tr>\n'
            mrkdwn += f'|{" | ".join(line)}|\n'
        html += '</tbody>\n</table>\n'

        # Only add a page break if we have multiple sections
        if len(data) > 1:
            html += "<hr>\n"
            mrkdwn += "---\n"


    if dtype == "mrkdwn":
        return mrkdwn
    elif dtype == "html":
        try:
            with open("report_template.html","r") as f:
                html_wrapper = f.read()
        except FileNotFoundError:
            with open("./scripts/report_template.html","r") as f:
                html_wrapper = f.read()
        return html_wrapper.format(html)


        






    
  
    