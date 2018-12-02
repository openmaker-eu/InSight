import time
from pymongo import MongoClient
import pandas as pd
from time import sleep
import string
import numpy as np
import pickle
import requests
from requests_oauthlib import OAuth1
import json
import datetime


key = [["CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]]

auth = OAuth1(key[0][0], key[0][1], key[0][2], key[0][3])

ENDPOINTS = {
	'users_lookup': 'https://api.twitter.com/1.1/users/lookup.json',
	'followers': 'https://api.twitter.com/1.1/followers/ids.json',
	'friends': "https://api.twitter.com/1.1/friends/ids.json",
	'user_timeline': "https://api.twitter.com/1.1/statuses/user_timeline.json"
}

host = "HOST_IP"
MongoDBClient = MongoClient('mongodb://'+'MONGODB_USER'+':'+'MONGODB_PASSWORD'+'@'+host+':27017/', connect=False)
CapsuleCRMdb = MongoDBClient.CapsuleCRMdb

capsuleID_twitterProfile = CapsuleCRMdb.capsuleID_twitterProfile
df_userInfo = pd.DataFrame(list(capsuleID_twitterProfile.find()))
twitter_profile_snaps = CapsuleCRMdb.twitter_profile_snaps

tIDtoCrmID = {}
userIDs = []

for index, row in df_userInfo.iterrows():
	tIDtoCrmID[row["TwitterProfile"]['id']] = row["CapsuleID"]
	userIDs.append(row["TwitterProfile"]['id'])


keyInd = 0
auth = OAuth1(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])

timeNow = time.time()
print(datetime.datetime.fromtimestamp(timeNow).strftime('%Y-%m-%d %H:%M:%S'))

for i in range(int(len(userIDs)/100)+1):
	imin = i*100
	imax = (i+1)*100
	if i == int(len(userIDs)/100):
		imax = len(userIDs)
	while(True):
		params = {'user_id': userIDs[imin : imax]}
		response = requests.get(ENDPOINTS['users_lookup'], auth=auth, params=params)
		if response.status_code == 200:
			for r in response.json():
				mongoDict = {
					"CapsuleID": tIDtoCrmID[r['id']],
					"TwitterProfile": r,
					"DateTime": datetime.datetime.fromtimestamp(timeNow).strftime('%Y-%m-%d %H:%M:%S')
				}
				twitter_profile_snaps.insert_one(mongoDict)
				capsuleID_twitterProfile.update({"TwitterProfile.id_str":r['id_str']}, {"$set":{"TwitterProfile":r}})
			break
		else:
			print(response)
			if response.status_code == 429:
				sleep(60)
				keyInd = (keyInd + 1)%len(key)
			else:
				break
			auth = OAuth1(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])