import requests
from intercom.client import Client
from sqlalchemy import create_engine
import json

USER = ''
PASS = ''
HOST = ''
PORT = ''
DB_NAME = ''

engine = create_engine(f'postgresql+psycopg2://{USER}:{PASS}@{HOST}:{PORT}/{DB_NAME}')

KEY = ''  # Intercom App Key
intercom = Client(personal_access_token=f'{KEY}')

USER_UPDATE_ENDPOINT = 'https://api.intercom.io/users'
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {KEY}'
}

final_user_map = {}
raw_user_map = {}
rows = engine.execute('SELECT legacy_id, id FROM users').fetchall()
​
for row in rows:
    legacy_id = row[0]
    new_id = row[1]
    raw_user_map[int(f'{legacy_id}')] = new_id
​
# Using the intercom-python client scroll intercom and re-write the user_dic key to be the intercom id,
# and value to remain the new id.

for user in intercom.users.scroll():
    try:
        legacy_id = int(user.user_id)
    except:
        continue

    if legacy_id in raw_user_map:
        intercom_id = user.id
        new_id = raw_user_map[legacy_id]
        final_user_map[intercom_id] = new_id
    else:
        print(f'Intercom user_id not in DB (or duplicated) for user {legacy_id}')

print('#### Now updating users, total={0}'.format(len(final_user_map)))
for intercom_id, new_id in final_user_map.items():
    print(f'Treating User {intercom_id} => {new_id}')
    payload = {
        'id': f'{intercom_id}',
        'user_id': f'{new_id}'
    }
    r = requests.post(USER_UPDATE_ENDPOINT, headers=HEADERS, json=payload)
    print(r.status_code)