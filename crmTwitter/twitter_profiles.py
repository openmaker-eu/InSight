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

def twitterNameFilter(tName):
	if tName[0] == "@":
		return tName[1:]
	elif tName.rfind("/") != -1:
		if tName.find("?") != -1:
			return tName[tName.rfind("/")+1:tName.find("?")]
		else:
			return tName[tName.rfind("/")+1: ]
	elif tName.find(" ") != -1:
		return tName[: tName.find(" ")]
	else:
		return tName


userSnameToCRMid = {}
userCRMids = []
userSname = []

timeNow = time.time()
print(datetime.datetime.fromtimestamp(timeNow).strftime('%Y-%m-%d %H:%M:%S'))

page = 1
header = {'Authorization': "AUTHORIZATION_CREDENTIALS"}

while(True):
	print(page)
	r = requests.get('https://api.capsulecrm.com/api/v2/parties'+"?page="+str(page), headers=header)
	if len(r.json()['parties']) == 0:
		break
	page += 1
	
	for user in r.json()['parties']:
		if str(user['id']) not in list(df_userInfo["CapsuleID"]):
			for web in user['websites']:
				if web['service'] == "TWITTER":
					tName = twitterNameFilter(web['address'])
					userCRMids.append(str(user['id']))
					userSname.append(str(tName))
					break
					
for i, us in enumerate(userSname):
	userSnameToCRMid[us.lower()] = userCRMids[i]



keyInd = 0
auth = OAuth1(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])

userInfo = []

for i in range(int(len(userSname)/100)+1):
	imin = i*100
	imax = (i+1)*100
	if i == int(len(userSname)/100):
		imax = len(userSname)
	while(True):
		params = {'screen_name': userSname[imin : imax]}
		response = requests.get(ENDPOINTS['users_lookup'], auth=auth, params=params)
		if response.status_code == 200:
			for r in response.json():
				if r['id_str'] in list(pd.DataFrame(list(df_userInfo['TwitterProfile']))['id_str']):
					capsuleID_twitterProfile.update({"TwitterProfile.id_str":r['id_str']}, {"$set":{"CapsuleID":userSnameToCRMid[r['screen_name'].lower()]}})
				else:
					capsuleID_twitterProfile.insert_one({"CapsuleID": userSnameToCRMid[r['screen_name'].lower()], "TwitterProfile": r})
					CapsuleCRMdb.twitter_mentions.insert_one({"TwitterID":str(r['id_str']) , "CapsuleID":userSnameToCRMid[r['screen_name'].lower()], "mentioned_to": [], "mentioned_by": []})
				userInfo.append([userSnameToCRMid[r['screen_name'].lower()], r])
			break
		else:
			print(response)
			if response.status_code == 429:
				sleep(60)
				keyInd = (keyInd + 1)%len(key)
			else:
				break
			auth = OAuth1(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])
		
		