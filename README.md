# TidyHQ wrapper

This repository contains a server designed to serve cached and live TidyHQ data for use in other tools. It also contains a series of report [generation scripts](/scripts/README.md) that are intended to be run periodically via cron and then disseminated using external resources.

## Installation

`pip install -r requirements.txt`

* Flask/waitress: Serving content
* mutagen: MP3 verification
* phonenumbers: Phone number verification
* requests: Interacting with TidyHQ API
* slack-logger: Slack webhook support for logging
* tabulate: formatting tables

## Configuration

* Copy `config.json.example` to `config.json`
* Add TidyHQ information, an easy way to get IDs is from `GET /contacts/me`. Use a trailing space in the name of a drink option to denote sugar free.
* Set ["server"]["debug"] to `true` if the server does something you don't expect. Production instances should set this to `false`
* Set your auth tokens. The server will warn you if you've left example tokens in the file.

## Running

Run `main.py` directly.

Sample outputs when starting the server and running the example client:

### Normal operation

```
WARNING:root:Demo client token active. Do not use in production!
INFO:waitress:Serving on http://0.0.0.0:8080
INFO:root:127.0.0.1 using token:<DEMO CLIENT> requested cached data for door.keys
INFO:root:127.0.0.1 using token:<DEMO CLIENT> requested a pull from TidyHQ for door.keys
INFO:root:127.0.0.1 using token:<DEMO CLIENT> requested a sound for 1234567
INFO:root:127.0.0.1 using token:<DEMO CLIENT> requested a pull from TidyHQ for vending.keys
INFO:root:127.0.0.1 using token:<DEMO CLIENT> requested a pull from TidyHQ for vending.data
```

### Debug mode

```
DEBUG:root:Attempting to get contact dump from TidyHQ...
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): api.tidyhq.com:443
DEBUG:urllib3.connectionpool:https://api.tidyhq.com:443 "GET /v1/contacts?access_token=TOKEN HTTP/1.1" 200 None
DEBUG:root:Initial pull for door.keys
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): s3.tidyhq.com:443
DEBUG:urllib3.connectionpool:https://s3.tidyhq.com:443 "GET SOUND_URL HTTP/1.1" 200 96139
DEBUG:root:Updated keys for zone:door.keys, 5 keys processed
DEBUG:root:5 keys written to backup file: backup.door.keys.json
DEBUG:root:Initial pull for vending.keys
DEBUG:root:Updated keys for zone:vending.keys, 6 keys processed
DEBUG:root:6 keys written to backup file: backup.vending.keys.json
DEBUG:root:Attempting to get option data from TidyHQ...
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): api.tidyhq.com:443
DEBUG:urllib3.connectionpool:https://api.tidyhq.com:443 "GET /v1//custom_fields/ID?access_token=TOKEN HTTP/1.1" 200 None
DEBUG:root:Updated keys for zone:sound.data, 0 keys processed
DEBUG:root:0 keys written to backup file: backup.sound.data.json
WARNING:root:Debug mode enabled. Do not use in production!
WARNING:root:Demo client token active. Do not use in production!
INFO:waitress:Serving on http://0.0.0.0:8080
INFO:root:127.0.0.1 using token:<DEMO CLIENT> requested cached data for door.keys
INFO:root:127.0.0.1 using token:<DEMO CLIENT> requested a pull from TidyHQ for door.keys
DEBUG:root:Attempting to get contact dump from TidyHQ...
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): api.tidyhq.com:443
DEBUG:urllib3.connectionpool:https://api.tidyhq.com:443 "GET /v1/contacts?access_token=TOKEN HTTP/1.1" 200 None
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): s3.tidyhq.com:443
DEBUG:urllib3.connectionpool:https://s3.tidyhq.com:443 "GET SOUND_URL HTTP/1.1" 200 96139
DEBUG:root:Updated keys for zone:door.keys, 5 keys processed
DEBUG:root:5 keys written to backup file: backup.door.keys.json
DEBUG:root:Attempting to get contact/CONTACT info from TidyHQ...
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): api.tidyhq.com:443
DEBUG:urllib3.connectionpool:https://api.tidyhq.com:443 "GET /v1/contacts/CONTACT?access_token=TOKEN HTTP/1.1" 200 None
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): s3.tidyhq.com:443
DEBUG:urllib3.connectionpool:https://s3.tidyhq.com:443 "GET SOUND URL HTTP/1.1" 200 96139
INFO:root:127.0.0.1 using token:<DEMO CLIENT> requested a sound for CONTACT
INFO:root:127.0.0.1 using token:<DEMO CLIENT> requested a pull from TidyHQ for vending.keys
DEBUG:root:Attempting to get contact dump from TidyHQ...
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): api.tidyhq.com:443
DEBUG:urllib3.connectionpool:https://api.tidyhq.com:443 "GET /v1/contacts?access_token=TOKEN HTTP/1.1" 200 None
DEBUG:root:Updated keys for zone:vending.keys, 6 keys processed
DEBUG:root:6 keys written to backup file: backup.vending.keys.json
INFO:root:127.0.0.1 using token:<DEMO CLIENT> requested a pull from TidyHQ for vending.data
DEBUG:root:Attempting to get option data from TidyHQ...
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): api.tidyhq.com:443
DEBUG:urllib3.connectionpool:https://api.tidyhq.com:443 "GET /v1//custom_fields/FIELD?access_token=TOKEN HTTP/1.1" 200 None
```

## Usage

Pass a token using `token` and (if desired) an update source using `update`. Right now the only valid update sources are `tidyhq` and `file`.

### Testing

A response on `/` is included for route testing purposes. It will return `200` if you have provided a valid token or `401` if not.

### Door

#### Keys

`/api/v1/keys/door`

```json
{
	"0012345678": {
		"door": 1,
		"groups": [],
		"name": "Test McTestington",
		"tidyhq": 1234567
	},
	"0012345442": {
		"door": 1,
		"groups": [],
		"name": "John Smith",
		"tidyhq": 8912345,
		"sound": "cd3d9dd904aca51abc55dbe7b7cc7b28",
		"slack": "UACBE123"
	}
}
```

The `sound` keypair is optional and will only be present if a file has been uploaded to the custom field set via the `sound` parameter. It contains an MD5 hash of the uploaded file.

#### Sounds

`/api/v1/data/sound`

This method will ignore the `update` parameter. It also requires a TidyHQ contact id passed with `tidyhq_id`. This ID is found in all `/api/v1/keys` responses. The intention is that a client only needs to download a sound if the hash has changed.

```json
{"hash": "cd3d9dd904aca51abc55dbe7b7cc7b28",
 "url": "TIDYHQ URL"}
```

### Vending Machine

#### Keys

`/api/v1/keys/vending`

```json
{
	"0008564668": {
		"name": "Test McTestington",
		"tidyhq": 736850
	},
	"0008942641": {
		"drink": "1234567890ab",
		"name": "John Smith",
		"tidyhq": 1234567
	}
}
```

#### Data

`/api/v1/data/door`

```json
{
	"1234567890ab": {
		"name": "Coke",
		"sugar": true
	},
	"cdef12345678": {
		"name": "Coke Zero",
		"sugar": false
	}
}
```

### Lockers

`/api/v1/data/locker`

This method will ignore the `update` parameter. It also requires a TidyHQ contact id passed with `tidyhq_id`. This ID is found in all `/api/v1/keys` responses.

```json
{"locker": "B01"}
```

### Contacts

`/api/v1/keys/contacts`

```json
{"123456": {"name": "John Smith",
             "phone": "0412345678"},
 "123457": {"name": "Jane Smith (J'Dizzle)",
             "phone": "0492112890",
             "slack": "UMM23ZZ8123",
             "tag": "0007781876"}}
```

This method will ignore the `update` parameter. The Slack and key tag fields will only be present if set in TidyHQ

## Response codes

* 200: Completed successfully
* 401: Invalid token or contact ID. Error will be passed as `{"message":"Error"}`
* 502: Could not reach TidyHQ