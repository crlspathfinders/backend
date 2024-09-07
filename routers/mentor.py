from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from models.mentormodel import make_mentor, change_mentor, remove_mentor, upload_mentor_image, set_mentor_image_doc
from fastapi import FastAPI, File, UploadFile, HTTPException
from sendmail import send_mail

router = APIRouter(
    tags=["mentor"]
)

class Mentor(BaseModel):
    firstname: str
    lastname: str
    bio: str
    email: str
    races: List[str]
    religions: List[str]
    gender: List[str] # Change to just a string later
    languages: List[str]
    academics: List[str]

@router.post("/creatementor/")
async def create_mentor(mentor: Mentor):
    try:
        print("create mentor start")
        make_mentor(mentor.firstname, mentor.lastname, mentor.bio, mentor.email, mentor.races, mentor.religions, mentor.gender, mentor.languages, mentor.academics)
        print("create mentor end")
        return {"status": "Successfully created mentor"}
    except Exception as e:
        return {"status": f"Failed to create mentor: {e}"}

@router.post("/updatementor/")
async def update_mentor(mentor: Mentor):
    try:
        change_mentor(mentor.firstname, mentor.lastname, mentor.bio, mentor.email, mentor.races, mentor.religions, mentor.gender, mentor.languages, mentor.academics)
        return {"status": "Successfully edited mentor"}
    except Exception as e:
        return {"status": f"Failed to edit mentor: {e}"}
    
@router.get("/deletementor/{email}")
async def delete_mentor(email: str):
    try:
        remove_mentor(email)
        return {"Status": "Successfully deleted mentor"}
    except Exception as e:
        return {"status": f"Failed to delete mentor: {e}"}
    
@router.post("/uploadmentorimage/")
async def upload_image(file: UploadFile = File(...)):
    print(file)
    try:
        img_url = upload_mentor_image(file)
        print(f"successfully uploaded mentor img: {img_url}")
        return {"status": img_url}
    except Exception as e:
        print(f"Failed: {e}")
        return {"status": "Failed"}
    
class SetClubImg(BaseModel):
    img_url: str
    mentor_email: str

@router.post("/setmentorimg/")
async def set_club_img(upload: SetClubImg):
    if upload.img_url != "Failed":
        set_mentor_image_doc(upload.mentor_email, upload.img_url)
        return {"status": "Successfully updated mentor img doc"}
    else:
        print(f"Failed to update mentor img doc.")
        return {"status": f"Failed to update mentor img doc."}

class MentorPitch(BaseModel):
    mentor_email: str
    pitch: str 

@router.post("/sendmentorpitch/")
async def send_mentor_pitch(mentor_pitch: MentorPitch):
    receiver = "crlspathfinders25@gmail.com"
    subject = f"Mentor pitch from {mentor_pitch.mentor_email}"
    body = f'''Mentor pitch received from {mentor_pitch.mentor_email}

Pitch:
{mentor_pitch.pitch}
    '''
    try:
        send_mail(receiver, subject, body)
        print("Sent mentor pitch mail")
        return {"status": "Sent mentor pitch mail"}
    except Exception as e:
        print(f"Failed to send mentor pitch email: {e}")
        return {"status": f"Failed to send mentor pitch email: {e}"}