from fastapi import APIRouter
from pydantic import BaseModel
from models.usermodel import make_user, change_user

router = APIRouter(
    tags=["user"]
)

class User(BaseModel):
    email: str
    is_leader: bool
    password: str
    role: str
    
@router.post("/createuser/")
async def create_user(user: User):
    return make_user(user.email, user.is_leader, user.password, user.role)

@router.post("/updateuser/")
async def update_user(user: User):
    return change_user(user.email, user.is_leader, user.password, user.role)