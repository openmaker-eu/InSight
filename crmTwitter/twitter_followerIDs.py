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
twitter_followerIDs = CapsuleCRMdb.twitter_followerIDs
df_twitter_followerIDs = pd.DataFrame(list(twitter_followerIDs.find({})))

def findAddedandDeletedFollowers(uid, followerIDs):
	df_currentUserFollowers = df_twitter_followerIDs[df_twitter_followerIDs["TwitterID"] == uid].sort_values("DateTime")
	#df_currentUserFollowers = pd.DataFrame(list(twitter_followerIDs.find({'TwitterID': uid}).sort([("DateTime",1)])))

	lastFollowerIDs = []

	for index, row in df_currentUserFollowers.iterrows():
		if lastFollowerIDs == []:
			lastFollowerIDs = row['FollowerIDs'].copy()
		else:
			for removed in row['RemovedFollowers']:
				try:
					lastFollowerIDs.remove(int(removed))
				except:
					pass
			for added in row['AddedFollowers']:
				lastFollowerIDs.append(int(added))

	newAdded = list(set(followerIDs) - set(lastFollowerIDs))
	newDeleted = list(set(lastFollowerIDs)  - set(followerIDs))
	
	return newAdded, newDeleted



keyInd = 0
auth = OAuth1(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])

ctr = 0

timeNow = time.time()
print(datetime.datetime.fromtimestamp(timeNow).strftime('%Y-%m-%d %H:%M:%S'))
for uI in df_userInfo["TwitterProfile"]:
	uid = uI['id_str']
	protec = False
	followerIDs = []
	
	print(str(ctr) + " - " + str(uI['id_str']) + " - " + str(uI['screen_name']))
	ctr+=1

	while(True):
		params = {"user_id": uid, "count":5000, "cursor":-1}
		response = requests.get(ENDPOINTS['followers'], auth=auth, params=params)

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
		followerIDs.append([])
		print('protected!')
	else:
		ncur = response.json()['next_cursor']
		followerIDs.extend(response.json()['ids'])

		while(ncur != 0):
			while(True):
				params = {"user_id": uid, "count":5000, "cursor":ncur}
				response = requests.get(ENDPOINTS['followers'], auth=auth, params=params)

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
			followerIDs.extend(response.json()['ids'])
			
		if len(df_twitter_followerIDs[df_twitter_followerIDs["TwitterID"] == uid]) > 0:
			newAdded, newDeleted = findAddedandDeletedFollowers(uid, followerIDs)
			mongoDict = {
				"TwitterID": uid,
				"FollowerIDs": [],
				"AddedFollowers": newAdded,
				"RemovedFollowers": newDeleted,
				"DateTime": datetime.datetime.fromtimestamp(timeNow).strftime('%Y-%m-%d %H:%M:%S')
			}
		else:
			mongoDict = {
				"TwitterID": uid,
				"FollowerIDs": followerIDs,
				"AddedFollowers": [],
				"RemovedFollowers": [],
				"DateTime": datetime.datetime.fromtimestamp(timeNow).strftime('%Y-%m-%d %H:%M:%S')
			}
		try:
			twitter_followerIDs.insert_one(mongoDict)
			print("ADDED")
		except:
			MongoClient('mongodb://'+'{MONGODB_USER}'+':'+'{MONGODB_PASSWORD}'+'@'+host+':27017/', connect=False)			print('CONNECTION PROBLEM')