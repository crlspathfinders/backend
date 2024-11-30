from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import List
from models.mentormodel import make_mentor, change_mentor, remove_mentor, upload_mentor_image, set_mentor_image_doc, show_or_hide_mentor
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
    
# Make router that accepts deleted image and calls the function to delete the image in mentormodel.py
'''
@router.get("/deleteimage/{old_url})
def delete_img(old_url: str):
    return handle_delete_img(old_url)
'''
# Something like that^

@router.post("/uploadmentorimage/")
async def upload_image(file: UploadFile = File(...), old_file_name: Optional[str] = Form(None)):
    print(file)
    try:
        # Validate file type
        if file.content_type not in ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, JPG, PNG, WEBP, and GIF are allowed.")
        if old_file_name:
            delete_mentor_image(old_file_name)
            
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
        print("Failed to update mentor img doc.")
        return {"status": "Failed to update mentor img doc."}

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

class MentorMenteeLog(BaseModel):
    mentor_email: str
    mentee_email: str
    log_description: str
    log_hours: str

@router.post("/mentormenteelogs/")
def log_mentor_mentee(log: MentorMenteeLog):
    # Send crlspathfinders25 the log, send mentor the confirmation, and send mentee the confirmation.
    try:

        # Send to crlspathfinders25:
        receiver = "crlspathfinders25@gmail.com"
        subject = f"Mentor-Mentee Logging form from {log.mentor_email}"
        body = f'''{log.mentor_email} has submitted a logging form.

Description: {log.log_description}

Hours: {log.log_hours}
'''
        send_mail(receiver, subject, body)    
        
        # Send email to mentor:
        receiver = log.mentor_email
        subject = f"Confirmation of Mentor-Mentee Logging form"
        body = f'''Hello,

You have successfully logged your hours. The CRLS PathFinders team has recieved your hours, and a confirmation email has been sent to your mentee, {log.mentee_email}. Once they have confirmed that the hours are correct, your hours will be logged and you can receieve community service hours for your work.
Below are your responses. To change anything, please send an email to crlspathfinders25@gmail.com or just fill out a new form.

Description: {log.log_description}

Hours: {log.log_hours}

Thank you,
CRLS PathFinders,
Rehaan Anjaria '25
Abel Asefaw '25
'''
        send_mail(receiver, subject, body)

        # Send email to mentee:
        receiver = log.mentee_email
        subject = f"Mentor-Mentee Logging form from {log.mentor_email}"
        body = f'''Hello,

Your mentor, {log.mentor_email}, has submitted a logging form. If they are not your mentor, please ignore this message.

Please confirm that the below hours are correct. If you have any questions please reach out to your mentor at {log.mentor_email} or email us with any questions at crlspathfinders25@gmail.com

Hours: {log.log_hours}

Thank you,
CRLS PathFinders,
Rehaan Anjaria '25
Abel Asefaw '25
'''
            
        send_mail(receiver, subject, body)
        return {"status": "Successfully send logging email"}
    except Exception as e:
        return {"status": "Failed to send logging email: {e}"}

@router.get("/toggleshowmentor/{mentor_email}/")
def toggle_show_mentor(mentor_email: str):
    return show_or_hide_mentor(mentor_email)