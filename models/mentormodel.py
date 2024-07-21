from .model import db, get_el_id

def make_mentor(firstname, lastname, email, race, religion, gender, languages, academics):
    # Need to pass in the id, etc for which collection to actually change.
    collection = "Mentors"
    try:
        result = db.collection(collection).add(
            {
                "firstname": firstname,
                "lastname": lastname,
                "email": email,
                "race": race,
                "religioin": religion,
                "gender": gender,
                "languages": languages,
                "academics": academics
                # Need to add img_url
            }
        )
        print(result)
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}
    
def change_mentor(firstname, lastname, email, race, religion, gender, languages, academics):
    collection = "Mentors"
    doc_id = get_el_id("Clubs", email)
    try:
        result = db.collection(collection).document(doc_id).update(
            {
                "firstname": firstname,
                "lastname": lastname,
                "email": email,
                "race": race,
                "religioin": religion,
                "gender": gender,
                "languages": languages,
                "academics": academics
            }
        )
        print(result)
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}