from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from models.usermodel import make_user, change_user, verify_token, get_current_user, get_user_from_email, join_leave_club
from typing import Annotated, List
from models.model import get_el_id, get_doc

router = APIRouter(
    tags=["user"]
)

class User(BaseModel):
    email: str
    is_leader: bool
    role: str
    leading: List[str]
    joined_clubs: List[str]
    
@router.post("/createuser/")
async def create_user(user: User):
    return make_user(user.email, user.is_leader, user.role, user.leading, user.joined_clubs)

@router.post("/updateuser/")
async def update_user(user: User):
    return change_user(user.email, user.is_leader, user.password, user.role)

class Token(BaseModel):
    token: str

@router.post("/verify-token")
def verify_token_route(token: Token):
    decoded_token = verify_token(token.token)
    return {"uid": decoded_token["uid"], "email": decoded_token.get("email")}

@router.get("/protected")
def protected_route(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = auth_header.split("Bearer ")[-1]
    decoded_token = verify_token(token)
    return {"message": "You are authorized", "user_id": decoded_token["uid"]}

# New endpoint to handle additional user creation logic
@router.post("/create-user")
def create_user_route(token: Token):
    # Creates / adds the user into the Google Firebase Authentication:
    decoded_token = verify_token(token.token)
    # Creates / adds the user into the Google Firebase Firestore Database:
    # user = User()
    print(f"successfully created user: {decoded_token['uid']}")
    return {"status": "User created successfully", "user_id": decoded_token["uid"]}

@router.post("/make-user")
def make_new_user(user: User):
    try:
        make_user(user.email, user.is_leader, user.role, user.leading, user.joined_clubs)
        return {"status": "Successfully made user"}
    except Exception as e:
        return {"status": f"Failed to make user: {e}"}

@router.get("/user-info")
def get_user_info(current_user: dict = Depends(get_current_user)):
    email = current_user.get("email")
    uid = current_user.get("uid")
    # Create the User document in Firestore here.
    return {"uid": uid, "email": email}

@router.get("/getuserdocdata/{email}")
def get_user_doc_data(email: str):
    try:
        return get_user_from_email(email)
    except Exception as e:
        return {"status": f"Faield to getuserdocfromdata: {e}"}
    
@router.get("/toggleclub/{email}/{club_id}")
def toggle_club(email: str, club_id: str):
    clubs = get_user_from_email(email)["joined_clubs"]
    print(clubs)

    if club_id in clubs:
        try:
            join_leave_club("leave", email, club_id)
            return {"status": "Successfully left club"}
        except Exception as e:
            return {"status": f"Failed to leave club: {e}"}
    else:
        try:
            join_leave_club("join", email, club_id)
            return {"status": "Successfully joined club"}
        except Exception as e:
            return {"status": f"Failed to leave club: {e}"}
