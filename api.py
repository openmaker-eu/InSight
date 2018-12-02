import json
from birdy.twitter import UserClient, BirdyException 
from time import sleep
import string
import matplotlib.pyplot as plt
import numpy as np
import urllib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import mpld3
import urllib.request
import logic
import requests


watchTowerIP = "https://watchtower.openmaker.eu"
watchTowerPort = ""
watchTowerVersion = "v1.3"

spirometerIP = "http://178.62.229.16"
spirometerPort = "5000"
spirometerVersion = ""

def get_user_topics(crm_ids):
	all_topics = []
	for crm_id in crm_ids:
		user_topics = logic.get_user_topics(crm_id)
		all_topics.append({"crm_id": crm_id, "topics": user_topics})

	return all_topics

def get_psychometric_scores(crm_ids):
	all_scores = []
	for crm_id in crm_ids:
		personality_scores = logic.get_psychometric_scores(crm_id)
		all_scores.append({"crm_id": crm_id, "scores": personality_scores})

	return all_scores

def get_feedbacks(crm_ids, content_ids, question_ids):
	all_feedbacks = []
	for crm_id in crm_ids:
		feedbacks = logic.get_feedbacks(crm_id, content_ids, question_ids)
		all_feedbacks.append({"crm_id": crm_id, "feedbacks": feedbacks})

	return all_feedbacks

def convert_fig_to_html(fig):
	canvas = FigureCanvas(fig)
	png_output = StringIO.StringIO()
	canvas.print_png(png_output)
	data = png_output.getvalue().encode('base64')
	  
	return '<img src="data:image/png;base64,{}">'.format(urllib.quote(data.rstrip('\n')))

def get_articles(userID, topic_names):
	topic_info = urllib.request.urlopen(watchTowerIP + watchTowerPort + "/api/" + watchTowerVersion + "/get_topics?keywords="+topic_names).read()
	topic_info = json.loads(topic_info.decode('utf-8'))

	topic_id = topic_info['topics'][0]['topic_id']
	topic_name = topic_info['topics'][0]['topic_name']

	articles = urllib.request.urlopen(watchTowerIP + watchTowerPort + "/api/" + watchTowerVersion + "/get_news?topic_ids="+str(topic_id)+"&date=month").read()
	articles = json.loads(articles.decode('utf-8'))

	articleInfo = articles['news'][np.random.randint(len(articles['news']))]

	return articleInfo

def get_question_articles(userID, articleInfo):
	# Here we can customize how we choose the qestion (from logic.get_question)
	question = list(logic.get_questions())[0]
	del question['_id']
	return question


def demonstrate_OMBot_interaction(userID, topic_names):
	articleInfo = get_articles(userID, topic_names)

	art_summary = articleInfo['summary']
	art_url = articleInfo['url']

	question = get_question_articles(userID, articleInfo)

	print(question) 

	sid = question['StatementID']
	t = question['text']
	q = question['question']
	a1 = question['response_choices'][0]
	a2 = question['response_choices'][1]
	a3 = question['response_choices'][2]

	return art_summary, art_url, sid, t, q, a1, a2, a3

def ombotChoice(choice, sid):
	logic.add_answer_to_db(5, sid, choice)

def spirometer_categories():
	try:
		categories = urllib.request.urlopen(spirometerIP + ":" + spirometerPort).read()
		categories = json.loads(categories.decode('utf-8'))
	except:
		categories = {"error": "Not found"}

	return categories

def spirometer_scoreboard():
	try:
		scoreboard = urllib.request.urlopen(spirometerIP + ":" + spirometerPort + "/scoreboard").read()
		scoreboard = json.loads(scoreboard.decode('utf-8'))
	except:
		scoreboard = {"error": "Not found"}

	return scoreboard

def spirometer_gui_api(screen_name):
	gui_api_result = requests.get(spirometerIP + ":" + spirometerPort + "/gui/api/"+screen_name)
	html_doc = ""
	for line in gui_api_result:
		html_doc += line.strip().decode('utf-8')

	return html_doc

def spirometer_scoreboardCategory(category):
	try:
		category_info = urllib.request.urlopen(spirometerIP + ":" + spirometerPort + "/scoreboard/"+str(category)).read()
		category_info = json.loads(category_info.decode('utf-8'))
	except:
		category_info = {"error": "Not found"}
	print(category_info)

	return category_info

def spirometer_influencer(influencer):
	try:
		influencer_info = urllib.request.urlopen(spirometerIP + ":" + spirometerPort + "/influencer/"+str(influencer)).read()
		influencer_info = json.loads(influencer_info.decode('utf-8'))

	except:
		influencer_info = {"error": "Not found"}
	return influencer_info




def omn_crawler_get_profiles(twitter_ids,crmIDs):
	crmIDs_profile = []
	ids = []
	isTwitterID = True
	if len(twitter_ids) != 0:
		ids = twitter_ids
	else:
		ids = crmIDs
		isTwitterID = False

	for _id in ids:
		twitterID, crmID, twitter_profile = logic.get_twitter_profiles(_id,isTwitterID)
		crmIDs_profile.append({"twitter_id":twitterID, "crm_id":crmID, "twitter_profile":twitter_profile})
	return crmIDs_profile


def omn_crawler_get_followers(twitter_ids,crmIDs,page,from_date,to_date,only_crm_users):
	followers = []

	ids = []
	isTwitterID = True
	if len(twitter_ids) != 0:
		ids = twitter_ids
	else:
		ids = crmIDs
		isTwitterID = False


	for _id in ids:
		twitterID, crmID, followerIDs, capsuleIDs = logic.get_twitter_followers(_id,from_date,to_date,page,isTwitterID,only_crm_users)
		temp = []
		for i in range(len(followerIDs)):
			temp.append({"follower_id":str(followerIDs[i]),"crm_id":str(capsuleIDs[i])})
		followers.append({"twitter_id":twitterID, "crm_id":crmID, "follower_ids":temp})
	return followers


def omn_crawler_get_friends(twitter_ids,crmIDs,page,from_date,to_date,only_crm_users):
	friends = []

	ids = []
	isTwitterID = True
	if len(twitter_ids) != 0:
		ids = twitter_ids
	else:
		ids = crmIDs
		isTwitterID = False

	for _id in ids:
		twitterID, crmID, friendIDs, capsuleIDs = logic.get_twitter_friends(_id,from_date,to_date,page,isTwitterID,only_crm_users)
		temp = []
		for i in range(len(friendIDs)):
			temp.append({"friend_id":str(friendIDs[i]),"crm_id":str(capsuleIDs[i])})
		friends.append({"twitter_id":twitterID, "crm_id":crmID, "friend_ids":temp})
	return friends


def omn_crawler_get_tweets(twitter_ids,crmIDs,page):
	all_tweets = []

	ids = []
	isTwitterID = True
	if len(twitter_ids) != 0:
		ids = twitter_ids
	else:
		ids = crmIDs
		isTwitterID = False


	for _id in ids:
		twitterID, crmID, tweets = logic.get_twitter_tweets(_id,page,isTwitterID)
		all_tweets.append({"twitter_id":twitterID, "crm_id":crmID, "tweets":tweets})
	return all_tweets


def omn_crawler_get_ids(twitter_ids,crmIDs):
	all_ids = []

	for tid in twitter_ids:
		cid = logic.twitter_id_to_crm_id(tid)
		all_ids.append({"twitter_id":tid, "crm_id":cid})

	for cid in crmIDs:
		tid = logic.crm_id_to_twitter_id(cid)
		all_ids.append({"twitter_id":tid, "crm_id":cid})

	return all_ids

def omn_crawler_get_news(twitter_ids,crmIDs,page):
	all_news = []

	ids = []
	isTwitterID = True
	if len(twitter_ids) != 0:
		ids = twitter_ids
	else:
		ids = crmIDs
		isTwitterID = False


	for _id in ids:
		twitterID, crmID, news = logic.get_twitter_news(_id,page,isTwitterID)
		all_news.append({"twitter_id":twitterID, "crm_id":crmID, "news":news})
	return all_news

def omn_crawler_get_crm_users(column_names,page):
	header = {'Authorization': "AUTHORIZATION_CREDENTIALS"}
	
	parties = []

	r = requests.get('https://api.capsulecrm.com/api/v2/parties?embed=tags,fields,organisation&'+"page="+str(page), headers=header)
	if len(r.json()['parties']) > 0:
		for user in r.json()['parties']:
			temp = {}
			for c in column_names:
				try:
					temp[c] = user[c]
				except:
					pass
			if len(temp) > 0:
				parties.append(temp)

	return {"parties": parties}


def recommendation_news(crmIDs, page):
	if crmIDs == []:
		_, news, feedback_type, prev_page, next_page = logic.get_recommended_news('1', page)
		return {"news":news, "feedback_type": feedback_type, 'prev_page': prev_page, 'next_page': next_page}
	else:
		recommended_news = []
		for _id in crmIDs:
			crmID, news, feedback_type, prev_page, next_page = logic.get_recommended_news(_id, page)
			recommended_news.append({"crm_id":crmID, "news":news, "feedback_type": feedback_type, 'prev_page': prev_page, 'next_page': next_page})
		return {"users":recommended_news}


def recommendation_users(crmIDs):
	recommended_users = []

	for _id in crmIDs:
		crmID, rec_users = logic.get_recommended_users(_id)
		recommended_users.append({"crm_id":crmID, "recommended_users":rec_users})

	return recommended_users
def recommendation_questions(crmIDs, count, context):
	recommended_questions = []

	for _id in crmIDs:
		recom_questions = logic.get_recommended_questions(_id,count,context)
		recommended_questions.append({"crm_id":_id, "questions": recom_questions})
	return recommended_questions

def recommendation_events(crmIDs, page):
	if crmIDs == []:
		_, events, feedback_type, prev_page, next_page = logic.get_recommended_events('1', page)
		return {"events":events, "feedback_type": feedback_type, 'prev_page': prev_page, 'next_page': next_page}
	else:
		recommended_events = []
		for _id in crmIDs:
			crmID, events, feedback_type, prev_page, next_page = logic.get_recommended_events(_id, page)
			recommended_events.append({"crm_id":crmID, "events":events, "feedback_type": feedback_type, 'prev_page': prev_page, 'next_page': next_page})
		return {"users":recommended_events}



def get_om_user_profiles(twitter_ids, crmIDs, page, sorting, descending, filters):
	if len(twitter_ids) == 0 and len(crmIDs) == 0:
		return logic.get_om_user_profiles(page,sorting,descending,filters)
	else:
		om_user_profiles = []
		ids = []
		isTwitterID = True
		if len(twitter_ids) != 0:
			ids = twitter_ids
		else:
			ids = crmIDs
			isTwitterID = False


		for _id in ids:
			om_user_profiles.append(logic.get_om_user_profiles2(_id,isTwitterID))
		return om_user_profiles

def omp_analytics_get_follower_change(twitter_ids, crmIDs):
	follower_changes = []
	ids = []
	isTwitterID = True
	if len(twitter_ids) != 0:
		ids = twitter_ids
	else:
		ids = crmIDs
		isTwitterID = False


	for _id in ids:
		twitterID, crmID, followerCountChange, followerChangeDate = logic.get_follower_change(_id,isTwitterID)
		follower_changes.append({"twitter_id":twitterID, "crm_id":crmID, "follower_counts":followerCountChange, "follower_dates":followerChangeDate})
	return follower_changes


def omn_crawler_get_mentions(twitter_ids, crmIDs):
	all_mentions = []

	ids = []
	isTwitterID = True
	if len(twitter_ids) != 0:
		ids = twitter_ids
	else:
		ids = crmIDs
		isTwitterID = False


	for _id in ids:
		twitterID, crmID, mentioned_to, mentioned_by = logic.get_twitter_mentions(_id,isTwitterID)
		all_mentions.append({"twitter_id":twitterID, "crm_id":crmID, "mentioned_to":mentioned_to, "mentioned_by": mentioned_by})
	return all_mentions


tnc_db_names = ["TaylanCemgilMLdb", "UskudarliTwitterdb"]
# tnc: twitter_network_crawler
def tnc_get_profiles(dbID):
	twitter_profiles = logic.get_tnc_twitter_profiles(dbID)
	return {'users':twitter_profiles}

def tnc_get_followers(dbID, from_date,to_date):
	twitter_followers = logic.get_tnc_twitter_followers(dbID,from_date,to_date)
	return {'users':twitter_followers}

def tnc_get_friends(dbID, from_date,to_date):
	twitter_friends = logic.get_tnc_twitter_friends(dbID,from_date,to_date)
	return {'users':twitter_friends}

def tnc_get_tweets(dbID):
	twitter_tweets = logic.get_tnc_twitter_tweets(dbID)
	return {'users':twitter_tweets}