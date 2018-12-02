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
MongoDBClient =MongoClient('mongodb://'+'MONGODB_USER'+':'+'MONGODB_PASSWORD'+'@'+host+':27017/', connect=False)
CapsuleCRMdb = MongoDBClient.CapsuleCRMdb

capsuleID_twitterProfile = CapsuleCRMdb.capsuleID_twitterProfile
df_userInfo = pd.DataFrame(list(capsuleID_twitterProfile.find()))
twitter_friendIDs = CapsuleCRMdb.twitter_friendIDs
df_twitter_friendIDs = pd.DataFrame(list(twitter_friendIDs.find({})))



def findAddedandDeletedFriends(uid, friendIDs):
	df_currentUserFriends = df_twitter_friendIDs[df_twitter_friendIDs["TwitterID"] == uid].sort_values("DateTime")
	#df_currentUserFriends = pd.DataFrame(list(twitter_friendIDs.find({'TwitterID': uid}).sort([("DateTime",1)])))

	lastFriendIDs = []

	for index, row in df_currentUserFriends.iterrows():
		if lastFriendIDs == []:
			lastFriendIDs = row['FriendIDs'].copy()
		else:
			for removed in row['RemovedFriends']:
				try:
					lastFriendIDs.remove(int(removed))
				except:
					pass
			for added in row['AddedFriends']:
				lastFriendIDs.append(int(added))

	newAdded = list(set(friendIDs) - set(lastFriendIDs))
	newDeleted = list(set(lastFriendIDs)  - set(friendIDs))
	
	return newAdded, newDeleted



keyInd = 0
auth = OAuth1(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])

timeNow = time.time()
print(datetime.datetime.fromtimestamp(timeNow).strftime('%Y-%m-%d %H:%M:%S'))
ctr = 0
for uI in df_userInfo["TwitterProfile"]:
	uid = uI['id_str']
	protec = False
	friendIDs = []
	
	print(str(ctr) + " - " + str(uI['id_str']) + " - " + str(uI['screen_name']))
	ctr+=1

	while(True):
		params = {"user_id": uid, "count":5000, "cursor":-1}
		response = requests.get(ENDPOINTS['friends'], auth=auth, params=params)

		if response.status_code == 200:
			break
		else:
			print(response)
			if response.status_code == 429:
				sleep(60)
				keyInd = (keyInd + 1)%len(key)
			else:
				protec = True
				break
			auth = OAuth1(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])

	if protec:
		friendIDs.append([])
		print('protected!')
	else:
		ncur = response.json()['next_cursor']
		friendIDs.extend(response.json()['ids'])

		while(ncur != 0):
			while(True):
				params = {"user_id": uid, "count":5000, "cursor":ncur}
				response = requests.get(ENDPOINTS['friends'], auth=auth, params=params)

				if response.status_code == 200:
					break
				else:
					print(response)
					if response.status_code == 429:
						sleep(60)
						keyInd = (keyInd + 1)%len(key)
					else:
						sleep(15)
					auth = OAuth1(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])

			ncur = response.json()['next_cursor']
			friendIDs.extend(response.json()['ids'])
			
		if len(df_twitter_friendIDs[df_twitter_friendIDs["TwitterID"] == uid]) > 0:
			newAdded, newDeleted = findAddedandDeletedFriends(uid, friendIDs)
			mongoDict = {
				"TwitterID": uid,
				"FriendIDs": [],
				"AddedFriends": newAdded,
				"RemovedFriends": newDeleted,
				"DateTime": datetime.datetime.fromtimestamp(timeNow).strftime('%Y-%m-%d %H:%M:%S')
			}
		else:
			mongoDict = {
				"TwitterID": uid,
				"FriendIDs": friendIDs,
				"AddedFriends": [],
				"RemovedFriends": [],
				"DateTime": datetime.datetime.fromtimestamp(timeNow).strftime('%Y-%m-%d %H:%M:%S')
			}
		try:
			twitter_friendIDs.insert_one(mongoDict)
			print("ADDED")
		except:
			MongoClient('mongodb://'+'{MONGODB_USER}'+':'+'{MONGODB_PASSWORD}'+'@'+host+':27017/', connect=False)
			print('CONNECTION PROBLEM')
		