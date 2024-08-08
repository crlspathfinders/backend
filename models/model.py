import firebase_admin, json, os
from firebase_admin import credentials, storage
from firebase_admin import firestore
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate(os.environ.get("FIREBASE_CREDENTIALS"))
firebase_admin.initialize_app(cred)

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

def get_el_id(collection, target):
    # target is club_name (Clubs) or email (Users & Mentors)

    if collection == "Clubs":
        collection = db.collection(collection)
        docs = collection.get()
        results = []
        for doc in docs:
            doc_dict = doc.to_dict()
            doc_dict["id"] = doc.id
            results.append(doc_dict)
        for r in results:
            if r["club_name"] == target:
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

    print(f"After: " + json_results)

    return json_results

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

        print(f"After: " + json_results)

        return json_results
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}
    
def remove_id(collection, id):
    try:
        db.collection(collection).document(id).delete()
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}