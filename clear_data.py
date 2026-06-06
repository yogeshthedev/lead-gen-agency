import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def clear_database():
    MONGO_DB_URL = os.getenv("MONGO_DB_URL", "mongodb+srv://user:password@cluster.mongodb.net/leadgen")
    
    print(f"Connecting to MongoDB...")
    try:
        client = MongoClient(MONGO_DB_URL)
        db = client.get_database('leadgen')
        
        # Clear leads collection
        leads_result = db['leads'].delete_many({})
        print(f"✅ Cleared {leads_result.deleted_count} leads from the database.")
        
        # Clear email history collection
        history_result = db['email_history'].delete_many({})
        print(f"✅ Cleared {history_result.deleted_count} email history records.")
        
        client.close()
        print("Database cleanup complete!")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")

if __name__ == "__main__":
    clear_database()
