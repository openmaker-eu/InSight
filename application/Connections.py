from __future__ import print_function

import psycopg2
import pymongo
from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool
import urllib.request

from application.utils.Singleton import Singleton

@Singleton
class Connection:
	def __init__(self):
		try:
			host = "HOST_IP"

			self.MongoDBClient = pymongo.MongoClient('mongodb://'+'MONGODB_USER'+':'+'MONGODB_PASSWORD'+'@'+host+':27017/', connect=False)
			self.db = self.MongoDBClient.db
			self.CapsuleCRMdb = self.MongoDBClient.CapsuleCRMdb
			self.tnc_dbs = [self.MongoDBClient.TaylanCemgilMLdb, self.MongoDBClient.UskudarliTwitterdb]
			self.userDb = self.MongoDBClient.userDb
			
			self.PostGreSQLConnect = psycopg2.connect(
				"dbname='' user='' host="+host+" password=''")

			self.pg_pool = psycopg2.pool.ThreadedConnectionPool(
				1, 15,
				host=host,
				port='5433',
				user='',
				password='',
				database='')

			print("new connection")
		except Exception as e:
			print(e)
			print("I am unable to connect to the database")
			pass

	@contextmanager
	def get_cursor(self):
		conn = self.pg_pool.getconn()
		try:
			yield conn.cursor()
			conn.commit()
		finally:
			self.pg_pool.putconn(conn)
