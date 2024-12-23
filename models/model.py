import firebase_admin, json, os
from firebase_admin import credentials, storage
from firebase_admin import firestore
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate("accountkey.json")
firebase_admin.initialize_app(cred, {
    "storageBucket": "crlspathfinders-82886.appspot.com"
})

firebaseConfig = {
  "apiKey": "AIzaSyAJ2VJSxD7StSrBH_PzrlHdM6VyxaLfCQ0",
  "authDomain": "crlspathfinders-82886.firebaseapp.com",
  "projectId": "crlspathfinders-82886",
  "storageBucket": "crlspathfinders-82886.appspot.com",
  "messagingSenderId": "545685285112",
  "appId": "1:545685285112:web:7eabce669a09ddd52ef30d",
  "measurementId": "G-JDLY6W8N7M"
}

db = firestore.client() # connecting to firestore
from upstash_redis import Redis

redis = Redis(url="https://welcomed-kiwi-27133.upstash.io", token="AWn9AAIjcDExYTU0MzNlMmExOTg0ZTk0OGM0YmM3YThiNDllMDA0YnAxMA")

def get_el_id(collection, target):
    # target is club_name (Clubs) or email (Users & Mentors)

    # Redis testing:
    # if collection == "Users":
    #     all_users = redis.hgetall("Users")
    #     for key, value in all_users.items():
    #         # Decode the key and value
    #         key_str = key.decode('utf-8') if isinstance(key, bytes) else key
    #         value_str = value.decode('utf-8') if isinstance(value, bytes) else value

    #         # Parse the value (user data)
    #         try:
    #             user_data = json.loads(value_str)
    #         except json.JSONDecodeError:
    #             continue  # Skip if there's an error parsing the JSON

    #         # Check if the email matches
    #         if user_data.get("email") == target:
    #             return key_str  # Return the user's ID (Redis key)

    if collection == "Clubs":
        collection = db.collection(collection)
        docs = collection.get()
        results = []
        for doc in docs:
            doc_dict = doc.to_dict()
            doc_dict["id"] = doc.id
            results.append(doc_dict)
        for r in results:
            if r["secret_password"] == target:
                return r["id"]
    elif collection == "Users" or collection == "Mentors":
        collection = db.collection(collection)
        docs = collection.get()
        results = []
        for doc in docs:
            doc_dict = doc.to_dict()
            doc_dict["id"] = doc.id
            results.append(doc_dict)
        for r in results:
            if r["email"] == target:
                return r["id"]
    elif collection == "PeerMentorLinks":
        collection = db.collection(collection)
        docs = collection.get()
        results = []
        for doc in docs:
            doc_dict = doc.to_dict()
            doc_dict["id"] = doc.id
            results.append(doc_dict)
        for r in results:
            if r["name"] == target:
                return r["id"]
    
def get_collection_id(collection, id):
    try:
        result = db.collection(collection).document(id).get().to_dict()
        return result
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}
    
def get_collection(collection):
    collection = db.collection(collection)
    docs = collection.get()
    results = []
    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict["id"] = doc.id
        results.append(doc_dict)

    # print(f"Before: {results}")

    json_results = json.dumps(results)

    return json_results

def get_collection_python(collection):
    collection = db.collection(collection)
    docs = collection.get()
    results = []
    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict["id"] = doc.id
        results.append(doc_dict)

    return results

def get_sub_collection(collection, id, subcollection):
    try:
        docs = db.collection(collection).document(id).collection(subcollection).get()
        results = []
        for doc in docs:
            doc_dict = doc.to_dict()
            doc_dict["id"] = doc.id
            results.append(doc_dict)

        # print(f"Before: {results}")

        json_results = json.dumps(results)

        return json_results
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}
    
def remove_id(collection, id):
    try:
        db.collection(collection).document(id).delete()
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}
    
def get_doc(collection, doc):
    try:
        result = db.collection(collection).document(doc).get().to_dict()
        return result
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}