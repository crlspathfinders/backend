import os, secrets, uuid, random, string
from typing import Annotated, List
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from models.allinfomodel import add_document_to_all_info_collection, update_all_info_collection, update_doc
from models.model import get_doc

from models.alumnimodel import (
    make_alumni
)
from models.redismodel import add_redis_collection

load_dotenv()

security = HTTPBasic()
router = APIRouter(tags=["alumni"])

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

class Alum(BaseModel):
    firstname: str
    lastname: str
    gradyear: int
    fullschool: str
    shortschool: str
    major: str
    bio: str
    loc: str
    coords: List[str]
    logo: str

@router.post("/addalumni/")
def add_alumni(alum: Alum, username: Annotated[str, Depends(get_current_username)]):
    try:
        new_alum = alum.model_dump()
        # print(new_alum)
        res = make_alumni(new_alum)
        # print(res)
        if res["status"] == 0:
            # Update and increment AllInfo/universities
            new_id = str(generate_rand_id())
            universities = get_doc("AllInfo", "universities")
            unis = list(universities.keys())
            # print(unis)
            for u in unis:
                curr_uni = universities[u]
                # print(curr_uni)
                if curr_uni["name"] == alum.fullschool:
                    # print("found")
                    universities[u]["amount_in"] += 1
                    update_doc("universities", universities)
                    return {"status": 0}
            # print("not found")
            new_uni = {
                "name": alum.fullschool,
                "loc": alum.loc,
                "amount_in": 1,
                "coords": alum.coords,
                "logo": alum.logo
            }
            # print(new_uni)
            universities[new_id] = new_uni
            # print(universities)
            # print("starting update all info collection")
            update_doc("universities", universities)
            return {"status": 0}
        return {"status": -1, "error_message": res["error_message"]}
    except Exception as e:
        return {"status": -1, "error_message": e}

def generate_rand_id(length=20):
    chars = string.ascii_letters 
    return ''.join(random.choices(chars, k=length))