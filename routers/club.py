import os
import secrets
from typing import List, Optional, Annotated

from dotenv import load_dotenv
from fastapi import (
    File,
    UploadFile,
    Depends,
    HTTPException,
    status,
    APIRouter,
    Form,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from models.clubmodel import (
    make_club,
    change_club,
    update_status,
    remove_club,
    verify_club_model,
    upload_club_image,
    delete_club_image,
    set_club_image_doc,
)
from models.model import (
    get_el_id,
    get_collection_id,
)
from models.redismodel import (
    add_redis_collection_id,
    delete_redis_id,
    add_redis_collection,
)
from sendmail import send_mail

load_dotenv()

security = HTTPBasic()
router = APIRouter(tags=["club"])


class Club(BaseModel):
    advisor_email: str
    club_days: List[str]
    club_description: str
    club_name: str
    president_email: str
    room_number: str
    google_classroom_link: str
    secret_password: int
    start_time: str
    status: str
    vice_president_emails: List[str]


class ChangeStatus(BaseModel):
    secret_password: int
    status: str


class VerifyClub(BaseModel):
    secret_password: int


class SetClubImg(BaseModel):
    img_url: str
    club_id: str
    old_id: str


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = bytes(os.environ.get("AUTH_USERNAME"), "utf-8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = bytes(os.environ.get("AUTH_PASSWORD"), "utf-8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.post("/createclub/")
async def create_info(club: Club):
    try:
        # Client side makes sure that the president email and advisor emails are correct, etc.
        # Make club will make create it as Pending -> will wait for advisor verification to Approve it.
        print("starting make club")
        make_club(
            club.advisor_email,
            club.club_days,
            club.club_description,
            club.club_name,
            club.president_email,
            club.room_number,
            club.google_classroom_link,
            club.secret_password,
            club.start_time,
            club.status,
            club.vice_president_emails,
        )
        print("done make club")

        club_id = get_el_id("Clubs", club.secret_password)
        print(f"clubid: {club_id}")
        coll_id = get_collection_id("Clubs", club_id)
        print("collid: {coll_id}")
        print(add_redis_collection_id("Clubs", coll_id, club_id=club_id))
        print(add_redis_collection("Users"))

        # Now have to send email to advisor with password:
        receiver = club.advisor_email
        subject = f"CRLS Pathfinders | {club.club_name} Confirmation Code"
        body = f"""CODE: {club.secret_password}

{club.president_email} is registering their club on the CRLS PathFinders website, crlspathfinders.com.
To verify {club.club_name}, you can either email them your code, and they can verify themself, or you can log into the PathFinders website, select your email in the top right corner, hit "Verify Club," and then input the code above.
Once successful, {club.club_name} should appear after hitting "Find a Club."

Thank you, and if there are any problems, send me an email @25ranjaria@cpsd.us
"""
        try:
            send_mail(receiver, subject, body)
            print("sent first mail")
        except Exception as e:
            print(f"Failed to send mail: {e}")
            return {"status": -16, "error_message": e}

        # Now send email to the club president:
        receiver = club.president_email
        subject = f"CRLS Pathfinders | {club.club_name} Confirmation Code"
        body = f"""Hello {club.president_email},

CONFIRMATION CODE: {club.secret_password}

We have received {club.club_name}'s registration.  
To verify {club.club_name}, log into crlspathfinders.com, select your email in the top right corner, hit "Verify Club," and then input the code above.
Once successful, {club.club_name} will appear after hitting "Find a Club." Try reloading the page if it's not there.

Thank you, and if there are any problems, send me an email @25ranjaria@cpsd.us
"""
        try:
            send_mail(receiver, subject, body)
            print("sent second mail")
        except Exception as e:
            print(f"Failed to send mail: {e}")
            return {"status": -16, "error_message": e}
        
        receiver = "crlspathfinders25@gmail.com"
        subject = f"{club.club_name} | Club Registration"
        body = f"""Club registration confifrmation for {club.club_name}

Advisor: {club.advisor_email}
Days: {club.club_days}
Description: {club.club_description}
Name: {club.club_name}
President: {club.president_email}
Room: {club.room_number}
Google Classroom: {club.google_classroom_link}
Password: {club.secret_password}
Start Time: {club.start_time}
Status: {club.status}
Vice Presidents: {club.vice_president_emails}
"""
        
        try:
            send_mail(receiver, subject, body)
            print("sent second mail")
        except Exception as e:
            print(f"Failed to send mail: {e}")
            return {"status": -16, "error_message": e}

        return {"status": 0}
    except Exception as e:
        return {"status": -17, "error_message": e}


@router.post("/updateclub/")
async def update_club(club: Club):
    try:
        change_club(
            club.advisor_email,
            club.club_days,
            club.club_description,
            club.club_name,
            club.president_email,
            club.room_number,
            club.google_classroom_link,
            club.secret_password,
            club.start_time,
            club.status,
            club.vice_president_emails,
        )
        club_id = get_el_id("Clubs", club.secret_password)
        coll_id = get_collection_id("Clubs", club_id)
        add_id = add_redis_collection_id("Clubs", coll_id, club_id=club_id)
        if add_id["status"] == 0:
            return {"status": 18}
        return {"status": -18.1}
    except Exception as e:
        return {"status": -18, "error_message": e}


@router.post("/changestatus/")
def change_status(change_status: ChangeStatus):
    try:
        update_status(change_status.secret_password, change_status.status)
        club_id = get_el_id("Clubs", change_status.secret_password)
        coll_id = get_collection_id("Clubs", club_id)
        add_redis_collection_id("Clubs", coll_id, club_id=club_id)
        return {"status": 19}
    except Exception as e:
        return {"status": -19, "error_message": e}


@router.get("/deleteclub/{club_id}")
def delete_club(club_id: str):
    try:
        del_id = delete_redis_id("Clubs", club_id)
        if del_id["status"] == 0:
            remove_club(club_id)
            # Now remove this club from all the users who are members of this club:
            # users = get_collection_python("Users")
            # print(f"57 - {users}")
            # for u in users:
            #     if len(u["joined_clubs"]) > 0:
            #         if club_id in u["joined_clubs"]:
            #             print("59 - Found!")
            #             join_leave_club("leave", u["email"], club_id)
            #         else:
            #             print("61 - Not found")
            return {"status": 20}
        return {"status": -20.1}

    except Exception as e:
        return {"status": -20, "error_message": e}


@router.post("/verifyclub")
def verify_club(verify: VerifyClub):
    try:
        verify_club_model(verify.secret_password)
        return {"status": 0}
    except Exception as e:
        return {"status": -21, "error_message": e}


@router.post("/uploadclubimage/")
async def upload_image(
    file: UploadFile = File(...),
    old_file_name: Optional[str] = Form(None),
):
    print(file)
    try:
        # Validate file type
        if file.content_type not in [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/gif",
            "image/webp",
        ]:
            return {"status": -22.1}
        if old_file_name:
            delete_club_image(old_file_name)

        upload_club_image(file)
        return {"status": 22}
    except Exception as e:
        return {"status": -22, "error_message": e}


@router.post("/setclubimg/")
async def set_club_img(upload: SetClubImg):
    if upload.img_url != "Failed":
        set_club_image_doc(upload.club_id, upload.img_url, upload.old_id)
        coll_id = get_collection_id("Clubs", upload.club_id)
        add_redis_collection_id("Clubs", coll_id, club_id=upload.club_id)
        return {"status": 23}
    else:
        return {"status": -23}
