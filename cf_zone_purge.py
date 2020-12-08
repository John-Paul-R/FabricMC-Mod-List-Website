
import requests
import json
from dotenv import load_dotenv
import os
import sys

load_dotenv()
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
zones_url = "https://api.cloudflare.com/client/v4/zones"
headers = {
    "Authorization": "Bearer %s" % AUTH_TOKEN,
    # "Content-Type": "application/json"
}
params = {
    "name": "fibermc.com",
    "status": "active",
    "match": "all"
}
def purgeAll():
    r = requests.get(
        zones_url, 
        headers=headers,
        params=params
        )

    resData = r.json()

    data = {"purge_everything": True}
    for zone in resData["result"]:
        post = requests.post("%s/%s/purge_cache" % (zones_url, zone['id']), data=json.dumps(data), headers=headers)
        print(post.json())


if ( len(sys.argv) > 1 and "-run" in sys.argv[1] ):
    purgeAll()

if __name__ == '__main__':
    purgeAll()