from .model import db, get_el_id
from fastapi import HTTPException, Header, Depends
from firebase_admin import auth

def make_user(email, is_leader, role):
    collection = "Users"
    try:
        result = db.collection(collection).add(
            {
                "email": email,
                "is_leader": is_leader,
                "role": role
                # Need to add img_url
            }
        )
        print(result)
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}

def change_user(email, is_leader, password, role):
    collection = "Users"
    doc_id = get_el_id("Users", email)
    try:
        result = db.collection(collection).document(doc_id).update(
            {
                # Schema:
               "email": email,
               "is_leader": is_leader,
               "password": password,
               "role": role
            }
        )
        print(result)
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}
    
# Google Firebase Authentication implementation:
def verify_token(token: str):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")