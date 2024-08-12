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
    races: List[str]
    religions: List[str]
    gender: List[str] # Change to just a string later
    languages: List[str]
    academics: List[str]

@router.post("/creatementor/")
async def create_mentor(mentor: Mentor):
    try:
        make_mentor(mentor.firstname, mentor.lastname, mentor.email, mentor.races, mentor.religions, mentor.gender, mentor.languages, mentor.academics)
        return {"status": "Successfully created mentor"}
    except Exception as e:
        return {"status": f"Failed to create mentor: {e}"}

@router.post("/updatementor/")
async def update_mentor(mentor: Mentor):
    try:
        change_mentor(mentor.firstname, mentor.lastname, mentor.email, mentor.races, mentor.religions, mentor.gender, mentor.languages, mentor.academics)
        return {"status": "Successfully edited mentor"}
    except Exception as e:
        return {"status": f"Failed to edit mentor: {e}"}