import requests

client = MongoClient(host="localhost:1303", port=1303)
db = client.policies
cursor = db.policies.find({"intervention": "1", "auto": "true"})
print cursor
# url = "https://cahl.berkeley.edu:1336/api/email"
#
# r = requests.post(url, data={})
