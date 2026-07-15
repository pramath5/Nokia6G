import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGO_URI:
    raise Exception("MONGO_URI not found")

if not DATABASE_NAME:
    raise Exception("DATABASE_NAME not found")


try:
    client = MongoClient(MONGO_URI)
    client.admin.command("ping")

    print("Connected to MongoDB Atlas")

except Exception as e:
    print("MongoDB Connection Failed")
    raise e

db = client[DATABASE_NAME]

ue_collection = db["UE"]

subscriber_collection = db["Subscribers"]

session_collection = db["Sessions"]
print("Database Ready")