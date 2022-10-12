# TidyHQ key authentication wrapper

This script queries the TidyHQ api for access key information.

## Installation

`pip install -r requirements.txt`

## Configuration

* Copy `config.json.example` to `config.json`
* Add TidyHQ information, an easy way to get IDs is from `GET /contacts/me`

## Running

```bash
./main.py
Attempting to refresh keys from TidyHQ...
Polling TidyHQ
Received response from TidyHQ
Updated keys for zone:door, 5 keys processed
5 keys written to backup file: backup.door.json
Attempting to refresh keys from TidyHQ...
Polling TidyHQ
Received response from TidyHQ
Updated keys for zone:vending, 6 keys processed
6 keys written to backup file: backup.vending.json
Auth server starting on 0.0.0.0:8080...
```

## Usage

### Testing

A response on `/` is included for route testing purposes.

### Door

`/api/v1/keys/door`

Pass a token using `token` and (if desired) an update source using `update`. Right now the only valid update sources are `tidyhq` and `file`.

TODO: Sample output

### Vending Machine

Pass a token using `token` and (if desired) an update source using `update`. Right now the only valid update sources are `tidyhq` and `file`.

TODO: Sample output

### Response codes

* 200: Completed successfully
* 401: Invalid token
* 502: Could not reach TidyHQ