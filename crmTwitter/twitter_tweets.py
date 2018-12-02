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
from newspaper import Article
import twitter_news


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
twitter_tweets = CapsuleCRMdb.twitter_tweets

twitter_url_news = CapsuleCRMdb.twitter_url_news
twitter_tweets_news = CapsuleCRMdb.twitter_tweets_news
twitter_mentions = CapsuleCRMdb.twitter_mentions


om_twitter_ids = list(pd.DataFrame(list(twitter_mentions.find({}, {"TwitterID":1, "_id":0})))['TwitterID'])
def add_mentions(tweet_info):
	uid = tweet_info["user"]["id_str"]
	for mention in tweet_info['entities']['user_mentions']:
		if twitter_mentions.find_one({"TwitterID": uid, "mentioned_to.TwitterID": mention['id_str']}) is None:
			twitter_mentions.update_one (
				{"TwitterID": uid }, 
				{"$push": {'mentioned_to': {"TwitterID": mention['id_str'], "count": 1}}}
			)
		else:
			twitter_mentions.update_one (
				{"TwitterID": uid, "mentioned_to.TwitterID": mention['id_str']}, 
				{"$inc": {"mentioned_to.$.count": 1}}
			)

		if mention['id_str'] in om_twitter_ids:
			if twitter_mentions.find_one({"TwitterID": mention['id_str'], "mentioned_by.TwitterID": uid}) is None:
				twitter_mentions.update_one (
					{"TwitterID": mention['id_str'] }, 
					{"$push": {'mentioned_by': {"TwitterID": uid, "count": 1}}}
				)
			else:
				twitter_mentions.update_one (
					{"TwitterID": mention['id_str'], "mentioned_by.TwitterID": uid}, 
					{"$inc": {"mentioned_by.$.count": 1}}
				)


try:
	news_url_list = [u['url'] for u in list(pd.DataFrame(list(twitter_url_news.find({},{"news_info.url":1, "_id":0})))['news_info'])]
	news_id_list = list(pd.DataFrame(list(twitter_url_news.find({},{"news_id":1, "_id":0})))['news_id'])
	max_news_id = int(max(news_id_list))
except:
	news_url_list = []
	news_id_list = []
	max_news_id = 0

try:
	tid_list = list(pd.DataFrame(list(twitter_tweets_news.find({},{"tweet_id":1, "_id":0})))['tweet_id'])
except:
	tid_list = []

new_added_tids = []
new_added_urls = []
new_added_news_ids = []

timeNow = time.time()
print(datetime.datetime.fromtimestamp(timeNow).strftime('%Y-%m-%d %H:%M:%S'))

keyInd = 0
auth = OAuth1(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])


ctr = 0
for uI in df_userInfo["TwitterProfile"]:
	uid = uI['id_str']
	protec = False
	print(str(ctr) + " - " + str(uI['id_str']) + " - " + str(uI['screen_name']))
	ctr+=1
	
	try:
		sinceID = list(twitter_tweets.find({'user.id_str':uid}).sort([("id",-1)]).limit(1))[0]['id']
	except:
		sinceID = 1

	
	while(True):
		params = {"user_id": uid, "count":200, "since_id": sinceID}
		response = requests.get(ENDPOINTS['user_timeline'], auth=auth, params=params)

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
		 
	if protec or len(response.json()) == 0:
		continue
		
	for tweet in response.json():
		twitter_tweets.insert_one(tweet)
		twitter_news.add_tweet_url_info(tweet)
		
	maxID = response.json()[-1]['id']
	
	while(maxID != 0):
		while(True):
			params = {"user_id": uid, "count":200, "max_id":maxID-1, "since_id": sinceID}
			response = requests.get(ENDPOINTS['user_timeline'], auth=auth, params=params)
			break
			
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

		if len(response.json()) == 0:
			break
		
		for tweet in response.json():
			twitter_tweets.insert_one(tweet)
			twitter_news.add_tweet_url_info(tweet)
			add_mentions(tweet)
			
		maxID = response.json()[-1]['id']


