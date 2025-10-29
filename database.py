from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

# Lazy initialization - connections created on first use
_client = None
_db = None

def get_client():
    """Get MongoDB client, initializing if needed"""
    global _client
    if _client is None:
        if not MONGO_URI:
            raise ValueError("MONGO_URI environment variable not set")
        _client = MongoClient(MONGO_URI)
    return _client

def get_db():
    """Get database instance, initializing if needed"""
    global _db
    if _db is None:
        client = get_client()
        _db = client[DB_NAME]
    return _db

# Initialize collections only when first accessed
def _init_collections():
    db = get_db()
    global users_col, transactions_col, qtable_col, appeals_col
    global atonements_col, death_events_col, karma_events_col, rnanubandhan_col
    
    users_col = db["users"]
    transactions_col = db["transactions"]
    qtable_col = db["q_table"]
    appeals_col = db["appeals"]
    atonements_col = db["atonements"]
    death_events_col = db["death_events"]
    karma_events_col = db["karma_events"]
    rnanubandhan_col = db["rnanubandhan_relationships"]

# Collections will be None until first use
users_col = None
transactions_col = None
qtable_col = None
appeals_col = None
atonements_col = None
death_events_col = None
karma_events_col = None
rnanubandhan_col = None