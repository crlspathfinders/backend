from .model import db, get_el_id, get_doc, storage
from .usermodel import change_user_role, change_is_mentor
from fastapi import FastAPI, File, UploadFile, HTTPException
from uuid import uuid4
from io import BytesIO

def make_mentor(firstname, lastname, bio, email, race, religion, gender, languages, academics):
    # Need to pass in the id, etc for which collection to actually change.
    collection = "Mentors"
    print("make mentor begin")
    try:
        result = db.collection(collection).add(
            {
                "firstname": firstname,
                "lastname": lastname,
                "bio": bio,
                "email": email,
                "races": race,
                "religions": religion,
                "gender": gender,
                "languages": languages,
                "academics": academics,
                "profile_pic": "",
                "show": True
                # Need to add img_url
            }
        )
        print(result)
        mentor_role = get_doc("Users", get_el_id("Users", email))["role"]
        print(f"Mentor role: {mentor_role}")
        if mentor_role == "Member":
            change_user_role(email, "Mentor")
            print(f"changed {email} role to mentor")
        change_is_mentor(email, True)
        print(f"changed {email} is mentor")
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}
    
def change_mentor(firstname, lastname, bio, email, race, religion, gender, languages, academics):
    collection = "Mentors"
    doc_id = get_el_id("Mentors", email)
    try:
        result = db.collection(collection).document(doc_id).update(
            {
                "firstname": firstname,
                "lastname": lastname,
                "bio": bio,
                "email": email,
                "races": race,
                "religions": religion,
                "gender": gender,
                "languages": languages,
                "academics": academics
                # Need to add img_url
            }
        )
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}
    
def remove_mentor(email):
    doc_id = get_el_id("Mentors", email)
    try:
        db.collection("Mentors").document(doc_id).delete()
        return {"Status": "Successfully deleted mentor"}
    except Exception as e:
        return {"status": f"Failed to delete mentor: {e}"}
    
# Make function that deletes old mentor image (look on google or chatgpt how to delte firebase storage images from a url)

def upload_mentor_image(file: UploadFile = File(...)):
    try:
        # Generate a unique file name
        file_name = f"{uuid4()}.jpg"
        blob = storage.bucket().blob(f'mentor-images/{file_name}')

        # Upload the image
        blob.upload_from_file(file.file, content_type=file.content_type)
        blob.make_public()

        image_url = blob.public_url

        print(f"Successfully uploaded image: {image_url}")
        return image_url
    except Exception as e:
        print(f"Failed to upload img: {e}")
        return "Failed"
    
def set_mentor_image_doc(mentor_email, img_url):
    mentor_id = get_el_id("Mentors", mentor_email)
    print(f"mentor id: {mentor_id}, email: {mentor_email}")
    try:
        db.collection("Mentors").document(mentor_id).update(
            {
                "profile_pic": img_url
            }
        )
        return {"status": "Successfully updated mentor img doc"}
    except Exception as e:
        print(f"Failed to update mentor img doc: {e}")
        return {"status": f"Failed to update mentor img doc: {e}"}
    
def show_or_hide_mentor(mentor_email):
    doc_id = get_el_id("Mentors", mentor_email)
    mentor = get_doc("Mentors", doc_id)
    toggle = not mentor["show"]
    # print(not toggle)
    try:
        db.collection("Mentors").document(doc_id).update(
            {
                "show": toggle
            }
        )
    except Exception as e:
        print(f"Failed to show or hide mentor: {e}")
        return {"status": f"Failed to show or hide mentor: {e}"}