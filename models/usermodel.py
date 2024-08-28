from .model import db, get_el_id, get_doc
from fastapi import HTTPException, Header, Depends
from firebase_admin import auth

def make_user(email, is_leader, role, leading, joined_clubs):
    collection = "Users"
    try:
        result = db.collection(collection).add(
            {
                "email": email,
                "is_leader": is_leader,
                "role": role,
                "leading": leading,
                "joined_clubs": joined_clubs
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
    
def get_user_from_email(email):
    collection = "Users"
    try:
        doc_id = get_el_id("Users", email)
        user = db.collection(collection).document(doc_id).get().to_dict()
        return user
    except Exception as e:
        return f"Failed to getuserfromemail: {e}"
    
def join_leave_club(join_leave, email, club):
    try:
        user = get_user_from_email(email)
        user_id = get_el_id("Users", email)
        print(user_id)
        clubs = user["joined_clubs"]
        print(clubs)

        if join_leave == "leave":
            clubs.remove(club)
        elif join_leave == "join":
            clubs.append(club)

        doc = db.collection("Users").document(user_id)
        doc.update(
            {
                "joined_clubs": clubs
            }
        )
        return {"status": "Successfully left club"}
    except Exception as e:
        return {"status": f"Failed to leave club: {e}"}
    
def change_user_role(email, role):
    try:
        user_id = get_el_id("Users", email)
        print(f"userid - {user_id}")
        doc = db.collection("Users").document(user_id)
        doc.update(
            {
                "role": role
            }
        )
        return {"status": "Successfully changed user role"}
    except Exception as e:
        print(f"Failed to change role: {e}")
        return {"status": f"Failed to change user role: {e}"}
    
def delete_user(email):
    try:
        user_id = get_el_id("Users", email)
        print(f"userid - {user_id}")
        db.collection("Users").document(user_id).delete()
        return {"status": "Successfully deleted user"}
    except Exception as e:
        print(f"Failed to delete user: {e}")
        return {"status": f"Failed to delete user: {e}"}
    
def change_is_leader(email, leader):
    try:
        user_id = get_el_id("Users", email)
        db.collection("Users").document(user_id).update(
            {
                "is_leader": leader
            }
        )
        return {"status": "Successfully changed is leader"}
    except Exception as e:
        print(f"Failed to change is leader: {e}")
        return {"status": f"Failed to change is leader: {e}"}