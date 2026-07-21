# database/mongo.py

from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "5g_ai_agents")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file")

# MongoDB Client
client = MongoClient(MONGO_URI)

# Database
db = client[DATABASE_NAME]

# Collections
ue_collection = db["UE"]
subscriber_collection = db["Subscribers"]
session_collection = db["Sessions"]


def test_connection():
    """
    Test MongoDB connection.
    """
    try:
        client.admin.command("ping")
        print("✅ Connected to MongoDB Atlas")
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")


if __name__ == "__main__":
    test_connection()