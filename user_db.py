from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import bcrypt
import os
import uuid



load_dotenv()
client = MongoClient(os.getenv('URI'))
db = client["dungeons_droids"]
collection = db["users"]


def create_user(user_id):
    """
    Creates a user with given user_id to store in MongoDB
    """
    user_doc = {
        "user_id": user_id,
        "created_at": datetime.now(),

        # Placeholder fields for future implementation
        "_player_character_id": None
    }
    
    result = collection.insert_one(user_doc)
    print(f"User created with user_id: {user_id}, MongoDB _id: {result.inserted_id}")
    return result.inserted_id


def register_user(username, password):
    """
    Creates a new user account with username and password.
    Returns the user_id if successful, None if username already exists.
    """
    # Check if username already exists
    existing_user = collection.find_one({"username": username})
    if existing_user:
        return None
    
    # Generate unique user_id
    user_id = str(uuid.uuid4())
    
    # Hash the password using bcrypt
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user_doc = {
        "user_id": user_id,
        "username": username,
        "password_hash": password_hash,
        "created_at": datetime.now(),
        
        # Placeholder fields for future implementation
        "_player_character_id": None,
    }
    
    result = collection.insert_one(user_doc)
    print(f"User registered with username: {username}, user_id: {user_id}, MongoDB _id: {result.inserted_id}")
    return user_id


def authenticate_user(username, password):
    """
    Authenticates a user with username and password.
    Returns the user_id if successful, None if authentication fails.
    """
    user_doc = collection.find_one({"username": username})
    if not user_doc:
        return None
    
    # Check password using bcrypt
    stored_hash = user_doc.get("password_hash", "")
    if stored_hash and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return user_doc.get("user_id")
    return None


def get_user_by_username(username):
    """
    Retrieves a user doc via username.
    """
    user_doc = collection.find_one({"username": username})
    return user_doc


def get_user_by_id(user_id):
    """
    Retrieves a user doc via user_id.
    """
    user_doc = collection.find_one({"user_id": user_id})
    return user_doc


def update_user(user_id, updates):
    """
    Updates a user doc with the given updates.
    """
    query_filter = {"user_id": user_id}
    update_operation = {"$set": updates}
    
    result = collection.update_one(query_filter, update_operation)
    print(f"User {user_id} update result: {result.modified_count} document(s) modified")
    return result


def delete_user(user_id):
    """
    Deletes a user from the database.
    """
    result = collection.delete_one({"user_id": user_id})
    print(f"User {user_id} delete result: {result.deleted_count} document(s) deleted")
    return result


def query_doc(dict_param):
    """
    Query function to pull user if needed.
    """
    results = collection.find_one(dict_param)
    return results
