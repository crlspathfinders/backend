from .model import db, get_el_id

def make_user(email, is_leader, password, role):
    collection = "Users"
    try:
        result = db.collection(collection).add(
            {
                "email": email,
                "is_leader": is_leader,
                "password": password,
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