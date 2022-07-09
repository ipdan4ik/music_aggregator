import pymongo.database
from pymongo import MongoClient

client = MongoClient()

db: pymongo.database.Database = client.music
