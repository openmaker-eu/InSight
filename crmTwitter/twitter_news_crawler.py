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


host = "HOST_IP"
MongoDBClient = MongoClient('mongodb://'+'MONGODB_USER'+':'+'MONGODB_PASSWORD'+'@'+host+':27017/', connect=False)
CapsuleCRMdb = MongoDBClient.CapsuleCRMdb



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
	
twitter_tweets = CapsuleCRMdb.twitter_tweets

new_added_tids = []
new_added_urls = []
new_added_news_ids = []



def add_tweet_url_info(df_twitter_tweets):
	for i, row in df_twitter_tweets.iterrows():
		uid = row["user"]["id_str"]
		tid = row["id_str"]
		retweeted_status = -1
		
		if ("retweeted_status" in row) and (not pd.isnull(row['retweeted_status'])):
			row = row["retweeted_status"]
			retweeted_status = {"tweet_id": row["id_str"] , "user_id": row["user"]["id_str"]}
		
		tweet_text = row["text"]

		if (tid not in tid_list) and (tid not in new_added_tids):
			for t_url in row["entities"]["urls"]:
				url = t_url["expanded_url"]
				if (url not in news_url_list) and (url not in new_added_urls): 
					if "twitter.com" not in url:
						try:
							article = Article(url)
							article.download()
							article.parse()
							article.nlp()
						except:
							continue
						   
						news_info =  {
							"url": url,
							"title": article.title,
							"text": article.text,
							"summary": article.summary,
							"authors": article.authors,
							"keywords": article.keywords,
							"publish_date": article.publish_date.__str__()[:19],
							"top_image": article.top_image
						}
						if article.summary != "":
							if len(new_added_news_ids) != 0:
								new_news_id = int(max(new_added_news_ids)) + 1
							else:
								new_news_id = int(max_news_id)+1
							new_added_news_ids.append(new_news_id)
							new_added_urls.append(url)
							new_added_tids.append(tid)  
							print(str(i) + " - " + str(tid))
							
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
					if url in news_url_list:
						news_id = int(news_id_list[news_url_list.index(url)])
					else:
						news_id = int(new_added_news_ids[new_added_urls.index(url)])

					print(str(i) + " - " + str(tid))
						
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




twitter_tweets_count = twitter_tweets.count()
for i in range(103, twitter_tweets_count//1000+1):
	print("page: " + str(i))
	df_twitter_tweets = pd.DataFrame(list(twitter_tweets.find().skip(i*1000).limit(1000)))
	add_tweet_url_info(df_twitter_tweets)
	print()

