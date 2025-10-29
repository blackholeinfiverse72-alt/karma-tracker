from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

# Lazy initialization - connections created on first use
_client = None
_db = None
_collections = {}

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

def get_collection(collection_name):
    """Get a collection, initializing if needed"""
    if collection_name not in _collections:
        _collections[collection_name] = get_db()[collection_name]
    return _collections[collection_name]

# Collection accessors using lazy getter pattern
class _LazyCollection:
    def __init__(self, name):
        self.name = name
    
    def __getattr__(self, attr):
        # Delegate all method calls to the actual collection
        return getattr(get_collection(self.name), attr)
    
    def __call__(self, *args, **kwargs):
        # Support callable usage
        return get_collection(self.name)(*args, **kwargs)

# Create lazy collection proxies
users_col = _LazyCollection("users")
transactions_col = _LazyCollection("transactions")
qtable_col = _LazyCollection("q_table")
appeals_col = _LazyCollection("appeals")
atonements_col = _LazyCollection("atonements")
death_events_col = _LazyCollection("death_events")
karma_events_col = _LazyCollection("karma_events")
rnanubandhan_col = _LazyCollection("rnanubandhan_relationships")