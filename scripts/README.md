# Report generation and TidyHQ python utilities

## Scripts

### All reports

```bash
all_reports.py [json|html|mrkdwn]

all_reports.py html > report.html
all_reports.py mrkdwn > report.md
all_reports.py json | script.py
```

Generates a combined set of all other reports. Due to a lack of caching this will take a while.

### Template

```bash
template.py
```

Returns a single line containing the total number of contacts in the TidyHQ org specified in `../config.json`. Primarily used as a test to confirm whether a token is valid.

### Lockers

```bash
locker_allocation.py [json|html|mrkdwn|string]

locker_allocation.py html > report.html
locker_allocation.py mrkdwn > report.md
locker_allocation.py json | script.py
```

Returns a sorted report of locker allocations in various formats. If two people are assigned the same locker the person with the higher TidyHQ contact ID will be listed. (Joined later)

```bash
locker_utilisation.py [json|html|mrkdwn|string]

locker_utilisation.py html > report.html
locker_utilisation.py mrkdwn > report.md
locker_utilisation.py json | script.py
```

Returns a summary of locker utilisation sorted by membership status.

### Emergency contact validity

```bash
audit_emergency.py [json|html|mrkdwn|string]

audit_emergency.py html > report.html
audit_emergency.py mrkdwn > report.md
audit_emergency.py json | script.py
```

Returns a report on emergency contacts with basic problems (Missing/invalid number, their own number etc). The report is limited to contacts with at least one membership not marked as expired.

### Membership
```bash
members.py [json|html|mrkdwn|string]

members.py html > report.html
members.py mrkdwn > report.md
members.py json | script.py
```

Returns a summary of membership numbers.

```bash
awaiting_approval.py [json|html|mrkdwn|string]

awaiting_approval.py html > report.html
awaiting_approval.py mrkdwn > report.md
awaiting_approval.py json | script.py
```

Returns a list of prospective members that haven't had their memberships voted on yet.

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