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
Loading keys from file cache...
Updated keys, 69 keys found
Attempting to refresh keys from TidyHQ...
Polling TidyHQ
Received response from TidyHQ
Updated keys, 69 keys found
Keys written to backup file
Auth server starting on 0.0.0.0:8080...
```

## Usage

### Testing

A response on `/` is included for route testing purposes.

### Keys

`/api/v1/keys/door`

Pass a token using `token` and (if desired) an update source using `update`. Right now the only valid update sources are `tidyhq` and `file`.

### Response codes

* 200: Completed successfully
* 401: Invalid token
* 502: Could not reach TidyHQ