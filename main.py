import requests
from time import sleep
import json


def update_status(text):
    input = {
        "input": {
            "client_mutation_id": "1",
            "actor_id": "xxxxx",
            "additional_params": {
                "note_create_params": {
                    "note_style": 0,
                    "text": text
                }
            },
            "audience": 0,
            "inbox_tray_item_type": "note"
        }
    }
    # copy from instagram notes api in browsers network tab
    payload = {
        "variables": str(input).replace("'", '"'),
    }
    headers = {"X-CSRFToken": "PrPsSRd6FcttrKJ2C8hWK9LBjlm7DOfN"}
    # copy from instagram notes api in browsers network tab
    cookies = {}
    s = requests.session()
    s.post("https://www.instagram.com/graphql/query",
           data=payload, headers=headers, cookies=cookies)
    # print(response.status_code,response.text)
    print("set status to ", text)


# create spotify app and pcopy credentials to here
CLIENT_ID = ''
CLIENT_SECRET = ''
TOKEN_FILE = 'tokens.json'


def get_refresh_token():
    # Load the refresh token from file
    with open(TOKEN_FILE, 'r') as token_file:
        tokens = json.load(token_file)
        refresh_token = tokens['refresh_token']

    url = "https://accounts.spotify.com/api/token"
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data['access_token']
        # Use the new refresh token if provided
        refresh_token = response_data.get('refresh_token', refresh_token)

        # Save the new tokens
        tokens['access_token'] = access_token
        tokens['refresh_token'] = refresh_token
        with open(TOKEN_FILE, 'w') as token_file:
            json.dump(tokens, token_file)

        return access_token
    else:
        print("Failed to refresh token:", response.status_code, response.text)
        return None


def fetch_now_playing():
    # Load the access token from file
    with open(TOKEN_FILE, 'r') as token_file:
        tokens = json.load(token_file)
        access_token = tokens['access_token']

    url = "https://api.spotify.com/v1/me/player/currently-playing"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 401:  # Unauthorized error
        print("Access token expired, refreshing token...")
        new_access_token = get_refresh_token()
        if new_access_token:
            headers['Authorization'] = f'Bearer {new_access_token}'
            response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print('Now Playing:', data)
        return data['item']['name']
    else:
        print('Failed to fetch now playing:',
              response.status_code, response.text)
        return "user offline"


old = ""
while True:
    song = fetch_now_playing()
    if song != "user offline":
        song = "Now playing: "+song
    if len(song) > 50:
        song = song[0:50]
    if song != old:
        old = song
        update_status(song)
    sleep(5)
