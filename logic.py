from application.Connections import Connection
from datetime import date
import time
import datetime
import numpy as np
import pandas as pd

import plotly.offline
import plotly.graph_objs as go

import matplotlib.pyplot as plt

import plotly.plotly as py
import plotly.tools as tls

from collections import Counter

import mpld3

from newspaper import Article

from nltk.corpus import wordnet

import requests
from requests_oauthlib import OAuth1
import json
import random
import copy
import math

watchTowerIP = "https://watchtower.openmaker.eu"
watchTowerPort = ""
watchTowerVersion = "v1.3"
watchTowerSetting = watchTowerIP + watchTowerPort + "/api/" + watchTowerVersion

insight_api_key = "INSIGHT_API_KEY"
idPerPage = 1000
tweetPerPage = 100
profilePerPage = 50
contentPerPage = 20


feedback_types = {'news': {'Dislike':0, "Neutral":1, "Like":2}, 'event': {'Dislike':0, "Neutral":1, "Like":2}}
context_types = {"news": 1, "event": 2, "other": 0}
# if content_id == 0 then no spesific content info given


def post_registered_user(crm_id):
	# Get user from Capsule CRM

	header = {'Authorization': "AUTHORIZATION_CREDENTIALS"}
	r = requests.get('https://api.capsulecrm.com/api/v2/parties/'+str(crm_id)+'?embed=tags,fields,organisation', headers=header)
	if 'party' not in r.json():
		return {'error': 'user is not in Capsule CRM'}
	user = r.json()['party']

	if list(Connection.Instance().CapsuleCRMdb.om_user_profiles.find({"capsule_profile.id": int(crm_id)})) == []:
		Connection.Instance().CapsuleCRMdb.om_user_profiles.insert_one({"capsule_profile":user})
		Connection.Instance().CapsuleCRMdb.om_user_profiles.update_one({"capsule_profile.id":user['id']}, {"$set":{"extra_info":[]}})
	else:
		Connection.Instance().CapsuleCRMdb.om_user_profiles.update_one({"capsule_profile.id":user['id']}, {"$set":{"capsule_profile":user}})

	# Make Recommendation

	r = requests.get(watchTowerSetting + "/get_topics")
	topic_list = r.json()['topics']

	# wt_topic_ids = [t["topic_id"] for t in topic_list]
	# np.random.shuffle(wt_topic_ids)
	# wt_topic_ids = wt_topic_ids[:3]
	# Connection.Instance().CapsuleCRMdb.om_user_properties.update_one({"CapsuleID":str(user['id']) },{"$set" : {"wt_topic_ids": wt_topic_ids}}, upsert=True)

	u_inf = {'tags':user["tags"], 'fields':user["fields"]}

	wt_topics = {t["topic_name"]:{'interest':0, 'topic_id':t["topic_id"]} for t in topic_list}
	u_wt_topics = copy.deepcopy(wt_topics)
	for tag in u_inf['tags']:
		r = requests.get(watchTowerSetting + "/get_topics?keywords="+tag['name'])
		for t in r.json()['topics']:
			u_wt_topics[t['topic_name']]['interest'] += 1
	Connection.Instance().CapsuleCRMdb.om_user_properties.update_one({"CapsuleID":str(user['id']) },{"$set" : {"wt_topics": u_wt_topics}}, upsert=True)


	# news and events recommendations

	empty_topic_counts = [[1, t['topic_id']] for t in topic_list]

	temp_content_table = pd.DataFrame(list(Connection.Instance().CapsuleCRMdb.temp_content_table.find({},{'_id':0,'temp_id':1,'topic_id':1,'content_type':1})))
	topic_counts = []
	for t_name, t_info in u_wt_topics.items():
		if t_info['interest'] > 0:
			topic_counts.append([t_info['interest'], t_info['topic_id']])
	
	if topic_counts == []:
		topic_counts = copy.deepcopy(empty_topic_counts)
			
	topic_contents = temp_content_table[temp_content_table.topic_id.isin([t[1] for t in topic_counts])]
	news_topic_contents = topic_contents[topic_contents.content_type == "news"]
	event_topic_contents = topic_contents[topic_contents.content_type == "event"]
	
	
	# NEWS Recommendation

	news_temp_ids = []
	ctr = 0
	mtp = 0
	
	topic_counts = sorted(topic_counts,reverse=True)
	while ctr < 100:
		ctr_x = ctr
		for t in topic_counts:
			tids = list(news_topic_contents[news_topic_contents.topic_id==t[1]]['temp_id'][mtp*t[0] : (mtp+1)*t[0]])
			news_temp_ids.extend(tids)
			ctr += len(tids)
		if ctr == ctr_x:
			break
		mtp += 1

	# EVENTS Recommendation
	event_temp_ids = []
	ctr = 0
	mtp = 0
	
	topic_counts = sorted(topic_counts,reverse=True)
	while ctr < 50:
		ctr_x = ctr
		for t in topic_counts:
			tids = list(event_topic_contents[event_topic_contents.topic_id==t[1]]['temp_id'][mtp*t[0] : (mtp+1)*t[0]])
			event_temp_ids.extend(tids)
			ctr += len(tids)
		if ctr == ctr_x:
			break
		mtp += 1

	try:
		news_temp_ids = [np.asscalar(_id) for _id in news_temp_ids]
		event_temp_ids = [np.asscalar(_id) for _id in event_temp_ids]
	except:
		pass
	
	Connection.Instance().CapsuleCRMdb.om_user_analytics.update_one({"CapsuleID":str(user['id']) },{"$set" : {"recommended_news": news_temp_ids,"recommended_events": event_temp_ids}},upsert=True)

	# user to user recommendation

	user_ids = [str(x["capsule_profile"]["id"]) for x in list(Connection.Instance().CapsuleCRMdb.om_user_profiles.find())]
	np.random.shuffle(user_ids)
	Connection.Instance().CapsuleCRMdb.om_user_analytics.update_one({"CapsuleID":str(user['id']) },{"$set" : {"recommended_users":user_ids[:10]}})

	return {'success': 'user information and recommendations are added/updated'}


def get_synonyms(word, synsets):
	synonyms = []
	for synset in synsets:
		synonyms += [str(lemma.name()) for lemma in synset.lemmas()]

	synonyms = [synonym.replace("_", " ") for synonym in synonyms]
	synonyms = list(set(synonyms))
	synonyms = [synonym for synonym in synonyms if synonym != word]

	return synonyms


def get_antonyms(word, synsets):
	antonyms = []
	for syn in synsets:
		for l in syn.lemmas():
			if l.antonyms():
				antonyms += [str(lemma.name()) for lemma in l.antonyms()]
		
	antonyms = [antonym.replace("_", " ") for antonym in antonyms]
	antonyms = list(set(antonyms))
	antonyms = [antonym for antonym in antonyms if antonym != word]

	return antonyms

def get_synonym_antonym(word, pos):
	wordnet_pos = {
		"noun": wordnet.NOUN,
		"verb": wordnet.VERB,
		"adj": wordnet.ADJ,
		"adv": wordnet.ADV
	}
	if pos:
		synsets = wordnet.synsets(word, pos=wordnet_pos[pos])
	else:
		synsets = wordnet.synsets(word)

	synonyms = get_synonyms(word, synsets)
	antonyms = get_antonyms(word, synsets)
	
	return {'word':word, 'pos':pos, 'synonyms': synonyms, 'antonyms': antonyms}


def url_scraper(url):
	try:
		article = Article(url)
		article.download()
		article.parse()
		news_info =  {
			"url": url,
			"title": article.title,
			"text": article.text,
			"summary": "",
			#"authors": article.authors,
			"keywords": [],
			"publish_date": article.publish_date.__str__()[:19],
			#"top_image": article.top_image
		}
	except:
		news_info =  {
			"Error": "Content Not Found"
		}

	try:
		article.nlp()
		news_info["summary"] = article.summary,
		news_info["keywords"] = article.keywords
	except:
		pass

	return news_info
		

def check_api_key(api_key):
	return api_key == insight_api_key

def get_twitter_mentions(_id,isTwitterID):
	capsuleID_twitterProfile = Connection.Instance().CapsuleCRMdb.capsuleID_twitterProfile

	if isTwitterID:
		twitterID = _id
		try:
			crmID = list(capsuleID_twitterProfile.find({'TwitterProfile.id_str':_id}))[0]["CapsuleID"]
		except:
			crmID = -1
			return twitterID, crmID, [], []
			
	else:
		crmID = _id
		try:
			twitterID = list(capsuleID_twitterProfile.find({'CapsuleID':_id}))[0]["TwitterProfile"]["id_str"]
		except:
			twitterID = -1
			return twitterID, crmID, [], []

	mention_info = Connection.Instance().CapsuleCRMdb.twitter_mentions.find_one({"TwitterID": twitterID})
	return mention_info["TwitterID"], mention_info["CapsuleID"], mention_info["mentioned_to"], mention_info["mentioned_by"]


def get_om_user_profiles(page,sorting,descending,filters):
	om_user_profiles = Connection.Instance().CapsuleCRMdb.om_user_profiles

	possible_filters = ["min_followers", "max_followers", "min_tweets", "max_tweets"]
	filter_keys = list(filters.keys())

	filter_str = ""

	if "min_followers" in filter_keys and "max_followers" in filter_keys:
		filter_str += "'twitter_profile.followers_count': {'$gte':"+str(filters["min_followers"])+", '$lte':"+str(filters["max_followers"])+"},"
	elif "min_followers" in filter_keys:
		filter_str += "'twitter_profile.followers_count': {'$gte':"+str(filters["min_followers"])+"},"
	elif "max_followers" in filter_keys:
		filter_str += "'twitter_profile.followers_count': {'$lte':"+str(filters["max_followers"])+"},"

	if "min_tweets" in filter_keys and "max_tweets" in filter_keys:
		filter_str += "'twitter_profile.statuses_count': {'$gte':"+str(filters["min_tweets"])+", '$lte':"+str(filters["max_tweets"])+"},"
	elif "min_tweets" in filter_keys:
		filter_str += "'twitter_profile.statuses_count': {'$gte':"+str(filters["min_tweets"])+"},"
	elif "max_tweets" in filter_keys:
		filter_str += "'twitter_profile.statuses_count': {'$lte':"+str(filters["max_tweets"])+"},"


	filter_str = '{' + filter_str[:-1] +  '}'
	filter_str = eval(filter_str)

	result = om_user_profiles.find(filter_str,  {"_id":0})

	if descending:
		order = -1
	else:
		order = 1

	
	if sorting == "c_date":
		result = result.sort([("capsule_profile.createdAt",order)])
	if sorting == "c_alphabetical":
		result = result.sort([("capsule_profile.name",order), ("capsule_profile.firstName",order)])
	if sorting == "t_followers":
		result = result.sort([("twitter_profile.followers_count",order)])
	if sorting == "t_tweets":
		result = result.sort([("twitter_profile.statuses_count",order)])

	return list(result[(page-1)*profilePerPage : page*profilePerPage])

def get_om_user_profiles2(_id,isTwitterID):
	om_user_profiles = Connection.Instance().CapsuleCRMdb.om_user_profiles

	if isTwitterID:
		twitterID = _id
		try:
			profile = om_user_profiles.find_one({'twitter_profile.id_str':str(_id)})
			crmID = profile['capsule_profile']['id']
		except:
			crmID = -1
			return {"twitter_id":twitterID, "crm_id":str(crmID), "twitter_profile":[], "capsule_profile":[], "extra_info":[]}
			
	else:
		crmID = _id
		try:
			profile = om_user_profiles.find_one({'capsule_profile.id':int(_id)})
			try:
				twitterID = profile['twitter_profile']['id_str']
			except:
				twitterID = -1
				return {"twitter_id":twitterID, "crm_id":str(crmID), "twitter_profile":[], "capsule_profile":profile['capsule_profile'], "extra_info":profile['extra_info']}
		except:
			twitterID = -1
			return {"twitter_id":twitterID, "crm_id":crmID, "twitter_profile":[], "capsule_profile":[], "extra_info":[]}



	return {"twitter_id":twitterID, "crm_id":str(crmID), "twitter_profile":profile['twitter_profile'], "capsule_profile":profile['capsule_profile'], "extra_info":profile['extra_info']}




def get_twitter_news(_id,page,isTwitterID):
	capsuleID_twitterProfile = Connection.Instance().CapsuleCRMdb.capsuleID_twitterProfile

	if isTwitterID:
		twitterID = _id
		try:
			crmID = list(capsuleID_twitterProfile.find({'TwitterProfile.id_str':_id}))[0]["CapsuleID"]
		except:
			crmID = -1
			return twitterID, crmID, []
			
	else:
		crmID = _id
		try:
			twitterID = list(capsuleID_twitterProfile.find({'CapsuleID':_id}))[0]["TwitterProfile"]["id_str"]
		except:
			twitterID = -1
			return twitterID, crmID, []


	twitter_tweets_news = Connection.Instance().CapsuleCRMdb.twitter_tweets_news

	try:
		news_ids = list(set(pd.DataFrame(list(twitter_tweets_news.find({"user_id": twitterID}, {"news_id":1, "_id":0})))["news_id"]))[(page-1)*tweetPerPage:page*tweetPerPage]
	except:
		return twitterID, crmID, []

	twitter_url_news = Connection.Instance().CapsuleCRMdb.twitter_url_news

	news_list = []
	for nid in news_ids:
		try:
			news_list.append(list(pd.DataFrame(list(twitter_url_news.find({"news_id": int(nid)}, {"news_info":1, "_id":0})))["news_info"])[0])
		except:
			pass

	return twitterID, crmID, news_list



def twitter_id_to_crm_id(twitter_id):
	capsuleID_twitterProfile = Connection.Instance().CapsuleCRMdb.capsuleID_twitterProfile
	try:
		crmID = list(capsuleID_twitterProfile.find({'TwitterProfile.id_str':twitter_id}))[0]["CapsuleID"]
	except:
		crmID = -1
	return crmID


def crm_id_to_twitter_id(crmID):
	capsuleID_twitterProfile = Connection.Instance().CapsuleCRMdb.capsuleID_twitterProfile
	try:
		twitterID = list(capsuleID_twitterProfile.find({'CapsuleID':crmID}))[0]["TwitterProfile"]["id_str"]
	except:
		twitterID = -1
	return twitterID


def get_twitter_profiles(_id,isTwitterID):
	capsuleID_twitterProfile = Connection.Instance().CapsuleCRMdb.capsuleID_twitterProfile

	if isTwitterID:
		twitterID = _id
		try:
			crmID = list(capsuleID_twitterProfile.find({'TwitterProfile.id_str':_id}))[0]["CapsuleID"]
		except:
			crmID = -1
	else:
		crmID = _id
		try:
			twitterID = list(capsuleID_twitterProfile.find({'CapsuleID':_id}))[0]["TwitterProfile"]["id_str"]
		except:
			twitterID = -1

	twitter_profile_snaps = Connection.Instance().CapsuleCRMdb.twitter_profile_snaps
	try:
		twitterProfile = list(twitter_profile_snaps.find({'CapsuleID': crmID}).sort([("DateTime",-1)]))[0]["TwitterProfile"]
	except:
		twitterProfile = -1

	return twitterID, crmID, twitterProfile



def get_twitter_followers(_id,from_date,to_date,page,isTwitterID,only_crm_users):
	capsuleID_twitterProfile = Connection.Instance().CapsuleCRMdb.capsuleID_twitterProfile

	if isTwitterID:
		twitterID = _id
		try:
			crmID = list(capsuleID_twitterProfile.find({'TwitterProfile.id_str':_id}))[0]["CapsuleID"]
		except:
			crmID = -1
			return twitterID, crmID, [], []
			
	else:
		crmID = _id
		try:
			twitterID = list(capsuleID_twitterProfile.find({'CapsuleID':_id}))[0]["TwitterProfile"]["id_str"]
		except:
			twitterID = -1
			return twitterID, crmID, [], []


	twitter_followerIDs = Connection.Instance().CapsuleCRMdb.twitter_followerIDs

	followerIDs = []
	capsuleIDs = []

	try:
		df_followerChange = pd.DataFrame(list(twitter_followerIDs.find({'TwitterID': twitterID}).sort([("DateTime",1)])))
		if from_date != "-1":
			df_followerChange = df_followerChange[df_followerChange.DateTime >= from_date]
		if to_date != "-1":
			df_followerChange = df_followerChange[df_followerChange.DateTime <= to_date]

		for index, row in df_followerChange.iterrows():
			if followerIDs == [] and len(row['FollowerIDs']) > 0:
				followerIDs = row['FollowerIDs'].copy()
			else:
				for removed in row['RemovedFollowers']:
					try:
						followerIDs.remove(int(removed))
					except:
						pass
				for added in row['AddedFollowers']:
					followerIDs.append(int(added))

		user_ids = {str(x["TwitterProfile"]["id_str"]): str(x["CapsuleID"]) for x in list(capsuleID_twitterProfile.find())}
		if only_crm_users:
			cfids = []
			ccids = []
			for fid in followerIDs:
				if str(fid) in user_ids:
					capsuleID = user_ids[str(fid)]
					cfids.append(str(fid))
					ccids.append(str(capsuleID))
			return twitterID, crmID, cfids, ccids
		else:
			for fid in followerIDs[(page-1)*idPerPage:page*idPerPage]:
				if str(fid) in user_ids:
					capsuleID = user_ids[str(fid)]
				else:
					capsuleID = -1
				capsuleIDs.append(str(capsuleID))
		
	except:
		followerIDs = []
		capsuleIDs = []
		
	return twitterID, crmID, followerIDs[(page-1)*idPerPage:page*idPerPage], capsuleIDs


def get_twitter_friends(_id,from_date,to_date,page,isTwitterID,only_crm_users):
	capsuleID_twitterProfile = Connection.Instance().CapsuleCRMdb.capsuleID_twitterProfile

	if isTwitterID:
		twitterID = _id
		try:
			crmID = list(capsuleID_twitterProfile.find({'TwitterProfile.id_str':_id}))[0]["CapsuleID"]
		except:
			crmID = -1
			return twitterID, crmID, [], []
			
	else:
		crmID = _id
		try:
			twitterID = list(capsuleID_twitterProfile.find({'CapsuleID':_id}))[0]["TwitterProfile"]["id_str"]
		except:
			twitterID = -1
			return twitterID, crmID, [], []


	df_capsuleID_twitterProfile = pd.DataFrame(list(capsuleID_twitterProfile.find({})))
	twitter_friendIDs = Connection.Instance().CapsuleCRMdb.twitter_friendIDs

	friendIDs = []
	capsuleIDs = []

	try:
		df_friendChange = pd.DataFrame(list(twitter_friendIDs.find({'TwitterID': twitterID}).sort([("DateTime",1)])))
		if from_date != "-1":
			df_friendChange = df_friendChange[df_friendChange.DateTime >= from_date]
		if to_date != "-1":
			df_friendChange = df_friendChange[df_friendChange.DateTime <= to_date]

		for index, row in df_friendChange.iterrows():
			if friendIDs == [] and len(row['FriendIDs']) > 0:
				friendIDs = row['FriendIDs'].copy()
			else:
				for removed in row['RemovedFriends']:
					try:
						friendIDs.remove(int(removed))
					except:
						pass
				for added in row['AddedFriends']:
					friendIDs.append(int(added))
					

		user_ids = {str(x["TwitterProfile"]["id_str"]): str(x["CapsuleID"]) for x in list(capsuleID_twitterProfile.find())}
		if only_crm_users:
			cfids = []
			ccids = []
			for fid in friendIDs:
				if str(fid) in user_ids:
					capsuleID = user_ids[str(fid)]
					cfids.append(str(fid))
					ccids.append(str(capsuleID))
			return twitterID, crmID, cfids, ccids
		else:
			for fid in friendIDs[(page-1)*idPerPage:page*idPerPage]:
				if str(fid) in user_ids:
					capsuleID = user_ids[str(fid)]
				else:
					capsuleID = -1
				capsuleIDs.append(str(capsuleID))
		
		
	except:
		friendIDs = []
		capsuleIDs = []
		
	return twitterID, crmID, friendIDs[(page-1)*idPerPage:page*idPerPage], capsuleIDs



def get_twitter_tweets(_id,page,isTwitterID):
	capsuleID_twitterProfile = Connection.Instance().CapsuleCRMdb.capsuleID_twitterProfile

	if isTwitterID:
		twitterID = _id
		try:
			crmID = list(capsuleID_twitterProfile.find({'TwitterProfile.id_str':_id}))[0]["CapsuleID"]
		except:
			crmID = -1
	else:
		crmID = _id
		try:
			twitterID = list(capsuleID_twitterProfile.find({'CapsuleID':_id}))[0]["TwitterProfile"]["id_str"]
		except:
			twitterID = -1

	twitter_tweets = Connection.Instance().CapsuleCRMdb.twitter_tweets
	try:
		twitterID = list(capsuleID_twitterProfile.find({'CapsuleID': crmID}))[0]["TwitterProfile"]["id_str"]
		tweets = list(twitter_tweets.find({'user.id_str': twitterID},{'_id': 0}).sort([("id",-1)]).skip((page-1)*tweetPerPage).limit(tweetPerPage))
	except:
		tweets = []
	return twitterID, crmID, tweets




def get_tnc_twitter_profiles(dbID):
	db = Connection.Instance().tnc_dbs[dbID]

	try:
		twitterProfile = list(db.twitter_profile.find({},{'_id': 0}))
	except:
		twitterProfile = -1

	return twitterProfile

def get_tnc_twitter_followers(dbID, from_date,to_date):
	db = Connection.Instance().tnc_dbs[dbID]

	twitter_followerIDs = db.twitter_followerIDs
	df_twitter_followerIDs = pd.DataFrame(list(twitter_followerIDs.find({})))
	twitter_profile = db.twitter_profile
	df_userInfo = pd.DataFrame(list(twitter_profile.find()))

	followerIDs = []
	for uid in list(df_userInfo['id_str']):
		df_currentUserFollowers = df_twitter_followerIDs[df_twitter_followerIDs["TwitterID"] == uid].sort_values("DateTime")
		if from_date != "-1":
			df_currentUserFollowers = df_currentUserFollowers[df_currentUserFollowers.DateTime >= from_date]
		if to_date != "-1":
			df_currentUserFollowers = df_currentUserFollowers[df_currentUserFollowers.DateTime <= to_date]
			

		lastFollowerIDs = []

		for index, row in df_currentUserFollowers.iterrows():
			if lastFollowerIDs == [] and len(row['FollowerIDs']) > 0:
				lastFollowerIDs = row['FollowerIDs'].copy()
			else:
				for removed in row['RemovedFollowers']:
					try:
						lastFollowerIDs.remove(int(removed))
					except:
						pass
				for added in row['AddedFollowers']:
					lastFollowerIDs.append(int(added))

		followerIDs.append({"twitter_id":uid, "follower_ids":lastFollowerIDs})

		
	return followerIDs


def get_tnc_twitter_friends(dbID, from_date,to_date):
	db = Connection.Instance().tnc_dbs[dbID]

	twitter_friendIDs = db.twitter_friendIDs
	df_twitter_friendIDs = pd.DataFrame(list(twitter_friendIDs.find({})))
	twitter_profile = db.twitter_profile
	df_userInfo = pd.DataFrame(list(twitter_profile.find()))

	friendIDs = []

	for uid in list(df_userInfo['id_str']):
		df_currentUserFriends = df_twitter_friendIDs[df_twitter_friendIDs["TwitterID"] == uid].sort_values("DateTime")
		if from_date != "-1":
			df_currentUserFriends = df_currentUserFriends[df_currentUserFriends.DateTime >= from_date]
		if to_date != "-1":
			df_currentUserFriends = df_currentUserFriends[df_currentUserFriends.DateTime <= to_date]

		lastFriendIDs = []

		for index, row in df_currentUserFriends.iterrows():
			if lastFriendIDs == [] and len(row['FriendIDs']) > 0:
				lastFriendIDs = row['FriendIDs'].copy()
			else:
				for removed in row['RemovedFriends']:
					try:
						lastFriendIDs.remove(int(removed))
					except:
						pass
				for added in row['AddedFriends']:
					lastFriendIDs.append(int(added))

		friendIDs.append({"twitter_id":uid, "friend_ids":lastFriendIDs})

		
	return friendIDs



def get_tnc_twitter_tweets(dbID):
	db = Connection.Instance().tnc_dbs[dbID]

	twitter_tweets = db.twitter_tweets
	twitter_profile = db.twitter_profile
	df_userInfo = pd.DataFrame(list(twitter_profile.find()))

	all_tweets = []

	for uid in list(df_userInfo['id_str']):
		try:
			tweets = list(twitter_tweets.find({'user.id_str': uid},{'_id': 0}))
		except:
			tweets = -1
		all_tweets.append({"twitter_id":uid, "tweets":tweets})
	
	return all_tweets

def add_answer_to_db(uid, sid, answer):
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	return Connection.Instance().db['ombot-answers'].insert({"uid" : uid, "sid" : sid, "answer" : answer, "timestamp": st})

def get_questions():
	cnt = Connection.Instance().db['question-answer'].count()
	return Connection.Instance().db['question-answer'].find({"StatementID" : np.random.randint(1,cnt+1)})


def get_next_user_id_sequence():
	cursor = Connection.Instance().userDb["counters"].find_and_modify(
		query={'_id': "user_id"},
		update={'$inc': {'seq': 1}},
		new=True,
		upsert=True
	)
	return cursor['seq']

def register(username, password):
	#user_id = get_next_user_id_sequence()
	#Connection.Instance().userDb['users'].insert_one({"user_id": user_id, "username" : username, "password" : password})

	#return {'response': True, 'user_id': user_id}
	pass

def getUser(user_id):
	with Connection.Instance().get_cursor() as cur:
		sql = (
			"SELECT username "
			"FROM users "
			"WHERE user_id = %s"
		)
		cur.execute(sql, [user_id])
		fetched = cur.fetchone()

		return {'username': fetched[0]}

def updateUser(user_id, password):
	with Connection.Instance().get_cursor() as cur:
		sql = (
			"UPDATE users "
			"SET password = %s "
			"WHERE user_id = %s"
		)
		cur.execute(sql, [password, user_id])

		return {'response': True}

def login(username, password):
	# with Connection.Instance().get_cursor() as cur:
	# 	sql = (
	# 		"SELECT * "
	# 		"FROM users "
	# 		"WHERE username = %s"
	# 	)
	# 	cur.execute(sql, [username])
	# 	fetched = cur.fetchall()
	# 	if len(fetched) == 0:
	# 		return {'response': False, 'error_type': 1, 'message': 'Invalid username'}

	# 	if password != fetched[0][2]:
	# 		return {'response': False, 'error_type': 2, 'message': 'Invalid password'}
	
	user = Connection.Instance().userDb['users'].find_one({"username" : username, "password": password})

	if user is not None and len(user) != 0:
		return {'response': True, 'user_id': user['user_id']}
	else:
		return {'response': False, 'error_type': 2, 'message': 'Invalid password'}

def get_twitter_users():
	profiles = Connection.Instance().CapsuleCRMdb["capsuleID_twitterProfile"].find({}, {"TwitterProfile":1, "_id":0})

	new_profiles = []

	for profile in profiles:
		new_profiles.append(profile['TwitterProfile'])
	return new_profiles

def get_crm_users(cid = None):
	if cid is not None:
		profiles = Connection.Instance().CapsuleCRMdb["om_user_profiles"].find({"capsule_profile.id":int(cid)}, {"capsule_profile":1, "_id":0})
	else:
		profiles = Connection.Instance().CapsuleCRMdb["om_user_profiles"].find({}, {"capsule_profile":1, "_id":0})

	new_profiles = []

	for profile in profiles:
		cp = profile['capsule_profile']
		cp['createdAt'] = datetime.datetime.strptime(cp['createdAt'], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y-%m-%d")
		city = 'World'
		gender = 'Empty'
		age = '-'
		for index in cp['fields']:
			if index['definition']['name'] == 'CIty':
				city = index['value']
				break
			if index['definition']['name']== 'Gender':
				gender = index['value']

			if index['definition']['name']== 'Age':
				age = index['value']

		address = "None"
		for addr in cp['emailAddresses']:
			address = addr['address']

		websiteUrl = "None"
		for ws in cp['websites']:
			websiteUrl = ws['url']

		bckgrndimg = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ6-dvOOYeOZ0gpFPbFGJYPg_v2aWQUViRoHQghyFTPjqGmy3V7eA"
		if cp['type'] == 'person':
			name = ""
			if cp["firstName"] is not None:
				name += cp["firstName"] + " "
			if cp["lastName"] is not None:
				name += cp["lastName"]
			new_profile = {'tags': cp['tags'], 'address': address, 'website_url':websiteUrl, 'backgroundImg': bckgrndimg, 'id': cp['id'], 'name': name, 'jobTitle': cp['jobTitle'], 'pictureURL': cp['pictureURL'], 'createdAt': cp['createdAt'], 'city':city, 'age': age}
		else:
			new_profile = {'tags': cp['tags'], 'address': address, 'website_url':websiteUrl, 'backgroundImg': bckgrndimg, 'id': cp['id'], 'name': cp["name"], 'pictureURL': cp['pictureURL'], 'jobTitle': "Organization", 'createdAt': cp['createdAt'], 'city':city, 'age': age}
		new_profiles.append(new_profile)
	return new_profiles

def get_twitter_screen_name(twitter_id):
	return str(list(Connection.Instance().CapsuleCRMdb["capsuleID_twitterProfile"].find({"TwitterProfile.id_str": str(twitter_id)}))[0]["TwitterProfile"]["screen_name"])


def get_follower_change(_id,isTwitterID):
	capsuleID_twitterProfile = Connection.Instance().CapsuleCRMdb.capsuleID_twitterProfile


	if isTwitterID:
		twitterID = _id
		try:
			crmID = capsuleID_twitterProfile.find_one({'TwitterProfile.id_str':_id})["CapsuleID"]
		except:
			crmID = -1
			return twitterID, crmID, [], []
			
	else:
		crmID = _id
		try:
			twitterID = capsuleID_twitterProfile.find_one({'CapsuleID':_id})["TwitterProfile"]["id_str"]
		except:
			twitterID = -1
			return twitterID, crmID, [], []


	df_twitter_followerIDs = pd.DataFrame(list(Connection.Instance().CapsuleCRMdb.twitter_followerIDs.find({"TwitterID":twitterID})))
	df_currentUserFollowers = df_twitter_followerIDs.sort_values("DateTime")

	followerCountChange = [0]
	followerChangeDate = [0]
	for i, row in df_currentUserFollowers.iterrows():
		if row.DateTime[:10] not in followerChangeDate:
			followerChangeDate.append(row.DateTime[:10])
			
			if i == 0:
				followerCountChange.append(len(row.FollowerIDs))
				continue
			followerCountChange.append(len(row.AddedFollowers)+followerCountChange[-1]-len(row.RemovedFollowers))

	return twitterID, crmID, followerCountChange[1:], followerChangeDate[1:]


def graph_follower_change(twitter_id):
	twitter_id, crmID, followerCountChange, followerChangeDate = get_follower_change(twitter_id,True)
	followerChangeDate = [fcd[5:] for fcd in followerChangeDate]

	font1 = {'size'   : 20}
	font2 = {'size'   : 17}
	plt.switch_backend('agg')
	mpl_fig = plt.figure(figsize=(8,7))
	plt.title("Change of Followers", **font1)
	plt.plot( range(len(followerCountChange)), followerCountChange)
	plt.plot( range(len(followerCountChange)), followerCountChange, 'o', label="Followers")
	plt.xlim(0, len(followerCountChange)-1)
	#plt.ylim(0, max(followerCountChange)+10)
	plt.xlabel("Dates", **font2)
	plt.ylabel("Followers Count", **font2)

	plotly_fig = tls.mpl_to_plotly( mpl_fig )



	plotly_fig['layout']['xaxis1'].update({'ticktext': followerChangeDate,
										   'tickvals': list(range(len(followerCountChange))),
										   'tickfont': {'size': 14, 'family':'Courier New, monospace'},
										   'tickangle': 60
										   })

	return plotly.offline.plot(plotly_fig, output_type='div')


scoring_matrix = np.array([
	[3,1,0,0,0,-1,-1,0,0,1],
	[1,3,1,1,0,-1,-1,0,0,0],
	[0,1,3,1,1,0,0,0,-1,-1],
	[0,1,1,3,1,0,0,0,-1,-1],
	[0,0,1,1,3,1,0,0,-1,-1],
	[-1,-1,0,0,1,3,1,0,0,0],
	[-1,-1,0,0,0,1,3,1,0,0],
	[0,0,0,0,0,0,1,3,1,0],
	[0,0,-1,-1,-1,0,0,1,3,1],
	[1,0,-1,-1,-1,0,0,0,1,3]
])

schwartz =['universalism', 'benevolence', 'conformity', 'tradition',
	   'security', 'power', 'achievement', 'hedonism', 'stimulation',
	   'self-direction']

def get_psychometric_scores(crm_id):
	try:
		Connection.Instance().CapsuleCRMdb.om_user_profiles.find_one({'capsule_profile.id':int(crm_id)})["capsule_profile"]
	except:
		return {'error': "invalid crm id argument"}

	scoring = np.array([0]*10)

	df_uq = pd.DataFrame(list(Connection.Instance().CapsuleCRMdb.user_question.find({'crm_id': str(crm_id)})))
	
	if len(df_uq) > 0:
		uq_qid = [np.asscalar(qid) for qid in np.array(df_uq['q_id'])]
		df_qq = pd.DataFrame(list(Connection.Instance().CapsuleCRMdb.question_questions.find({'q_id': {"$in": uq_qid}})))
		df_qa = pd.DataFrame(list(Connection.Instance().CapsuleCRMdb.question_answers.find()))

		for i, uq in df_uq.iterrows():
			if uq['answer_id'] > 0:
				ans_id = uq['answer_id']
				all_ans_ids = list(df_qq[df_qq.q_id == uq['q_id']]['answer_ids'])[0]
				
				for a_id in all_ans_ids:
					if a_id == ans_id:
						multp = 0.8
					elif a_id == 0:
						continue
					else:
						multp = -0.4
						
					sch_dist = list(df_qa[df_qa.id == a_id]['schwartz_distribution'])[0]
					for j, s in enumerate(schwartz):
						scoring = scoring + multp*sch_dist[s]*scoring_matrix[j]
					
			elif uq['answer_id'] < 0:
				multp = 0
				if uq['answer_id'] == -1:
					multp = -0.8
				elif uq['answer_id'] == -3:
					multp = 1
				else:
					continue
				ans_id = list(df_qq[df_qq.q_id == uq['q_id']]['text'])[0]['answer_id']
				sch_dist = list(df_qa[df_qa.id == ans_id]['schwartz_distribution'])[0]
				for j, s in enumerate(schwartz):
					scoring = scoring + multp*sch_dist[s]*scoring_matrix[j]

	personality_scores = {}
	for i, s in enumerate(schwartz):
		personality_scores[s] = np.round(scoring[i], 3).astype(float)

	return personality_scores


def get_user_topics(crm_id):
	try:
		Connection.Instance().CapsuleCRMdb.om_user_profiles.find_one({'capsule_profile.id':int(crm_id)})["capsule_profile"]
	except:
		return {'error': "invalid crm id argument"}

	return Connection.Instance().CapsuleCRMdb.om_user_properties.find_one({'CapsuleID':str(crm_id)})["wt_topics"]

def get_contents_contents(content_ids, temp_ids, content_type):
	contents_dict = {}
	for c_id in content_ids:
		contents_dict[c_id] = Connection.Instance().CapsuleCRMdb.content_table.find_one({"content_id":int(c_id), "content_type":content_type}, {"_id":0})

	temps_dict = {}
	for t_id in temp_ids:
		temps_dict[t_id] = Connection.Instance().CapsuleCRMdb.temp_content_table.find_one({"temp_id":int(t_id), "content_type":content_type}, {"_id":0})
	
	return {'Permanent Contents': contents_dict, 'Temporary Contents': temps_dict}


def get_news_contents(content_ids, temp_ids):
	return get_contents_contents(content_ids, temp_ids, "news")

def get_events_contents(content_ids, temp_ids):
	return get_contents_contents(content_ids, temp_ids, "event")


def get_questions_contents(question_ids):
	questions = {}

	for q_id in question_ids:
		try:
			q = Connection.Instance().CapsuleCRMdb.question_questions.find_one({"q_id":int(q_id)}, {"_id":0})

			answer_vals = {}
			for ans in q["answer_ids"]:
				answer_vals[Connection.Instance().CapsuleCRMdb.question_answers.find_one({"id": ans})['answer']] = ans

			question_text = Connection.Instance().CapsuleCRMdb.question_statements.find_one({"id": q["text"]['statement_id']})['text']
			if 'answer_id' in q["text"]:
				question_text = question_text.format(Connection.Instance().CapsuleCRMdb.question_answers.find_one({"id": q["text"]['answer_id']})['answer'].lower())
			if 'answer_ids' in q["text"]:
				t_ans = list(Connection.Instance().CapsuleCRMdb.question_answers.find({"id": {"$in": q["text"]['answer_ids']}},{'answer':1, '_id':0}))
				t_ans = [ta['answer'].lower() for ta in t_ans]
				question_text = question_text.format(*t_ans)

			questions[q_id] = {
				"question_id": q_id,
				"question_text": question_text,
				"answers" : answer_vals
				}
		except:
			questions[q_id] = None

	return questions

def get_feedbacks(crm_id, content_ids, question_ids):
	news_feedbacks = []
	events_feedbacks = []
	question_feedbacks = []

	if content_ids == [] and question_ids == []:
		news_feedbacks.extend(list(Connection.Instance().CapsuleCRMdb.feedback_records.find({"crm_id":crm_id, "content_type":"news"}, {"_id":0})))
		events_feedbacks.extend(list(Connection.Instance().CapsuleCRMdb.feedback_records.find({"crm_id":crm_id, "content_type":"event"}, {"_id":0})))
		question_feedbacks.extend(list(Connection.Instance().CapsuleCRMdb.user_question.find({"crm_id":crm_id}, {"_id":0})))

	for content_id in content_ids:
		tmp = list(Connection.Instance().CapsuleCRMdb.feedback_records.find({"crm_id":crm_id, "content_id": int(content_id)}, {"_id":0}))
		if tmp[0]['content_type'] == "news":
			news_feedbacks.extend(tmp)
		elif tmp[0]['content_type'] == "event":
			events_feedbacks.extend(tmp)
	for q_id in question_ids:
		question_feedbacks.extend(list(Connection.Instance().CapsuleCRMdb.user_question.find({"crm_id":crm_id, "q_id": int(q_id)}, {"_id":0})))


	return {"news": news_feedbacks, "events": events_feedbacks, "questions": question_feedbacks}

def feedback_change_privacy(crm_id, content_ids, question_ids, is_private):
	if content_ids == [] and question_ids == []:
		Connection.Instance().CapsuleCRMdb.feedback_records.update_many({"crm_id":crm_id}, {"$set": {"is_private":is_private}})
		Connection.Instance().CapsuleCRMdb.user_question.update_many({"crm_id":crm_id}, {"$set": {"is_private":is_private}})

	for content_id in content_ids:
		Connection.Instance().CapsuleCRMdb.feedback_records.update_many({"crm_id":crm_id, "content_id": int(content_id)}, {"$set": {"is_private":is_private}})
	for q_id in question_ids:
		Connection.Instance().CapsuleCRMdb.user_question.update_many({"crm_id":crm_id, "q_id": int(q_id)}, {"$set": {"is_private":is_private}})


	return {"Success": "Privacy settings updated"}


def feedback_question(crm_id, question_id, answer_id, context, is_private):
	try:
		Connection.Instance().CapsuleCRMdb.om_user_profiles.find_one({'capsule_profile.id':int(crm_id)})["capsule_profile"]
	except:
		return {'error': "invalid crm id argument"}

	try:
		question_id = int(question_id)
		question_type = Connection.Instance().CapsuleCRMdb.question_questions.find_one({"q_id": question_id})['type']
		answer_ids = Connection.Instance().CapsuleCRMdb.question_questions.find_one({"q_id": question_id})['answer_ids']
	except:
		return {'error': "invalid question id argument"}

	try:
		answer_id = int(answer_id)
		if answer_id in answer_ids:
			answer_value = Connection.Instance().CapsuleCRMdb.question_answers.find_one({"id": answer_id})['answer']
		else:
			return {'error': "invalid answer position argument"}
	except:
		return {'error': "invalid answer position argument"}


	if context['content_type'] not in context_types.values():
		return {'error': "invalid context content_type"}

	if context['content_type'] != 0 and context['content_id'] != 0:
		cnt = Connection.Instance().CapsuleCRMdb.content_table.find_one({'content_id':int(context['content_id'])})
		if cnt is None:
			return {'error': "invalid context content_id"}
		if cnt['content_type'] != list(context_types.keys())[list(context_types.values()).index(context['content_type'])]:
			return {'error': "context contenty_type content_id incompatibility"}

	answer_record = {
		"crm_id": crm_id,
		"q_id": question_id,
		"answer_id": answer_id,
		"answer_value": answer_value,
		"question_type": question_type,
		"context": context,
		"is_private": is_private,
		"created_at": datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	}
	answer_record_return = answer_record.copy()
	Connection.Instance().CapsuleCRMdb.user_question.insert_one(answer_record)

	return answer_record_return


# def get_next_feedback_id_sequence():
# 	cursor = Connection.Instance().CapsuleCRMdb["counters"].find_and_modify(
# 		query={'_id': "feedback_id"},
# 		update={'$inc': {'seq': 1}},
# 		new=True,
# 		upsert=True
# 	)
# 	return cursor['seq']

def get_next_content_id_sequence():
	cursor = Connection.Instance().CapsuleCRMdb["counters"].find_and_modify(
		query={'_id': "content_id"},
		update={'$inc': {'seq': 1}},
		new=True,
		upsert=True
	)
	return cursor['seq']


def send_feedback(crm_id, temp_id, feedback_pos, is_private, content_name):

	########## Get user's contents ##########
	try:
		recommended_ids = []
		if content_name == 'news':
			#recommended = Connection.Instance().CapsuleCRMdb.om_user_analytics.find_one({"CapsuleID": crm_id})["recommended_events"]
			recommended_ids = Connection.Instance().CapsuleCRMdb.om_user_analytics.find_one({"CapsuleID": crm_id})["recommended_news"]
		if content_name == 'event':
			#recommended = Connection.Instance().CapsuleCRMdb.om_user_analytics.find_one({"CapsuleID": crm_id})["recommended_news"]
			recommended_ids = Connection.Instance().CapsuleCRMdb.om_user_analytics.find_one({"CapsuleID": crm_id})["recommended_events"]
		recommended = list(Connection.Instance().CapsuleCRMdb.temp_content_table.find({'temp_id': {"$in": recommended_ids}}, {'_id':0}))
	except:
		return {'error': 'user not found'}


	########## Get content type ##########
	content_type = ""

	for r in recommended:
		if r['temp_id'] == temp_id:
			content_type = content_name
			content = r
			break


	if content_type == "":
		return {'error': "content not found"}


	########## Look Content Table ##########

	# news -> link_id (int)
	# events -> id (str)

	content_id = None
	if content_type == "news":
		try:
			content_id = Connection.Instance().CapsuleCRMdb.content_table.find_one({"content.link_id": content["link_id"]})["content_id"]
		except:
			pass
	elif content_type == "event":
		try:
			content_id = Connection.Instance().CapsuleCRMdb.content_table.find_one({"content.id": content["id"]})["content_id"]
		except:
			pass

	if content_id is None:
		content_id = get_next_content_id_sequence()
		content_table_dict = {
			"content_id": content_id,
			"content_type": content_type,
			"content": content,
			"created_at": datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		}
		Connection.Instance().CapsuleCRMdb.content_table.insert_one(content_table_dict)


	try:
		feedback_pos = int(feedback_pos)
		feedback_value = list(feedback_types[content_type].keys())[list(feedback_types[content_type].values()).index(feedback_pos)]
	except:
		return {'error': "invalid feedback position argument"}

	feedback_record = {
		#"feedback_id": get_next_feedback_id_sequence(),
		"content_id": content_id,
		"crm_id": crm_id,
		"feedback_pos": feedback_pos,
		"feedback_value": feedback_value,
		"content_type": content_type,
		"is_private": is_private,
		"created_at": datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	}
	feedback_record_return = feedback_record.copy()
	Connection.Instance().CapsuleCRMdb.feedback_records.insert_one(feedback_record)

	return feedback_record_return

from operator import itemgetter

def get_recommended_news(crmID, page):
	try:
		#recommended_news = Connection.Instance().CapsuleCRMdb.om_user_analytics.find_one({"CapsuleID": crmID})["recommended_news"]
		recommended_news_ids = Connection.Instance().CapsuleCRMdb.om_user_analytics.find_one({"CapsuleID": crmID})["recommended_news"]
		if page < 1:
			return crmID, [], feedback_types['news'], 1, 1
		if len(recommended_news_ids) > page*contentPerPage:
			next_page = page+1
		else:
			next_page = 0
		if len(recommended_news_ids) < (page-1)*contentPerPage:
			prev_page = math.ceil(len(recommended_news_ids)/contentPerPage)
		else:
			prev_page = page-1

		recommended_news_ids = recommended_news_ids[(page-1)*contentPerPage:page*contentPerPage]
		recommended_news = list(Connection.Instance().CapsuleCRMdb.temp_content_table.find({'temp_id': {"$in": recommended_news_ids}}, {'_id':0}))
		recommended_news = sorted(recommended_news, key=itemgetter('popularity'), reverse=True)
		return crmID, recommended_news, feedback_types['news'], prev_page, next_page
	except:
		return crmID, [], feedback_types['news'], 0, 0


def get_recommended_users(crmID):
	
	#feedback_types = Connection.Instance().CapsuleCRMdb.content_feedback_types.find_one({"content_type": "events"})["feedback_types"]

	try:
		recommended_users = Connection.Instance().CapsuleCRMdb.om_user_analytics.find_one({"CapsuleID": crmID})["recommended_users"]
		return crmID, recommended_users
	except:
		return crmID, []


def get_recommended_questions(crm_id,count,context):
	try:
		Connection.Instance().CapsuleCRMdb.om_user_profiles.find_one({'capsule_profile.id':int(crm_id)})["capsule_profile"]
	except:
		return {'error': "invalid crm id argument"}

	# get users previous questions
	user_question = pd.DataFrame(list(Connection.Instance().CapsuleCRMdb.user_question.find({"crm_id": crm_id})))
	if "q_id" in user_question:
		answered_qids = list(user_question['q_id'])
		answered_qids = [int(qid) for qid in answered_qids]
	else:
		answered_qids = []
	
	#print(answered_qids)
	#print(type(answered_qids[0]))

	recom_questions_df = pd.DataFrame(list(Connection.Instance().CapsuleCRMdb.question_questions.aggregate([
		{"$match": {"q_id": { "$nin": answered_qids}}},
		{"$sample": { "size": count }}]
	)))

	recom_questions = []

	for i, q in recom_questions_df.iterrows():
		q_id = int(q.q_id)
		answer_vals = {}
		for ans in q.answer_ids:
			answer_vals[Connection.Instance().CapsuleCRMdb.question_answers.find_one({"id": ans})['answer']] = ans

		question_text = Connection.Instance().CapsuleCRMdb.question_statements.find_one({"id": q.text['statement_id']})['text']
		if 'answer_id' in q.text:
			question_text = question_text.format(Connection.Instance().CapsuleCRMdb.question_answers.find_one({"id": q.text['answer_id']})['answer'].lower())
		if 'answer_ids' in q.text:
			t_ans = list(Connection.Instance().CapsuleCRMdb.question_answers.find({"id": {"$in": q.text['answer_ids']}},{'answer':1, '_id':0}))
			t_ans = [ta['answer'].lower() for ta in t_ans]
			question_text = question_text.format(*t_ans)

		recom_questions.append({
			"question_id": q_id,
			"question_text": question_text,
			"answers" : answer_vals
			})


	return recom_questions


def get_recommended_events(crmID, page):
	try:
		#recommended_events = Connection.Instance().CapsuleCRMdb.om_user_analytics.find_one({"CapsuleID": crmID})["recommended_events"]

		recommended_events_ids = Connection.Instance().CapsuleCRMdb.om_user_analytics.find_one({"CapsuleID": crmID})["recommended_events"]
		if page < 1:
			return crmID, [], feedback_types['event'], 1, 1
		if len(recommended_events_ids) > page*contentPerPage:
			next_page = page+1
		else:
			next_page = 0
		if len(recommended_events_ids) < (page-1)*contentPerPage:
			prev_page = math.ceil(len(recommended_events_ids)/contentPerPage)
		else:
			prev_page = page-1

		recommended_events_ids = recommended_events_ids[(page-1)*contentPerPage:page*contentPerPage]
		recommended_events = list(Connection.Instance().CapsuleCRMdb.temp_content_table.find({'temp_id': {"$in": recommended_events_ids}}, {'_id':0}))

		return crmID, recommended_events, feedback_types['event'], prev_page, next_page
	except:
		return crmID, [], feedback_types['event'], 0, 0


def get_crm_demographs():
	users = list(Connection.Instance().CapsuleCRMdb.om_user_profiles.find())


	### GENDER ###
	all_genders = []

	for g in users:
		for index in g['capsule_profile']['fields']:
			if index['definition']['name']== 'Gender':
				all_genders.append(index['value'])

	count_gender = Counter()

	for i in all_genders:
		count_gender[i] += 1

	gender_labels = []
	gender_size = []

	for k in count_gender.keys():
		gender_labels.append(k)
		gender_size.append(count_gender[k])



	plt.switch_backend('agg')
	mpl_fig = plt.figure(figsize=(4,4))

	labels = gender_labels
	sizes = gender_size
	colors = ['lightskyblue', 'gold', 'lightcoral']
	 
	plt.pie(sizes, labels=labels, colors=colors,
			autopct='%1.1f%%', startangle=140)
	plt.title('Gender Analysis of OpenMaker Community')
	 

	gender_plot = mpld3.fig_to_html(mpl_fig)



	### AGES ### 

	all_ages_birthdate = []

	for a in users:
		for index in a['capsule_profile']['fields']:
			# if index['definition']['name'] == 'Age':
			if index['definition']['name'] == 'Birth Date':
				all_ages_birthdate.append(index['value'])


	all_ages = []
	for bd in all_ages_birthdate:
	    age = (int(str(date.today())[:4]) - int(bd[:4]))
	    all_ages.append(str(age))

	count_ages = Counter()

	for i in all_ages:
		count_ages[i] += 1

	# categorize all ages into four groups
	# 0-30, 30-40, 40-50, 50+ 

	interval_one = 0
	interval_two = 0
	interval_three = 0
	interval_four = 0

	for index in count_ages.keys():
		if int(index) in range(0, 30):
			interval_one += count_ages[index]
		elif int(index) in range(30, 40):
			interval_two += count_ages[index]
		elif int(index) in range(40, 50):
			interval_three += count_ages[index]
		else:
			interval_four += count_ages[index]

	ages_size = [interval_one, interval_two, interval_three, interval_four]
	ages_labels = ['0-30', '30-40', '40-50', '50+']


	labels = ages_labels
	y_pos = np.arange(len(labels))
	sizes = ages_size

	plt.switch_backend('agg')
	mpl_fig = plt.figure(figsize=(4,4))
	 
	plt.bar(y_pos, sizes, align='center', alpha=0.6, width=.5)
	plt.xticks(y_pos, labels)
	plt.ylabel('Number of Counts')
	plt.xlabel('Age Intervals')
	plt.title('Age Analysis of OpenMaker Community')


	age_plot = mpld3.fig_to_html(mpl_fig)


	### CITIES ###
	all_cities = []

	for c in users:
		for index in c['capsule_profile']['fields']:
			if index['definition']['name'] == 'CIty':
				all_cities.append(index['value'])


	count_cities = Counter()

	for i in all_cities:
		count_cities[i] += 1       

	cities_list = pd.DataFrame.from_dict(count_cities, orient='index').reset_index()
	cities_list = cities_list.rename(columns={'index': 'Cities', 0:'Count'})
	cities_list = cities_list.sort_values('Count', ascending=False).reset_index(drop=True)

	labels = list(cities_list[:10]['Cities'])
	y_pos = np.arange(len(list(cities_list[:10]['Cities'])))
	sizes = list(cities_list[:10]['Count'])

	plt.switch_backend('agg')
	mpl_fig = plt.figure(figsize=(12,4))

	labels.reverse()
	sizes.reverse()

	plt.barh(y_pos, sizes, alpha=0.6, height=0.5)
	plt.yticks(y_pos, labels)
	plt.xlabel('Number of Counts')
	plt.ylabel('Cities')
	plt.title('Top 10 Cities of OpenMaker Community')
	city_plot = mpld3.fig_to_html(mpl_fig)

	#print("Total Number of different Cities of Capsule CRM users: " + str(len(set(count_cities))))
	#cities_list


	### JOBS ###

	all_jobs = []

	for j in users:
		if j['capsule_profile'].get('jobTitle') is not None:
			all_jobs.append(j['capsule_profile'].get('jobTitle').upper())

	count_jobs = Counter()

	for i in all_jobs:
		count_jobs[i] += 1

	jobs_list = pd.DataFrame.from_dict(count_jobs, orient='index').reset_index()
	jobs_list = jobs_list.rename(columns={'index':'Jobs', 0:'Count'})
	jobs_list = jobs_list.sort_values('Count', ascending=False).reset_index(drop=True)

	#print ("Total Number of different Jobs of Capsule CRM users: " + str(len(set(count_cities))) )
	#jobs_list

	labels = list(jobs_list[:10]['Jobs'])
	y_pos = np.arange(len(list(jobs_list[:10]['Jobs'])))
	sizes = list(jobs_list[:10]['Count'])
	 
	plt.switch_backend('agg')
	mpl_fig = plt.figure(figsize=(9,4))

	labels.reverse()
	sizes.reverse()
			   
	plt.barh(y_pos, sizes, alpha=0.6, height=.5)
	plt.yticks(y_pos, labels)
	plt.xlabel('Number of Counts')
	plt.ylabel('Cities')
	plt.title('Top 10 Jobs of OpenMaker Community')
	job_plot = mpld3.fig_to_html(mpl_fig)

	return gender_plot, age_plot, city_plot, job_plot