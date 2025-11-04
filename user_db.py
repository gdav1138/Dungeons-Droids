from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os



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
        "_player_character_id": None,
        "rooms_visited": [],
    }
    
    result = collection.insert_one(user_doc)
    print(f"User created with user_id: {user_id}, MongoDB _id: {result.inserted_id}")
    return result.inserted_id


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
