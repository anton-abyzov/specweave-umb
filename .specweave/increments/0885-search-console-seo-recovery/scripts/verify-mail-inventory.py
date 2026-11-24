import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'reports' / 'mail-inventory.json'
data = json.loads(path.read_text())
rows = data['messages']
assert data['mailbox'] == 'admin@easychamp.com'
assert data['paginationComplete'] is True
assert data['matchingMessages'] == len(rows) == 88
assert len({row['messageId'] for row in rows}) == len(rows)
assert all(row['decoded'] and row['recipientVerified'] for row in rows)
assert sum(data['propertyCounts'].values()) == len(rows)
assert {'easychamp.com', 'spec-weave.com', 'verified-skill.com'} <= set(data['propertyCounts'])
assert 'https://c.gle/' not in path.read_text()
print(f'PASS: {len(rows)} complete decoded notices from verified admin mailbox; no tracking links retained')
