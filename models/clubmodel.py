from .model import db, get_el_id

def get_secret_pass(club_id):
    return db.collection("Clubs").document(club_id).get().to_dict()["secret_password"]

def make_club(advisor_email, club_days, club_description, club_name, president_email, room_number, secret_password, start_time, status, vice_presidents_emails):
    # Need to pass in the id, etc for which collection to actually change.
    collection = "Clubs"
    try:
        result = db.collection(collection).add(
            {
                "advisor_email": advisor_email,
                "club_days": club_days,
                "club_description": club_description,
                "club_name": club_name,
                "president_email": president_email,
                "room_number": room_number,
                "secret_password": secret_password,
                "start_time": start_time,
                "status": status,
                "vice_presidents_emails": vice_presidents_emails,
                "members": []
                # Need to add img_url
            }
        )
        print(result)
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}
    
def change_club(advisor_email, club_days, club_description, club_name, president_email, room_number, secret_password, start_time, status, vice_presidents_emails):
    collection = "Clubs"
    doc_id = get_el_id(collection, secret_password)
    try:
        db.collection(collection).document(doc_id).update(
            {
                # Schema:
                "advisor_email": advisor_email,
                "club_days": club_days,
                "club_description": club_description,
                "club_name": club_name,
                "president_email": president_email,
                "room_number": room_number,
                "secret_password": secret_password,
                "start_time": start_time,
                "status": status,
                "vice_presidents_emails": vice_presidents_emails
            }
        )
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}
    
def update_status(secret_password, status):
    collection = "Clubs"
    doc_id = get_el_id(collection, secret_password)
    try:
        db.collection(collection).document(doc_id).update(
            {
                "status": status
            }
        )
        return {"status": "Successfully changed status"}
    except Exception as e:
        return {"status": f"Failed to change status: {e}"}
    
def get_members(club_id):
    return db.collection("Clubs").document(club_id).get().to_dict()["members"]
    
def manage_members(secret_password, new_members):
    collection = "Clubs"
    doc_id = get_el_id(collection, secret_password)
    try:
        db.collection(collection).document(doc_id).update(
            {
                "members": new_members
            }
        )
        return {"status": "Successfully updated members"}
    except Exception as e:
        return {"status": f"Failed to update members: {e}"}
    
def remove_club(club_id):
    try:
        db.collection("Clubs").document(club_id).delete()
        # Also have to delete from joined club of every user, etc.
        return {"status": "Successfully deleted club"}
    except Exception as e:
        return {"status": f"Failed to delete club: {e}"}