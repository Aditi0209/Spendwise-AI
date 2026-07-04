from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

db = client["spendwise"]

# Collections
profiles = db["profiles"]
transactions = db["transactions"]
insights = db["insights"]