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

def add_tweet_url_info(twitter_info):
	uid = twitter_info["user"]["id_str"]
	tid = twitter_info["id_str"]
	retweeted_status = -1
	
	if ("retweeted_status" in twitter_info) and (not pd.isnull(twitter_info['retweeted_status'])):
		twitter_info = twitter_info["retweeted_status"]
		retweeted_status = {"tweet_id": twitter_info["id_str"] , "user_id": twitter_info["user"]["id_str"]}
	
	tweet_text = twitter_info["text"]

	if (tid not in tid_list) and (tid not in new_added_tids):
		for t_url in twitter_info["entities"]["urls"]:
			url = t_url["expanded_url"]
			if (url not in news_url_list) and (url not in new_added_urls): 
				print("New News")
				if "twitter.com" not in url:
					try:
						article = Article(url)
						article.download()
						article.parse()
						news_info =  {
							"url": url,
							"title": article.title,
							"text": article.text,
							"summary": "",
							"authors": article.authors,
							"keywords": [],
							"publish_date": article.publish_date.__str__()[:19],
							"top_image": article.top_image
						}
					except:
						continue

					try:
						article.nlp()
						news_info["summary"] = article.summary,
						news_info["keywords"] = article.keywords
					except:
						pass
					   
					
					if article.text != "":
						if len(new_added_news_ids) != 0:
							new_news_id = int(max(new_added_news_ids)) + 1
						else:
							new_news_id = int(max_news_id)+1
						new_added_news_ids.append(new_news_id)
						new_added_urls.append(url)
						new_added_tids.append(tid)  
						print(str(new_news_id))
						
						try:
							twitter_url_news.insert_one({"news_id": new_news_id, "news_info": news_info})
						except:
							CapsuleCRMdb.twitter_url_news.insert_one({"news_id": new_news_id, "news_info": news_info})
							
						try:
							if retweeted_status == -1:
								twitter_tweets_news.insert_one({"news_id": new_news_id, "tweet_id": tid, "user_id": uid})
							else:
								twitter_tweets_news.insert_one({"news_id": new_news_id, "tweet_id": tid, "user_id": uid, "retweeted_status": retweeted_status})
						except:
							if retweeted_status == -1:
								CapsuleCRMdb.twitter_tweets_news.insert_one({"news_id": new_news_id, "tweet_id": tid, "user_id": uid})
							else:
								CapsuleCRMdb.twitter_tweets_news.insert_one({"news_id": new_news_id, "tweet_id": tid, "user_id": uid, "retweeted_status": retweeted_status})
								
			else:
				new_added_tids.append(tid)
				print("Old News")
				if url in news_url_list:
					news_id = int(news_id_list[news_url_list.index(url)])
				else:
					news_id = int(new_added_news_ids[new_added_urls.index(url)])
					
				try:
					if retweeted_status == -1:
						twitter_tweets_news.insert_one({"news_id": news_id, "tweet_id": tid, "user_id": uid})
					else:
						twitter_tweets_news.insert_one({"news_id": news_id, "tweet_id": tid, "user_id": uid, "retweeted_status": retweeted_status})
				except:
					if retweeted_status == -1:
						CapsuleCRMdb.twitter_tweets_news.insert_one({"news_id": news_id, "tweet_id": tid, "user_id": uid})
					else:
						CapsuleCRMdb.twitter_tweets_news.insert_one({"news_id": news_id, "tweet_id": tid, "user_id": uid, "retweeted_status": retweeted_status})


