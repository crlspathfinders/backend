from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from models.clubmodel import make_club, change_club, update_status, remove_club, verify_club_model, upload_club_image, set_club_image_doc
from models.model import get_collection_python, get_el_id, get_doc
from models.usermodel import join_leave_club
from sendmail import send_mail
from dotenv import load_dotenv
import os
from fastapi import FastAPI, File, UploadFile, HTTPException

load_dotenv()

router = APIRouter(
    tags=["club"]
)

class Club(BaseModel):
    advisor_email: str
    club_days: List[str]
    club_description: str
    club_name: str
    president_email: str
    room_number: int
    google_classroom_link: str
    secret_password: int
    start_time: str
    status: str
    vice_president_emails: List[str]

@router.post("/createclub/")
async def create_info(club: Club):
    try:
        # Client side makes sure that the president email and advisor emails are correct, etc.
        # Make club will make create it as Pending -> will wait for advisor verification to Approve it.
        make_club(club.advisor_email, club.club_days, club.club_description, club.club_name, club.president_email, club.room_number, club.google_classroom_link, club.secret_password, club.start_time, club.status, club.vice_president_emails)
        # Now have to send email to advisor with password:
        receiver = club.advisor_email
        subject = f"CRLS Pathfinders | {club.club_name} Confirmation Code"
        body = f'''CODE: {club.secret_password}

{club.president_email} is registering their club on the CRLS PathFinders website.
To verify {club.club_name}, log into the PathFinders website, select your email in the top right corner, hit "Verify Club," and then input the code above.
Once successful, {club.club_name} should appear after hitting "Find a Club."

If there are any problems, send me an email @25ranjaria@cpsd.us
'''
        try:
            send_mail(receiver, subject, body)
            print("Sent mail")
        except Exception as e:
            print(f"Failed to send mail: {e}")
            return {"status": f"Failed to send mail: {e}"}
        return {"status": "Successfully created club"}
    except Exception as e:
        return {"status": f"Failed to create club: {e}"}

@router.post("/updateclub/")
async def update_club(club: Club):
    try:
        change_club(club.advisor_email, club.club_days, club.club_description, club.club_name, club.president_email, club.room_number, club.google_classroom_link, club.secret_password, club.start_time, club.status, club.vice_president_emails)
        return {"status": "Successfully edited club"}
    except Exception as e:
        return {"status": f"Failed to edit club: {e}"}

class ChangeStatus(BaseModel):
    secret_password: int
    status: str

@router.post("/changestatus/")
def change_status(change_status: ChangeStatus):
    try:
        update_status(change_status.secret_password, change_status.status)
        return {"status": "Successfully changed status"}
    except Exception as e:
        return {"status": f"Failed to change status: {e}"}
    
@router.get("/deleteclub/{club_id}")
def delete_club(club_id: str):
    try:
        remove_club(club_id)
        # Now remove this club from all of the users who are members of this club:
        users = get_collection_python("Users")
        print(f"57 - {users}")
        for u in users:
            if len(u["joined_clubs"]) > 0:
                if club_id in u["joined_clubs"]:
                    print("59 - Found!")
                    join_leave_club("leave", u["email"], club_id)
                else: print("61 - Not found")
        return {"status": "Successfully deleted club"}
    except Exception as e:
        return {"status": f"Failed to delete club: {e}"}
    
class VerifyClub(BaseModel):
    secret_password: int

@router.post("/verifyclub")
def verify_club(verify: VerifyClub):
    try:
        status = verify_club_model(verify.secret_password)
        # print()
        return status
    except Exception as e:
        print(f"Club verification failed: {e}")
        return {"status": "Failed", "error": e}

@router.post("/uploadclubimage/")
async def upload_image(file: UploadFile = File(...)):
    print(file)
    try:
        img_url = upload_club_image(file)
        print(f"successfully uploaded club img: {img_url}")
        return {"status": img_url}
    except Exception as e:
        print(f"Failed: {e}")
        return {"status": "Failed"}
    
class SetClubImg(BaseModel):
    img_url: str
    club_id: str

@router.post("/setclubimg/")
async def set_club_img(upload: SetClubImg):
    if upload.img_url != "Failed":
        set_club_image_doc(upload.club_id, upload.img_url)
        return {"status": "Successfully updated club img doc"}
    else:
        print(f"Failed to update club img doc.")
        return {"status": f"Failed to update club img doc."}