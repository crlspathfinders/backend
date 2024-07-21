from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from models.clubmodel import make_club, change_club

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
    secret_password: str
    start_time: str
    status: str
    vice_president_emails: List[str]

@router.post("/createclub/")
async def create_info(club: Club):
    return make_club(club.advisor_email, club.club_days, club.club_description, club.club_name, club.president_email, club.room_number, club.secret_password, club.start_time, club.status, club.vice_president_emails)

@router.post("/updateclub/")
async def update_club(club: Club):
    return change_club(club.advisor_email, club.club_days, club.club_description, club.club_name, club.president_email, club.room_number, club.secret_password, club.start_time, club.status, club.vice_president_emails)