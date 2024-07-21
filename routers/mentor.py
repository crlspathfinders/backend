from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from models.mentormodel import make_mentor, change_mentor

router = APIRouter(
    tags=["mentor"]
)

class Mentor(BaseModel):
    firstname: str
    lastname: str
    email: str
    race: str # Maybe a list (??)
    religion: str
    gender: str
    languages: List[str]
    academics: List[str]

@router.post("/creatementor/")
async def create_mentor(mentor: Mentor):
    return make_mentor(mentor.firstname, mentor.lastname, mentor.email, mentor.race, mentor.religion, mentor.gender, mentor.languages, mentor.academics)

@router.post("/updatementor/")
async def update_mentor(mentor: Mentor):
    return change_mentor(mentor.firstname, mentor.lastname, mentor.email, mentor.race, mentor.religion, mentor.gender, mentor.languages, mentor.academics)