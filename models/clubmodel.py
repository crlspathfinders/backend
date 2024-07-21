from .model import db, get_el_id

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
                "vice_presidents_emails": vice_presidents_emails
                # Need to add img_url
            }
        )
        print(result)
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}
    
def change_club(advisor_email, club_days, club_description, club_name, president_email, room_number, secret_password, start_time, status, vice_presidents_emails):
    collection = "Clubs"
    doc_id = get_el_id("Clubs", club_name)
    try:
        result = db.collection(collection).document(doc_id).update(
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
        print(result)
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}