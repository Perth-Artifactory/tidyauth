# Report generation and TidyHQ python utilities

## Scripts

### Template

```bash
template.py
```

Returns a single line containing the total number of contacts in the TidyHQ org specified in `../config.json`. Primarily used as a test to confirm whether a token is valid.

### Lockers

```bash
locker.py [json|html|mrkdwn|string]

locker.py html > report.html
locker.py mrkdwn > report.md
locker.py json | script.py
```

## Utilities

### Contact retrieval

```python
pull(contact_id: str = None, config: dict)
```
Takes a configuration dictionary (for the TidyHQ token) and an optional TidyHQ contact ID.

Returns a `list` of contacts or a single `dict` if a valid TidyHQ contact ID is passed. 

### Custom field processing

```python
find(contact: dict, field_id: str)
```
TidyHQ custom fields are lists rather dictionaries. This will take a contact `dict` and return the `value` field from the custom field specified with `field_id` if present.

### Active membership check

```python
check_membership(contact_id: str = None, config: dict = None) -> bool:
```
Takes a configuration dictionary (for the TidyHQ token) and a TidyHQ contact ID. Returns `True` if the contact has a current `Active` or `Partial` membership.

### Name formatting

```python
prettyname(contact_id: str, config: dict, contacts:list = None) -> str:
```

Takes a TidyHQ contact ID, an optional configuration dictionary (for the TidyHQ token) and an optional list of contacts. Either the configuration dictionary or the prepulled list of contacts must be passed. Returns a string with the format `"first_name last_name (nickname)"`

### Report formatting

```python
report_formatter(data: List[dict],dtype: str) -> str:
```
Accepts a list of dictionaries containing report sections and an output format. (`html` or `mrkdown`).

Each dictionary in the data list should contain the following keys:

* `title` - The title of the section
* `explainer` - A brief description of the section
* `table` - A 2d list of values. The first row will be treated as the header. There is no requirement for all table rows to have the maximum number of items.

Outputs a string in either markdown or html as appropriate. Page formatting for html is handled by `report_template.html`