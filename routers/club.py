from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from models.clubmodel import make_club, change_club, update_status

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
    secret_password: int
    start_time: str
    status: str
    vice_president_emails: List[str]

@router.post("/createclub/")
async def create_info(club: Club):
    try:
        make_club(club.advisor_email, club.club_days, club.club_description, club.club_name, club.president_email, club.room_number, club.secret_password, club.start_time, club.status, club.vice_president_emails)
        return {"status": "Successfully created club"}
    except Exception as e:
        return {"status": f"Failed to create club: {e}"}

@router.post("/updateclub/")
async def update_club(club: Club):
    try:
        change_club(club.advisor_email, club.club_days, club.club_description, club.club_name, club.president_email, club.room_number, club.secret_password, club.start_time, club.status, club.vice_president_emails)
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