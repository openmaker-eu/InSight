import json

import os

import random

import string

from threading import Thread

#import requests



import tornado.ioloop

import tornado.options

import tornado.web

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from bson import json_util



import logic

import api

insightVersion = "v1.1"

chars = ''.join([string.ascii_letters, string.digits, string.punctuation]).replace('\'', '').replace('"', '').replace('\\', '')

secret_key = ''.join([random.SystemRandom().choice(chars) for i in range(100)])

secret_key = {secret_key}



settings = dict(

	template_path=os.path.join(os.path.dirname(__file__), "templates"),

	static_path=os.path.join(os.path.dirname(__file__), "static"),

	xsrf_cookies=False,

	cookie_secret=secret_key,

	login_url="/login",

)





class TemplateRendering:

	def render_template(self, template_name, variables={}):

		env = Environment(loader=FileSystemLoader(settings['template_path']))

		try:

			template = env.get_template(template_name)

		except TemplateNotFound:

			raise TemplateNotFound(template_name)



		content = template.render(variables)

		return content





class BaseHandler(tornado.web.RequestHandler):

	def get_current_user(self):

		return self.get_secure_cookie("user_id")



	def get_current_username(self):

		return self.get_secure_cookie("username")





class Application(tornado.web.Application):

	def __init__(self):

		handlers = [
			# ------------------------------------ V1.0 ------------------------------------
			(r"/", MainHandler, {}),

			(r"/logout", LogoutHandler, {}),

			(r"/login", LoginHandler, {}),

			(r"/register", RegisterHandler, {}),

			(r"/profile", ProfileHandler, {}),

			(r"/home", HomeHandler, {}),
			(r"/home/([0-9]*)", HomeHandler, {}),

			(r"/network", NetworkHandler, {}),



			(r"/api", DocumentationHandler, {}),


			(r"/api/"+"v1.0", ApiDocHandler, {}),



			(r"/api/"+"v1.0"+"/recommend_news_article", GetArticlesHandler, {}),



			(r"/api/"+"v1.0"+"/recommend_question_about_article", GetQuestionArticlesHandler, {}),



			(r"/api/"+"v1.0"+"/demonstrate_OMBot_interaction", GetOmbotInteractionHandler, {}),



			(r"/ombot_choice", GetOmbotChoiceHandler, {}),



			(r"/api/end_point", EndpointHandler, {}),



			(r"/api/"+"v1.0"+"/spirometer", SpirometerCategoriesHandler, {}),



			(r"/api/"+"v1.0"+"/spirometer/scoreboard", SpirometerScoreboardHandler, {}),



			(r"/api/"+"v1.0"+"/spirometer/gui/api", SpirometerGuiApiHandler, {}),



			(r"/api/"+"v1.0"+"/spirometer/influencer", SpirometerInfluencerHandler, {}),



			(r"/api/"+"v1.0"+"/omn_crawler/twitter/get_profiles", CapsuleTwitterUserProfileHandler, {}),

			(r"/api/"+"v1.0"+"/omn_crawler/twitter/get_followers", CapsuleTwitterFollowersHandler, {}),

			(r"/api/"+"v1.0"+"/omn_crawler/twitter/get_friends", CapsuleTwitterFriendsHandler, {}),

			(r"/api/"+"v1.0"+"/omn_crawler/twitter/get_tweets", CapsuleTwitterTweetsHandler, {}),

			(r"/api/"+"v1.0"+"/omn_crawler/twitter/get_ids", CapsuleTwitterIdHandler, {}),

			(r"/api/"+"v1.0"+"/omn_crawler/twitter/get_news", CapsuleTwitterNewsHandler, {}),

			(r"/api/"+"v1.0"+"/omn_crawler/twitter/get_mentions", CapsuleTwitterMentionsHandler, {}),

			(r"/api/"+"v1.0"+"/omn_crawler/crm/get_columns", CapsuleCrmColumnsHandler, {}),

			(r"/api/"+"v1.0"+"/omn_crawler/crm/get_users", CapsuleCrmUsersHandler, {}),

			(r"/api/"+"v1.0"+"/omn_crawler/get_om_user_profiles", OmUserProfilesHandler, {}),

			(r"/api/"+"v1.0"+"/omn_crawler/post_registered_user", PostRegisteredUserHandler, {}),



			(r"/api/"+"v1.0"+"/recommendation/news", RecommendationNewsHandler, {}),

			(r"/api/"+"v1.0"+"/recommendation/events", RecommendationEventsHandler, {}),

			(r"/api/"+"v1.0"+"/recommendation/questions", RecommendationQuestionsHandler, {}),

			(r"/api/"+"v1.0"+"/recommendation/users", RecommendationUsersHandler, {}),

			(r"/api/"+"v1.0"+"/recommendation/get_news_contents", RecommendationNewsContentHandler, {}),

			(r"/api/"+"v1.0"+"/recommendation/get_events_contents", RecommendationEventsContentHandler, {}),

			(r"/api/"+"v1.0"+"/recommendation/get_questions_contents", RecommendationQuestionsContentHandler, {}),

			#(r"/api/"+"v1.0"+"/recommendation/get_personality_scores", RecommendationPersonalityScoresHandler, {}),



			(r"/api/"+"v1.0"+"/feedback/news", FeedbackNewsHandler, {}),

			(r"/api/"+"v1.0"+"/feedback/event", FeedbackEventsHandler, {}),

			(r"/api/"+"v1.0"+"/feedback/question", FeedbackQuestionsHandler, {}),

			(r"/api/"+"v1.0"+"/feedback/change_privacy", FeedbackChangePrivacyHandler, {}),

			(r"/api/"+"v1.0"+"/feedback/get_feedbacks", FeedbackGetFeedbacksHandler, {}),




			(r"/api/"+"v1.0"+"/omp_analytics/twitter/get_follower_changes", OmpFollowerChangeHandler, {}),

			(r"/api/"+"v1.0"+"/omp_analytics/get_user_topics", OmpUserTopicsHandler, {}),



			(r"/api/"+"v1.0"+"/text_analytics/url_scraper", UrlScraperHandler, {}),

			(r"/api/"+"v1.0"+"/text_analytics/synonyms_antonyms", SynonymAntonymHandler, {}),




			(r"/api/"+"v1.0"+"/twitter_network_crawler/uskudarli/get_profiles", TncUskudarliProfileHandler, {}),

			(r"/api/"+"v1.0"+"/twitter_network_crawler/uskudarli/get_followers", TncUskudarliFollowerHandler, {}),

			(r"/api/"+"v1.0"+"/twitter_network_crawler/uskudarli/get_friends", TncUskudarliFriendHandler, {}),

			(r"/api/"+"v1.0"+"/twitter_network_crawler/uskudarli/get_tweets", TncUskudarliTweetHandler, {}),

			# ------------------------------------ V1.1 ------------------------------------

			# (r"/", MainHandler, {}),
			# (r"/logout", LogoutHandler, {}),
			# (r"/login", LoginHandler, {}),
			# (r"/register", RegisterHandler, {}),
			# (r"/profile", ProfileHandler, {}),
			# (r"/home", HomeHandler, {}),
			# (r"/home/([0-9]*)", HomeHandler, {}),
			# (r"/network", NetworkHandler, {}),
			# (r"/api", DocumentationHandler, {}),
			(r"/api/"+insightVersion, ApiDocHandler11, {}),

			# (r"/api/"+insightVersion+"/recommend_news_article", GetArticlesHandler, {}),
			# (r"/api/"+insightVersion+"/recommend_question_about_article", GetQuestionArticlesHandler, {}),
			# (r"/api/"+insightVersion+"/demonstrate_OMBot_interaction", GetOmbotInteractionHandler, {}),
			# (r"/ombot_choice", GetOmbotChoiceHandler, {}),
			# (r"/api/end_point", EndpointHandler, {}),

			(r"/api/"+insightVersion+"/omn_aggregator/twitter/get_profiles", CapsuleTwitterUserProfileHandler, {}),
			(r"/api/"+insightVersion+"/omn_aggregator/twitter/get_followers", CapsuleTwitterFollowersHandler, {}),
			(r"/api/"+insightVersion+"/omn_aggregator/twitter/get_friends", CapsuleTwitterFriendsHandler, {}),
			(r"/api/"+insightVersion+"/omn_aggregator/twitter/get_tweets", CapsuleTwitterTweetsHandler, {}),
			(r"/api/"+insightVersion+"/omn_aggregator/twitter/get_ids", CapsuleTwitterIdHandler, {}),
			(r"/api/"+insightVersion+"/omn_aggregator/twitter/get_news", CapsuleTwitterNewsHandler, {}),
			(r"/api/"+insightVersion+"/omn_aggregator/twitter/get_mentions", CapsuleTwitterMentionsHandler, {}),

			# (r"/api/"+insightVersion+"/omn_aggregator/crm/get_columns", CapsuleCrmColumnsHandler, {}),
			# (r"/api/"+insightVersion+"/omn_aggregator/crm/get_users", CapsuleCrmUsersHandler, {}),
			(r"/api/"+insightVersion+"/omn_aggregator/get_om_user_profiles", OmUserProfilesHandler, {}),
			(r"/api/"+insightVersion+"/post_registered_user", PostRegisteredUserHandler, {}),




			(r"/api/"+insightVersion+"/profile_analytics/twitter/get_follower_changes", OmpFollowerChangeHandler, {}),
			(r"/api/"+insightVersion+"/profile_analytics/get_user_topics", OmpUserTopicsHandler, {}),
			(r"/api/"+insightVersion+"/profile_analytics/get_psychometric_scores", RecommendationPsychometricScoresHandler, {}),

			(r"/api/"+insightVersion+"/profile_analytics/spirometer", SpirometerCategoriesHandler, {}),
			(r"/api/"+insightVersion+"/profile_analytics/spirometer/scoreboard", SpirometerScoreboardHandler, {}),
			(r"/api/"+insightVersion+"/profile_analytics/spirometer/gui/api", SpirometerGuiApiHandler, {}),
			(r"/api/"+insightVersion+"/profile_analytics/spirometer/influencer", SpirometerInfluencerHandler, {}),



			(r"/api/"+insightVersion+"/recommendation/news", RecommendationNewsHandler, {}),
			(r"/api/"+insightVersion+"/recommendation/events", RecommendationEventsHandler, {}),
			(r"/api/"+insightVersion+"/recommendation/questions", RecommendationQuestionsHandler, {}),
			(r"/api/"+insightVersion+"/recommendation/users", RecommendationUsersHandler, {}),
			(r"/api/"+insightVersion+"/recommendation/get_news_contents", RecommendationNewsContentHandler, {}),
			(r"/api/"+insightVersion+"/recommendation/get_events_contents", RecommendationEventsContentHandler, {}),
			(r"/api/"+insightVersion+"/recommendation/get_questions_contents", RecommendationQuestionsContentHandler, {}),
			

			(r"/api/"+insightVersion+"/feedback/news", FeedbackNewsHandler, {}),
			(r"/api/"+insightVersion+"/feedback/event", FeedbackEventsHandler, {}),
			(r"/api/"+insightVersion+"/feedback/question", FeedbackQuestionsHandler, {}),
			(r"/api/"+insightVersion+"/feedback/change_privacy", FeedbackChangePrivacyHandler, {}),
			(r"/api/"+insightVersion+"/feedback/get_feedbacks", FeedbackGetFeedbacksHandler, {}),



			# (r"/api/"+insightVersion+"/text_analytics/url_scraper", UrlScraperHandler, {}),
			# (r"/api/"+insightVersion+"/text_analytics/synonyms_antonyms", SynonymAntonymHandler, {}),

			# (r"/api/"+insightVersion+"/twitter_network_crawler/uskudarli/get_profiles", TncUskudarliProfileHandler, {}),
			# (r"/api/"+insightVersion+"/twitter_network_crawler/uskudarli/get_followers", TncUskudarliFollowerHandler, {}),
			# (r"/api/"+insightVersion+"/twitter_network_crawler/uskudarli/get_friends", TncUskudarliFriendHandler, {}),
			# (r"/api/"+insightVersion+"/twitter_network_crawler/uskudarli/get_tweets", TncUskudarliTweetHandler, {}),

			(r"/(.*)", tornado.web.StaticFileHandler, {'path': settings['static_path']}),

		]

		super(Application, self).__init__(handlers, **settings)


class OmpUserTopicsHandler(BaseHandler, TemplateRendering):

	def get(self):
		crm_ids = str(self.get_argument("crm_ids", []))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			user_topics_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			try:
				crm_ids = eval(crm_ids)
				crm_ids = crm_ids[:min(len(crm_ids),10)]
				crm_ids = [str(cid) for cid in crm_ids]
			except:
				crm_ids = []


			user_topics = api.get_user_topics(crm_ids)
			user_topics_str = json.dumps({"users":user_topics})
			user_topics_json = json.loads(user_topics_str)


		self.set_header('Content-Type', 'application/json')
		self.write(user_topics_json)
		template = 'getjson.html'
		variables = {
			'title': "User Topics",
		}
		content = self.render_template(template, variables)
		self.write(content)



class PostRegisteredUserHandler(BaseHandler, TemplateRendering):

	def get(self):
		crm_id = str(self.get_argument("crm_id", None))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			registered_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			registered = logic.post_registered_user(crm_id)

			registered_str = json.dumps(registered)
			registered_json = json.loads(registered_str)

		self.set_header('Content-Type', 'application/json')
		self.write(registered_json)
		template = 'getjson.html'
		variables = {
			'title': "Post Registered User",
		}
		content = self.render_template(template, variables)
		self.write(content)

class RecommendationPsychometricScoresHandler(BaseHandler, TemplateRendering):

	def get(self):
		crm_ids = str(self.get_argument("crm_ids", []))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			personality_scores_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			try:
				crm_ids = eval(crm_ids)
				crm_ids = crm_ids[:min(len(crm_ids),10)]
				crm_ids = [str(cid) for cid in crm_ids]
			except:
				crm_ids = []


			personality_scores = api.get_psychometric_scores(crm_ids)
			personality_scores_str = json.dumps({"users":personality_scores})
			personality_scores_json = json.loads(personality_scores_str)


		self.set_header('Content-Type', 'application/json')
		self.write(personality_scores_json)
		template = 'getjson.html'
		variables = {
			'title': "Personality Scores",
		}
		content = self.render_template(template, variables)
		self.write(content)



class RecommendationQuestionsContentHandler(BaseHandler, TemplateRendering):
	def get(self):
		question_ids = str(self.get_argument("question_ids", []))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			get_content_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			try:
				question_ids = eval(question_ids)
				question_ids = question_ids[:min(len(question_ids),50)]
				question_ids = [str(qid) for qid in question_ids]
			except:
				question_ids = []

			get_content = logic.get_questions_contents(question_ids)
			get_content_str = json.dumps(get_content)
			get_content_json = json.loads(get_content_str)


		self.set_header('Content-Type', 'application/json')
		self.write(get_content_json)
		template = 'getjson.html'
		variables = {
			'title': "Feedback Change Privacy",
		}
		content = self.render_template(template, variables)
		self.write(content)

class RecommendationEventsContentHandler(BaseHandler, TemplateRendering):

	def get(self):
		content_ids = str(self.get_argument("content_ids", []))
		temp_ids = str(self.get_argument("temp_ids", []))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			get_content_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			try:
				content_ids = eval(content_ids)
				content_ids = content_ids[:min(len(content_ids),20)]
				content_ids = [str(cid) for cid in content_ids]
			except:
				content_ids = []

			try:
				temp_ids = eval(temp_ids)
				temp_ids = temp_ids[:min(len(temp_ids),20)]
				temp_ids = [str(cid) for cid in temp_ids]
			except:
				temp_ids = []

			get_content = logic.get_events_contents(content_ids, temp_ids)
			get_content_str = json.dumps(get_content)
			get_content_json = json.loads(get_content_str)


		self.set_header('Content-Type', 'application/json')
		self.write(get_content_json)
		template = 'getjson.html'
		variables = {
			'title': "Feedback Change Privacy",
		}
		content = self.render_template(template, variables)
		self.write(content)

class RecommendationNewsContentHandler(BaseHandler, TemplateRendering):

	def get(self):
		content_ids = str(self.get_argument("content_ids", []))
		temp_ids = str(self.get_argument("temp_ids", []))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			get_content_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			try:
				content_ids = eval(content_ids)
				content_ids = content_ids[:min(len(content_ids),20)]
				content_ids = [str(cid) for cid in content_ids]
			except:
				content_ids = []

			try:
				temp_ids = eval(temp_ids)
				temp_ids = temp_ids[:min(len(temp_ids),20)]
				temp_ids = [str(cid) for cid in temp_ids]
			except:
				temp_ids = []

			get_content = logic.get_news_contents(content_ids, temp_ids)
			get_content_str = json.dumps(get_content)
			get_content_json = json.loads(get_content_str)


		self.set_header('Content-Type', 'application/json')
		self.write(get_content_json)
		template = 'getjson.html'
		variables = {
			'title': "News Content",
		}
		content = self.render_template(template, variables)
		self.write(content)

class FeedbackGetFeedbacksHandler(BaseHandler, TemplateRendering):

	def get(self):
		crm_ids = str(self.get_argument("crm_ids", []))
		content_ids = str(self.get_argument("content_ids", []))
		question_ids = str(self.get_argument("question_ids", []))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			feedback_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			try:
				crm_ids = eval(crm_ids)
				crm_ids = crm_ids[:min(len(crm_ids),10)]
				crm_ids = [str(cid) for cid in crm_ids]
			except:
				crm_ids = []


			try:
				content_ids = eval(content_ids)
				content_ids = content_ids[:min(len(content_ids),50)]
				content_ids = [str(cid) for cid in content_ids]
			except:
				content_ids = []

			try:
				question_ids = eval(question_ids)
				question_ids = question_ids[:min(len(question_ids),50)]
				question_ids = [str(qid) for qid in question_ids]
			except:
				question_ids = []

			feedback = api.get_feedbacks(crm_ids, content_ids, question_ids)
			feedback_str = json.dumps({"users":feedback})
			feedback_json = json.loads(feedback_str)


		self.set_header('Content-Type', 'application/json')
		self.write(feedback_json)
		template = 'getjson.html'
		variables = {
			'title': "Feedback Change Privacy",
		}
		content = self.render_template(template, variables)
		self.write(content)




class FeedbackChangePrivacyHandler(BaseHandler, TemplateRendering):

	def get(self):
		crm_id = str(self.get_argument("crm_id", None))
		content_ids = str(self.get_argument("content_ids", []))
		question_ids = str(self.get_argument("question_ids", []))
		is_private = str(self.get_argument("is_private", None))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			feedback_privacy_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			try:
				content_ids = eval(content_ids)
				content_ids = content_ids[:min(len(content_ids),50)]
				content_ids = [str(cid) for cid in content_ids]
			except:
				content_ids = []

			try:
				question_ids = eval(question_ids)
				question_ids = question_ids[:min(len(question_ids),50)]
				question_ids = [str(qid) for qid in question_ids]
			except:
				question_ids = []


			try:
				is_private = eval(is_private)
			except:
				feedback_privacy_json = {'Error': 'Invalid Privacy Input'}
			
			if is_private != True and is_private != False:
				feedback_privacy_json = {'Error': 'Invalid Privacy Input'}
			else:
				feedback_privacy = logic.feedback_change_privacy(crm_id, content_ids, question_ids, is_private)
				feedback_privacy_str = json.dumps(feedback_privacy)
				feedback_privacy_json = json.loads(feedback_privacy_str)


		self.set_header('Content-Type', 'application/json')
		self.write(feedback_privacy_json)
		template = 'getjson.html'
		variables = {
			'title': "Feedback Change Privacy",
		}
		content = self.render_template(template, variables)
		self.write(content)

class FeedbackNewsHandler(BaseHandler, TemplateRendering):

	def get(self):
		crm_id = str(self.get_argument("crm_id", None))
		temp_id = str(self.get_argument("temp_id", None))
		feedback_pos = str(self.get_argument("feedback_pos", None))
		is_private = str(self.get_argument("is_private", False))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			feedback_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			try:
				temp_id = eval(temp_id)
			except:
				temp_id = -1

			try:
				is_private = eval(is_private)
			except:
				is_private = False

			if is_private != True and is_private != False:
				is_private = False

			feedback = logic.send_feedback(crm_id, temp_id, feedback_pos, is_private, "news")

			feedback_str = json.dumps(feedback)
			feedback_json = json.loads(feedback_str)

		self.set_header('Content-Type', 'application/json')
		self.write(feedback_json)
		template = 'getjson.html'
		variables = {
			'title': "Send Feedback",
		}
		content = self.render_template(template, variables)
		self.write(content)


class FeedbackEventsHandler(BaseHandler, TemplateRendering):

	def get(self):
		crm_id = str(self.get_argument("crm_id", None))
		temp_id = str(self.get_argument("temp_id", None))
		feedback_pos = str(self.get_argument("feedback_pos", None))
		is_private = str(self.get_argument("is_private", False))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			feedback_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			try:
				temp_id = eval(temp_id)
			except:
				temp_id = -1

			try:
				is_private = eval(is_private)
			except:
				is_private = False
			if is_private != True and is_private != False:
				is_private = False

			feedback = logic.send_feedback(crm_id, temp_id, feedback_pos, is_private, "event")

			feedback_str = json.dumps(feedback)
			feedback_json = json.loads(feedback_str)

		self.set_header('Content-Type', 'application/json')
		self.write(feedback_json)
		template = 'getjson.html'
		variables = {
			'title': "Send Feedback",
		}
		content = self.render_template(template, variables)
		self.write(content)

class FeedbackQuestionsHandler(BaseHandler, TemplateRendering):

	def get(self):
		crm_id = str(self.get_argument("crm_id", None))
		question_id = str(self.get_argument("question_id", None))
		answer_id = str(self.get_argument("answer_id", None))
		context = str(self.get_argument("context", {'content_type': 0, 'content_id': 0}))
		is_private = str(self.get_argument("is_private", False))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			answer_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			try:
				context = eval(context)
				if context['content_type'] == 0:
					context['content_id'] = 0
			except:
				context = {'content_type': 0, 'content_id': 0}

			try:
				is_private = eval(is_private)
			except:
				is_private = False
			if is_private != True and is_private != False:
				is_private = False

			answer = logic.feedback_question(crm_id, question_id, answer_id, context, is_private)

			answer_str = json.dumps(answer)
			answer_json = json.loads(answer_str)

		self.set_header('Content-Type', 'application/json')
		self.write(answer_json)
		template = 'getjson.html'
		variables = {
			'title': "Qeustion Answer",
		}
		content = self.render_template(template, variables)
		self.write(content)

class SynonymAntonymHandler(BaseHandler, TemplateRendering):

	def get(self):
		word = str(self.get_argument("word", ""))
		pos = str(self.get_argument("pos", ""))

		if((pos != 'noun') and (pos != 'verb') and (pos != 'adj') and (pos != 'adv') and (pos != "")):
			pos = ""

		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			syn_ant_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			syn_ant = logic.get_synonym_antonym(word, pos)

			syn_ant_str = json.dumps(syn_ant)
			syn_ant_json = json.loads(syn_ant_str)

		self.set_header('Content-Type', 'application/json')
		self.write(syn_ant_json)
		template = 'getjson.html'
		variables = {
			'title': "Synonym Antonym",
		}
		content = self.render_template(template, variables)
		self.write(content)


class UrlScraperHandler(BaseHandler, TemplateRendering):

	def get(self):
		url = str(self.get_argument("url", None))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			scraped_url_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Your API key is wrong or missing. Please Contact Authorized Person for the key..'}
		else:
			scraped_url = logic.url_scraper(url)

			scraped_url_str = json.dumps(scraped_url)
			scraped_url_json = json.loads(scraped_url_str)

		self.set_header('Content-Type', 'application/json')
		self.write(scraped_url_json)
		template = 'getjson.html'
		variables = {
			'title': "URL Scraper",
		}
		content = self.render_template(template, variables)
		self.write(content)


class CapsuleTwitterMentionsHandler(BaseHandler, TemplateRendering):

	def get(self):
		#twitter_ids = str(self.get_argument("twitter_ids", []))
		crmIDs = str(self.get_argument("crm_ids", []))

		# try:
		# 	twitter_ids = eval(twitter_ids)
		# 	twitter_ids = twitter_ids[:min(len(twitter_ids),10)]
		# 	twitter_ids = [str(tid) for tid in twitter_ids]
		# except:
		twitter_ids = []
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			twitter_mentions_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []

			twitter_mentions = api.omn_crawler_get_mentions(twitter_ids, crmIDs)

			twitter_mentions_str = json.dumps({"users":twitter_mentions})
			twitter_mentions_json = json.loads(twitter_mentions_str)

		self.set_header('Content-Type', 'application/json')
		self.write(twitter_mentions_json)
		template = 'getjson.html'
		variables = {
			'title': "Twitter Mentions",
		}
		content = self.render_template(template, variables)
		self.write(content)


class OmpFollowerChangeHandler(BaseHandler, TemplateRendering):

	def get(self):
		#twitter_ids = str(self.get_argument("twitter_ids", []))
		crmIDs = str(self.get_argument("crm_ids", []))

		# try:
		# 	twitter_ids = eval(twitter_ids)
		# 	twitter_ids = twitter_ids[:min(len(twitter_ids),10)]
		# 	twitter_ids = [str(tid) for tid in twitter_ids]
		# except:
		twitter_ids = []
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			follower_changes_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []

			follower_changes = api.omp_analytics_get_follower_change(twitter_ids, crmIDs)

			follower_changes_str = json.dumps({"users":follower_changes})
			follower_changes_json = json.loads(follower_changes_str)

		self.set_header('Content-Type', 'application/json')
		self.write(follower_changes_json)
		template = 'getjson.html'
		variables = {
			'title': "OM Profile Analytics: Follower Changes",
		}
		content = self.render_template(template, variables)
		self.write(content)




class OmUserProfilesHandler(BaseHandler, TemplateRendering):

	def get(self):
		#twitter_ids = str(self.get_argument("twitter_ids", []))
		crmIDs = str(self.get_argument("crm_ids", []))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			om_user_profiles_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			try:
				page = int(self.get_argument("page", 1))
			except:
				page = 1

			sorting = str(self.get_argument("sort", 'Date'))

			try:
				descending = str(self.get_argument("descending", True))
				descending = eval(descending)
			except:
				descending = True

			# Filters
			try:
				filters = eval(str(self.get_argument("filters", {})))
			except:
				filters = {}


			# try:
			# 	twitter_ids = eval(twitter_ids)
			# 	twitter_ids = twitter_ids[:min(len(twitter_ids),10)]
			# 	twitter_ids = [str(tid) for tid in twitter_ids]
			# except:
			twitter_ids = []
			
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []

			#try:
			#	page = int(page)
			#except:
			#	page = 1

			om_user_profiles = api.get_om_user_profiles(twitter_ids, crmIDs, page, sorting, descending, filters)

			om_user_profiles_str = json.dumps({"users":om_user_profiles})
			om_user_profiles_json = json.loads(om_user_profiles_str)

		self.set_header('Content-Type', 'application/json')
		self.write(om_user_profiles_json)
		template = 'getjson.html'
		variables = {
			'title': "Recommend Personalized Events",
		}
		content = self.render_template(template, variables)
		self.write(content)



class RecommendationUsersHandler(BaseHandler, TemplateRendering):

	def get(self):
		crmIDs = str(self.get_argument("crm_ids", []))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			recommended_users_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []


			recommended_users = api.recommendation_users(crmIDs)

			recommended_users_str = json.dumps({"users":recommended_users})
			recommended_users_json = json.loads(recommended_users_str)

		self.set_header('Content-Type', 'application/json')
		self.write(recommended_users_json)
		template = 'getjson.html'
		variables = {
			'title': "Recommend Personalized Users",
		}
		content = self.render_template(template, variables)
		self.write(content)


class RecommendationQuestionsHandler(BaseHandler, TemplateRendering):

	def get(self):
		crmIDs = str(self.get_argument("crm_ids", []))
		count = str(self.get_argument("count", 1))
		context = str(self.get_argument("context", {'content_type': 0, 'content_id': 0}))

		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			recommended_questions_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []

			try:
				count = eval(count)
				if count > 10:
					count = 10
			except:
				count = 1

			try:
				context = eval(context)
			except:
				context = {'content_type': 0, 'content_id': 0}


			recommended_questions = api.recommendation_questions(crmIDs, count, context)

			recommended_questions_str = json.dumps({"users":recommended_questions})
			recommended_questions_json = json.loads(recommended_questions_str)

		self.set_header('Content-Type', 'application/json')
		self.write(recommended_questions_json)
		template = 'getjson.html'
		variables = {
			'title': "Recommend Personalized Questions",
		}
		content = self.render_template(template, variables)
		self.write(content)

class RecommendationEventsHandler(BaseHandler, TemplateRendering):

	def get(self):
		#twitter_ids = str(self.get_argument("twitter_ids", []))
		crmIDs = str(self.get_argument("crm_ids", []))
		try:
			page = int(self.get_argument("page", 1))
		except:
			page = 1
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			recommended_events_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []



			recommended_events = api.recommendation_events(crmIDs, page)

			recommended_events_str = json.dumps(recommended_events)
			recommended_events_json = json.loads(recommended_events_str)

		self.set_header('Content-Type', 'application/json')
		self.write(recommended_events_json)
		template = 'getjson.html'
		variables = {
			'title': "Recommend Personalized Events",
		}
		content = self.render_template(template, variables)
		self.write(content)


class RecommendationNewsHandler(BaseHandler, TemplateRendering):

	def get(self):
		#twitter_ids = str(self.get_argument("twitter_ids", []))
		crmIDs = str(self.get_argument("crm_ids", []))
		try:
			page = int(self.get_argument("page", 1))
		except:
			page = 1
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			recommended_news_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []

			recommended_news = api.recommendation_news(crmIDs, page)

			recommended_news_str = json.dumps(recommended_news)
			recommended_news_json = json.loads(recommended_news_str)

		self.set_header('Content-Type', 'application/json')
		self.write(recommended_news_json)
		template = 'getjson.html'
		variables = {
			'title': "Recommend Personalized News",
		}
		content = self.render_template(template, variables)
		self.write(content)



class CapsuleCrmUsersHandler(BaseHandler, TemplateRendering):

	def get(self):
		column_names = str(self.get_argument("column_names", []))
		page = int(self.get_argument("page", 1))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			parties_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			try:
				column_names = column_names[1:-1].split(',')
			except:
				column_names = []

			try:
				page = int(page)
			except:
				page = 1

			parties = api.omn_crawler_get_crm_users(column_names,page)

			parties_str = json.dumps(parties)
			parties_json = json.loads(parties_str)

		self.set_header('Content-Type', 'application/json')
		self.write(parties_json)
		template = 'getjson.html'
		variables = {
			'title': "Capsule CRM Users",
		}
		content = self.render_template(template, variables)
		self.write(content)


class CapsuleCrmColumnsHandler(BaseHandler, TemplateRendering):

	def get(self):
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			column_names = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			column_names = {'all_unique': [u'about',u'addresses',u'firstName',u'title',u'fields',u'organisation',u'tags',u'phoneNumbers',u'websites',u'id',u'pictureURL',u'jobTitle',u'lastName',u'owner',u'name',u'emailAddresses',u'type',u'updatedAt',u'createdAt',u'lastContactedAt'],
	'organisation': [u'about',u'addresses',u'name',u'tags',u'fields',u'phoneNumbers',u'websites',u'pictureURL',u'updatedAt',u'owner',u'emailAddresses',u'type',u'id',u'createdAt',u'lastContactedAt'],
	'person': [u'about',u'addresses',u'fields',u'firstName',u'title',u'lastName',u'organisation',u'tags',u'phoneNumbers',u'websites',u'emailAddresses',u'pictureURL',u'jobTitle',u'owner',u'updatedAt',u'type',u'id',u'createdAt',u'lastContactedAt']}
		
		self.set_header('Content-Type', 'application/json')
		self.write(column_names)

		template = 'getjson.html'
		variables = {
			'title': "Capsule CRM Columns",
		}
		content = self.render_template(template, variables)
		self.write(content)


class CapsuleTwitterNewsHandler(BaseHandler, TemplateRendering):

	def get(self):
		#twitter_ids = str(self.get_argument("twitter_ids", []))
		crmIDs = str(self.get_argument("crm_ids", []))
		page = str(self.get_argument("page", 1))

		# try:
		# 	twitter_ids = eval(twitter_ids)
		# 	twitter_ids = twitter_ids[:min(len(twitter_ids),10)]
		# 	twitter_ids = [str(tid) for tid in twitter_ids]
		# except:
		twitter_ids = []
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			all_news_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []

			try:
				page = int(page)
			except:
				page = 1

			all_news = api.omn_crawler_get_news(twitter_ids,crmIDs,page)

			all_news_str = json.dumps({"users":all_news})
			all_news_json = json.loads(all_news_str)

		self.set_header('Content-Type', 'application/json')
		self.write(all_news_json)
		template = 'getjson.html'
		variables = {
			'title': "Twitter Tweets News",
		}
		content = self.render_template(template, variables)
		self.write(content)


class CapsuleTwitterIdHandler(BaseHandler, TemplateRendering):

	def get(self):
		twitter_ids = str(self.get_argument("twitter_ids", []))
		crmIDs = str(self.get_argument("crm_ids", []))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			all_ids_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			try:
			 	twitter_ids = eval(twitter_ids)
			 	twitter_ids = twitter_ids[:min(len(twitter_ids),10)]
			 	twitter_ids = [str(tid) for tid in twitter_ids]
			except:
				twitter_ids = []
			
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []

			all_ids= api.omn_crawler_get_ids(twitter_ids,crmIDs)
			all_ids_str = json.dumps({"users":all_ids})
			all_ids_json = json.loads(all_ids_str)

		self.set_header('Content-Type', 'application/json')
		self.write(all_ids_json)
		template = 'getjson.html'
		variables = {
			'title': "Twitter ID - CRM ID",
		}
		content = self.render_template(template, variables)
		self.write(content)




class CapsuleTwitterUserProfileHandler(BaseHandler, TemplateRendering):

	def get(self):
		#twitter_ids = str(self.get_argument("twitter_ids", []))
		crmIDs = str(self.get_argument("crm_ids", []))

		# try:
		# 	twitter_ids = eval(twitter_ids)
		# 	twitter_ids = twitter_ids[:min(len(twitter_ids),10)]
		# 	twitter_ids = [str(tid) for tid in twitter_ids]
		# except:
		twitter_ids = []
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			crmIDs_profiles_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []

			crmIDs_profiles = api.omn_crawler_get_profiles(twitter_ids,crmIDs)
			crmIDs_profiles_str = json.dumps({"users":crmIDs_profiles})
			crmIDs_profiles_json = json.loads(crmIDs_profiles_str)

		self.set_header('Content-Type', 'application/json')
		self.write(crmIDs_profiles_json)
		template = 'getjson.html'
		variables = {
			'title': "Capsule CRM Twitter Profile",
		}
		content = self.render_template(template, variables)
		self.write(content)


class CapsuleTwitterFollowersHandler(BaseHandler, TemplateRendering):

	def get(self):
		#twitter_ids = str(self.get_argument("twitter_ids", []))
		crmIDs = str(self.get_argument("crm_ids", []))
		page = str(self.get_argument("page", 1))
		from_date = str(self.get_argument("from_date", -1))
		to_date = str(self.get_argument("to_date", -1))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			crmIDs_followers_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:

			try:
				only_crm_users = str(self.get_argument("only_crm_users", False))
				only_crm_users = eval(only_crm_users)
			except:
				only_crm_users = False


			# try:
			# 	twitter_ids = eval(twitter_ids)
			# 	twitter_ids = twitter_ids[:min(len(twitter_ids),10)]
			# 	twitter_ids = [str(tid) for tid in twitter_ids]
			# except:
			twitter_ids = []
			
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []

			try:
				page = int(page)
			except:
				page = 1
			crmIDs_followers = api.omn_crawler_get_followers(twitter_ids,crmIDs,page,from_date,to_date,only_crm_users)
			crmIDs_followers_str = json.dumps({"users":crmIDs_followers})
			crmIDs_followers_json = json.loads(crmIDs_followers_str)

		self.set_header('Content-Type', 'application/json')
		self.write(crmIDs_followers_json)
		template = 'getjson.html'
		variables = {
			'title': "Capsule CRM Twitter Followers",
		}
		content = self.render_template(template, variables)
		self.write(content)



class CapsuleTwitterFriendsHandler(BaseHandler, TemplateRendering):

	def get(self):
		#twitter_ids = str(self.get_argument("twitter_ids", []))
		crmIDs = str(self.get_argument("crm_ids", []))
		page = str(self.get_argument("page", 1))
		from_date = str(self.get_argument("from_date", -1))
		to_date = str(self.get_argument("to_date", -1))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			crmIDs_friends_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:
			try:
				only_crm_users = str(self.get_argument("only_crm_users", False))
				only_crm_users = eval(only_crm_users)
			except:
				only_crm_users = False

			# try:
			# 	twitter_ids = eval(twitter_ids)
			# 	twitter_ids = twitter_ids[:min(len(twitter_ids),10)]
			# 	twitter_ids = [str(tid) for tid in twitter_ids]
			# except:
			twitter_ids = []
			
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []


			try:
				page = int(page)
			except:
				page = 1
			crmIDs_friends = api.omn_crawler_get_friends(twitter_ids,crmIDs,page,from_date,to_date,only_crm_users)
			crmIDs_friends_str = json.dumps({"users":crmIDs_friends})
			crmIDs_friends_json = json.loads(crmIDs_friends_str)

		self.set_header('Content-Type', 'application/json')
		self.write(crmIDs_friends_json)
		template = 'getjson.html'
		variables = {
			'title': "Capsule CRM Twitter Friends",
		}
		content = self.render_template(template, variables)
		self.write(content)


class CapsuleTwitterTweetsHandler(BaseHandler, TemplateRendering):

	def get(self):
		#twitter_ids = str(self.get_argument("twitter_ids", []))
		crmIDs = str(self.get_argument("crm_ids", []))
		page = str(self.get_argument("page", 1))

		# try:
		# 	twitter_ids = eval(twitter_ids)
		# 	twitter_ids = twitter_ids[:min(len(twitter_ids),10)]
		# 	twitter_ids = [str(tid) for tid in twitter_ids]
		# except:
		twitter_ids = []
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			crmIDs_tweets_json = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:		
			try:
				crmIDs = eval(crmIDs)
				crmIDs = crmIDs[:min(len(crmIDs),10)]
				crmIDs = [str(cid) for cid in crmIDs]
			except:
				crmIDs = []


			try:
				page = int(page)
			except:
				page = 1
			crmIDs_tweets = api.omn_crawler_get_tweets(twitter_ids,crmIDs,page)
			crmIDs_tweets_str = json.dumps({"users":crmIDs_tweets})
			crmIDs_tweets_json = json.loads(crmIDs_tweets_str)

		self.set_header('Content-Type', 'application/json')
		self.write(crmIDs_tweets_json)
		template = 'getjson.html'
		variables = {
			'title': "Capsule CRM Twitter Tweets",
		}
		content = self.render_template(template, variables)
		self.write(content)


class TncUskudarliProfileHandler(BaseHandler, TemplateRendering):

	def get(self):
		twitter_profiles = api.tnc_get_profiles(1)
		twitter_profiles_str = json.dumps(twitter_profiles)
		twitter_profiles_json = json.loads(twitter_profiles_str)
		api_key = str(self.get_argument("api_key", None))	

		self.set_header('Content-Type', 'application/json')
		self.write(twitter_profiles_json)
		template = 'getjson.html'
		variables = {
			'title': "Twitter Network Crawler Uskudarli Profiles",
		}
		content = self.render_template(template, variables)
		self.write(content)


class TncUskudarliFollowerHandler(BaseHandler, TemplateRendering):

	def get(self):
		from_date = str(self.get_argument("from_date", -1))
		to_date = str(self.get_argument("to_date", -1))
		twitter_followers = api.tnc_get_followers(1, from_date, to_date)
		twitter_followers_str = json.dumps(twitter_followers)
		twitter_followers_json = json.loads(twitter_followers_str)

		self.set_header('Content-Type', 'application/json')
		self.write(twitter_followers_json)
		template = 'getjson.html'
		variables = {
			'title': "Twitter Network Crawler Uskudarli Followers",
		}
		content = self.render_template(template, variables)
		self.write(content)


class TncUskudarliFriendHandler(BaseHandler, TemplateRendering):

	def get(self):
		from_date = str(self.get_argument("from_date", -1))
		to_date = str(self.get_argument("to_date", -1))
		twitter_friends = api.tnc_get_friends(1, from_date, to_date)
		twitter_friends_str = json.dumps(twitter_friends)
		twitter_friends_json = json.loads(twitter_friends_str)

		self.set_header('Content-Type', 'application/json')
		self.write(twitter_friends_json)
		template = 'getjson.html'
		variables = {
			'title': "Twitter Network Crawler Uskudarli Friends",
		}
		content = self.render_template(template, variables)
		self.write(content)


class TncUskudarliTweetHandler(BaseHandler, TemplateRendering):

	def get(self):
		twitter_tweets = api.tnc_get_tweets(1)
		twitter_tweets_str = json.dumps(twitter_tweets)
		twitter_tweets_json = json.loads(twitter_tweets_str)

		self.set_header('Content-Type', 'application/json')
		self.write(twitter_tweets_json)
		template = 'getjson.html'
		variables = {
			'title': "Twitter Network Crawler Uskudarli Tweets",
		}
		content = self.render_template(template, variables)
		self.write(content)





class SpirometerCategoriesHandler(BaseHandler, TemplateRendering):

	def get(self):
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			categories = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:		
			categories = api.spirometer_categories()

		self.set_header('Content-Type', 'application/json')

		self.write(categories)

		template = 'getjson.html'

		variables = {

			'title': "Spirometer Categories",

		}

		content = self.render_template(template, variables)

		self.write(content)



class SpirometerScoreboardHandler(BaseHandler, TemplateRendering):

	def get(self):

		category = str(self.get_argument("category", None))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			scoreboard = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:	
			if category != "None":

				scoreboard = api.spirometer_scoreboardCategory(category)

			else:

				scoreboard = api.spirometer_scoreboard()

		self.set_header('Content-Type', 'application/json')

		self.write(scoreboard)

		template = 'getjson.html'

		variables = {

			'title': "Spirometer Scoreboard",

		}

		content = self.render_template(template, variables)

		self.write(content)



class SpirometerGuiApiHandler(BaseHandler, TemplateRendering):

	def get(self):

		screen_name = str(self.get_argument("screen_name", None))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			content = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:

			guiApi = api.spirometer_gui_api(screen_name)

		template = 'guiApi.html'

		variables = {

			'title': "Spirometer Gui API",

			'varr': guiApi

		}

		content = self.render_template(template, variables)

		self.write(content)





class SpirometerInfluencerHandler(BaseHandler, TemplateRendering):

	def get(self):

		influencer = str(self.get_argument("screen_name", None))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			influencer_info = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:	
			influencer_info = api.spirometer_influencer(influencer)

		self.set_header('Content-Type', 'application/json')

		self.write(influencer_info)

		template = 'getjson.html'

		variables = {

			'title': "Spirometer Influencer",

		}

		content = self.render_template(template, variables)

		self.write(content)



class GetOmbotChoiceHandler(BaseHandler, TemplateRendering):

	def get(self):

		choice = str(self.get_argument("choice", None))

		sid = str(self.get_argument("sid", None))

		userID = str(self.get_argument("userID", None))

		topic_names = str(self.get_argument("topic_names", None))

		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			content = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:	
			api.ombotChoice(choice,sid)

		template = 'api.html'

		variables = {

			'title': "We Got Your Answer",

			'uid': userID,

			'tnames' : topic_names

		}

		content = self.render_template(template, variables)

		self.write(content)





class GetOmbotInteractionHandler(BaseHandler, TemplateRendering):

	def get(self):

		userID = str(self.get_argument("userID", None))

		topic_names = str(self.get_argument("topic_names", None))
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			content = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:	
			art_summary, art_url, sid, t, q, a1, a2, a3 = api.demonstrate_OMBot_interaction(userID, topic_names)

		template = 'ombot.html'

		variables = {

			'title': "OMbot article and question",

			'art_summary': art_summary,

			'art_url': art_url,

			'sid': sid,

			't': t,

			'q': q,

			'a1': a1,

			'a2': a2,

			'a3': a3,

			'uid': userID,

			'tnames' : topic_names

		}

		content = self.render_template(template, variables)

		self.write(content)



class GetQuestionArticlesHandler(BaseHandler, TemplateRendering):

	def get(self):

		userID = str(self.get_argument("userID", None))

		articleInfo = str(self.get_argument("articleInfo", None))
		
		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			recommended_question_article = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:	
			recommended_question_article = api.get_question_articles(userID, articleInfo)

		self.set_header('Content-Type', 'application/json')

		self.write(recommended_question_article)

		template = 'getjson.html'

		variables = {

			'title': "Get Recommended Question of Article API",

		}

		content = self.render_template(template, variables)

		self.write(content)



class GetArticlesHandler(BaseHandler, TemplateRendering):

	def get(self):

		userID = str(self.get_argument("userID", None))

		topic_names = str(self.get_argument("topic_names", None))

		api_key = str(self.get_argument("api_key", None))

		if not logic.check_api_key(api_key):
			recommended_article = {'Unauthorized Connection': 'Your API key is wrong or missing. Please Contact Authorized Person for the key.'}
		else:	
			recommended_article = api.get_articles(userID, topic_names)

		self.set_header('Content-Type', 'application/json')

		self.write(recommended_article)

		template = 'getjson.html'

		variables = {

			'title': "Get Recommended Articles API",

		}

		content = self.render_template(template, variables)

		self.write(content)



class EndpointHandler(BaseHandler, TemplateRendering):

	def get(self):

		example = api.example_method()

		#self.set_header('Content-Type', 'application/json')

		#self.write(example)

		template = 'api.html'

		variables = {

			'title': "Insight Api",

			'varr': example

		}

		content = self.render_template(template, variables)

		self.write(content)





class DocumentationHandler(BaseHandler, TemplateRendering):

	def get(self):

		template = 'api.html'

		variables = {

			'title': "Insight Api"

		}

		content = self.render_template(template, variables)

		self.write(content)



class ApiDocHandler(BaseHandler, TemplateRendering):

	def get(self):

		template = 'apiary10.html'

		variables = {

			'title': "Insight Api Documentation"

		}

		content = self.render_template(template, variables)

		self.write(content)

class ApiDocHandler11(BaseHandler, TemplateRendering):

	def get(self):

		template = 'apiary11.html'

		variables = {

			'title': "Insight Api Documentation"

		}

		content = self.render_template(template, variables)

		self.write(content)



class MainHandler(BaseHandler, TemplateRendering):

	def get(self):

		template = 'index.html'

		variables = {

			'title': "Insight"

		}

		content = self.render_template(template, variables)

		self.write(content)





class RegisterHandler(BaseHandler, TemplateRendering):

	def get(self):

		template = 'register.html'

		variables = {

			'title': "Register Page"

		}

		content = self.render_template(template, variables)

		self.write(content)



	def post(self):

		username = self.get_argument("username")

		password = str(self.get_argument("password"))

		register_info = logic.register(str(username), password)

		if register_info['response']:

			self.set_secure_cookie("user_id", str(register_info['user_id']))

			self.set_secure_cookie("username", str(username))

			self.write({'response': True, 'redirectUrl': '/home'})

		else:

			self.write(json.dumps(register_info))





class LoginHandler(BaseHandler, TemplateRendering):

	def get(self):

		template = 'login.html'

		variables = {

			'title': "Login Page"

		}

		content = self.render_template(template, variables)

		self.write(content)



	def post(self):

		username = self.get_argument("username")

		login_info = logic.login(str(username), str(self.get_argument("password")))

		if login_info['response']:

			self.set_secure_cookie("user_id", str(login_info['user_id']))

			self.set_secure_cookie("username", str(username))

			self.write({'response': True, 'redirectUrl': self.get_argument('next', '/home')})

		else:

			self.write(json.dumps(login_info))





class LogoutHandler(BaseHandler, TemplateRendering):

	def get(self):

		self.clear_all_cookies()

		self.redirect("/")





class ProfileHandler(BaseHandler, TemplateRendering):

	@tornado.web.authenticated

	def get(self):

		user_id = tornado.escape.xhtml_escape(self.current_user)

		template = 'afterlogintemplate.html'

		user = logic.getUser(user_id)

		variables = {

			'title': "My Profile",

			'type': "profile",

			'username': user['username'],

		}

		content = self.render_template(template, variables)

		self.write(content)



	@tornado.web.authenticated

	def post(self):

		password = str(self.get_argument("password"))

		user_id = tornado.escape.xhtml_escape(self.current_user)

		update_info = logic.updateUser(user_id, password)

		if update_info['response']:

			self.write({'response': True, 'redirectUrl': '/home'})

		else:

			self.write(json.dumps(update_info))





class HomeHandler(BaseHandler, TemplateRendering):

	@tornado.web.authenticated

	def get(self, crm_id = None):

		if crm_id is None:

			user_id = tornado.escape.xhtml_escape(self.current_user)

			template = 'afterlogintemplate.html'


			crm_users = logic.get_crm_users()
			#twitter_users = logic.get_twitter_users()

			variables = {

				'title': "Profiles",

				'type': "home",

				'username': str(tornado.escape.xhtml_escape(self.get_current_username())),

				'crm_users': crm_users,

				'crm_users_count': len(crm_users),

			}

			content = self.render_template(template, variables)

			self.write(content)

		else:

			crm_profile = logic.get_crm_users(crm_id)[0]

			twitter_id, _, twitter_profile = logic.get_twitter_profiles(crm_id,False)
			if twitter_id != -1 and not twitter_profile["protected"]:
				follower_graph = logic.graph_follower_change(twitter_id)
			else:
				follower_graph = -1


			_, events, _, _, _ = logic.get_recommended_events(crm_id, 1)


			_, news, _, _, _ = logic.get_recommended_news(crm_id, 1)

			_, recommended_user_ids = logic.get_recommended_users(crm_id)
			try:
				all_recommended_user_ids = recommended_user_ids[:5]
			except:
				all_recommended_user_ids = -1

			if all_recommended_user_ids != -1:
				all_recommended_users = []
				for _id in all_recommended_user_ids:
					all_recommended_users.append(logic.get_om_user_profiles2(_id,False))
					all_recommended_users[-1]['capsule_profile'] = logic.get_crm_users(_id)[0]
			else:
				all_recommended_users = -1


			template = 'afterlogintemplate.html'

			variables = {

				'title': "CRM User Profile Analytics",

				'type': "crm_user_analytics",

				"crm_profile": crm_profile,

				"twitter_id": twitter_id,

				"twitter_profile": twitter_profile,

				'graph': follower_graph,

				'all_events': events,

				'all_news': news,

				'all_recommended_users': all_recommended_users,

				'user_topics': logic.get_user_topics(crm_id)

			}

			content = self.render_template(template, variables)

			self.write(content)




	@tornado.web.authenticated

	def post(self):

		alertid = self.get_argument("alertid")

		user_id = tornado.escape.xhtml_escape(self.current_user)



		template = "home.html"

		variables = {

			'title': "Profiles",

			'type': "home",

			'username': str(tornado.escape.xhtml_escape(self.get_current_username())),

		}

		content = self.render_template(template, variables)

		self.write(content)


class NetworkHandler(BaseHandler, TemplateRendering):

	@tornado.web.authenticated

	def get(self):

		user_id = tornado.escape.xhtml_escape(self.current_user)

		template = 'afterlogintemplate.html'

		crm_users = logic.get_crm_users()

		gender_plot, age_plot, city_plot, job_plot = logic.get_crm_demographs()


		variables = {

			'title': "Network",

			'type': "network",

			'crm_users_count': len(crm_users),

			'gender_plot': gender_plot,

			'age_plot': age_plot,

			'city_plot': city_plot,

			'job_plot': job_plot


		}

		content = self.render_template(template, variables)

		self.write(content)




	@tornado.web.authenticated

	def post(self):

		alertid = self.get_argument("alertid")

		user_id = tornado.escape.xhtml_escape(self.current_user)



		template = "home.html"

		variables = {

			'title': "Profiles",

			'type': "home",

			'username': str(tornado.escape.xhtml_escape(self.get_current_username())),

		}

		content = self.render_template(template, variables)

		self.write(content)



def main():

	tornado.options.parse_command_line()

	app = Application()

	app.listen(8484)

	tornado.ioloop.IOLoop.current().start()





def webserverInit():

	thr = Thread(target=main)

	thr.daemon = True

	thr.start()

	thr.join()





if __name__ == "__main__":

	main()

