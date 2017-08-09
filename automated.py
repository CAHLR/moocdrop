import csv
import json
import pandas as pd
import sys, getopt, pprint
import pymongo as pg
from pymongo import MongoClient
import requests

url = "https://cahl.berkeley.edu:1336/api/email"
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}

# Adding csv to mongo
csvfile = open('test_pred.csv', 'r')
reader = csv.DictReader(csvfile)
mongo_client = MongoClient(host="localhost:1303", port=1303)
db_pred = mongo_client.predictions
db_pred.pred.drop()
header= ['anon_user_id', 'attrition_prediction', 'completion_prediction', 'certification_prediction']

for each in reader:
    row={}
    for field in header:
        if field != "anon_user_id":
            row[field]= float(each[field])
        else:
            row[field]=each[field]

    db_pred.pred.insert(row)

db_policy = mongo_client.policies
cursor = db_policy.policies.find({"intervention": "true", "auto": "true"})

for p in cursor:
    old_ids = p['ids']

    attr_low = float(p['attr'][0])
    attr_high = float(p['attr'][1])
    comp_low = float(p['comp'][0])
    comp_high = float(p['comp'][1])
    cert_low = float(p['cert'][0])
    cert_high = float(p['cert'][1])

    new_ids = db_pred.pred.find({"$and": [{"attrition_prediction": { "$gte": attr_low }}, {"attrition_prediction": { "$lte": attr_high }}, {"completion_prediction": { "$gte": comp_low }}, {"completion_prediction": { "$lte": comp_high }}, {"certification_prediction": { "$gte": cert_low }}, {"certification_prediction": { "$lte": cert_high }}]})

    for i in new_ids:
        if i['anon_user_id'] not in old_ids:
            print(i)
            updated = old_ids + [i['anon_user_id']]
            db_policy.policies.find_one_and_update({"_id": p['_id']}, {"$set": {"ids":updated}})
            data_to_send = {"pass": "sadfvkn88asVLS891", "ids": [i['anon_user_id']], "body": p['body'], "subject": p['subject'], "reply": p['reply']}
            r = requests.post(url, data=json.dumps(data_to_send), headers=headers)
