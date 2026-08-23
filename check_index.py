import json

with open('data/index.json') as f:
    index = json.load(f)

print('Total indexed posts:', len(index))
accounts = {}
for pid, info in index.items():
    user = info['account']
    date = info['date']
    if user not in accounts or date > accounts[user]['date']:
        accounts[user] = {'date': date, 'id': pid}

for user, info in sorted(accounts.items()):
    print(f'  @{user}: {info["id"]} ({info["date"]})')