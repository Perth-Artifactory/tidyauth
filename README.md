# TidyHQ key authentication wrapper

This script queries the TidyHQ api for access key information.

## Installation

`pip install -r requirements.txt`

## Configuration

* Copy `config.json.example` to `config.json`
* Add TidyHQ information, an easy way to get IDs is from `GET /contacts/me`
* If you want this endpoint to check tokens set ["server"]["debug"] to `true`. Production instances should set this to `false`
* Set your tokens. The server will warn you if you've left example tokens in the file.

## Running

```bash
./main.py
Attempting to refresh keys from TidyHQ...
Polling TidyHQ
Received response from TidyHQ
Updated keys for zone:door, 5 keys processed
5 keys written to backup file: backup.door.json
Updated keys for zone:vending, 6 keys processed
6 keys written to backup file: backup.vending.json
Auth server starting on 0.0.0.0:8080...
```

## Usage

### Testing

A response on `/` is included for route testing purposes. It will return `200` if you have provided a valid token or `401` if not.

### Door

`/api/v1/keys/door`

Pass a token using `token` and (if desired) an update source using `update`. Right now the only valid update sources are `tidyhq` and `file`.

```json
{0012345678': {'door': 1,
                'groups': [],
                'name': 'Test McTestington',     
                'tidyhq': 1234567}}
```

### Vending Machine

Pass a token using `token` and (if desired) an update source using `update`. Right now the only valid update sources are `tidyhq` and `file`.

TODO: Sample output

### Response codes

* 200: Completed successfully
* 401: Invalid token
* 502: Could not reach TidyHQ