import httpx
import os
import secrets
from typing import Annotated

from dotenv import load_dotenv
from fastapi import (
    Depends,
    HTTPException,
    status,
    APIRouter,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials

load_dotenv()

security = HTTPBasic()

router = APIRouter(tags=["libraryinfo"])


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


@router.get("/getlibraryinfo/")
async def get_library_info(username: Annotated[str, Depends(get_current_username)]):
# async def get_library_info():
    try:
        url = os.environ.get("LIBRARY_INFO_URL")
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Raise exception for HTTP errors
            return {"status": 0, "data": response.json()}
    except Exception as e:
        return {"status": -1, "error_message": e}
