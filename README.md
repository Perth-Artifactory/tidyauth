# TidyHQ key authentication wrapper

This script queries the TidyHQ api for information like access keys.

## Installation

`pip install -r requirements.txt`

## Configuration

* Copy `config.json.example` to `config.json`
* Add TidyHQ information, an easy way to get IDs is from `GET /contacts/me`. Use a trailing space in the name of a drink option to denote sugar free.
* If you want this endpoint to check tokens set ["server"]["debug"] to `true`. Production instances should set this to `false`
* Set your tokens. The server will warn you if you've left example tokens in the file.

## Running

```
./main.py
Attempting to refresh keys from TidyHQ...
Polling TidyHQ
Received response from TidyHQ
Updated keys for zone:door.keys, 5 keys processed
5 keys written to backup file: backup.door.keys.json
Updated keys for zone:vending.keys, 6 keys processed
6 keys written to backup file: backup.vending.keys.json
Attempting to refresh keys from TidyHQ...
Polling TidyHQ
Received response from TidyHQ
Attempting to get option data from TidyHQ...
Polling TidyHQ
Received response from TidyHQ
Auth server starting on 0.0.0.0:8080...
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
		"sound": "cd3d9dd904aca51abc55dbe7b7cc7b28"
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

### Response codes

* 200: Completed successfully
* 401: Invalid token
* 502: Could not reach TidyHQ