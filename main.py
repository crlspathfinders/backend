from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from cloudinary.utils import cloudinary_url
import os, sys, io
import json, tempfile, mimetypes
from fastapi.responses import StreamingResponse
from typing import List
from datetime import timedelta
from pydantic import BaseModel
from models.model import get_collection_id, get_collection, get_sub_collection, remove_id, get_collection_python
from routers import user, club, mentor, peermentor
from requests_cache import CachedSession
from dotenv import load_dotenv
from sendmail import send_mail
from fastapi_cache.decorator import cache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from redis import Redis

load_dotenv()
curr_url = os.environ.get("CURR_URL")

# from google.cloud import storage

# DO NOT IMPORT PYRBASE (GIVES THE MUTABLEMAPPING ERROR)!!!

# CORS Documentation: https://fastapi.tiangolo.com/tutorial/cors/

# Create virtual environment: python3 -m venv venv

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "http://localhost",
    "http://localhost:8080",
    "https://crlspathfinders-frontend.vercel.app",
    "https://www.crlspathfinders.com",
    "https://www.crlspathfinders.com/",
    "crlspathfinders.com",
    "crlspathfinders.com/",
    "https://crlspathfinders-backend.vercel.app",
    "https://crlspathfinders-backend.vercel.app/",
    "https://crlspathfinders-backend.vercel.app/cache/Mentors"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(club.router)
app.include_router(mentor.router)
app.include_router(peermentor.router)

# Model schemas:

# uvicorn main:app --reload
# Read a document:

# Caching:

cached_mentors = CachedSession(
    cache_name="cache/Mentors",
    expire_after=10 # 10 s
)

@app.get("/cache/{collection}")
def cache_mentors(collection: str):
    mentors = cached_mentors.get(f"{curr_url}/read/{collection}")
    return mentors.json()

@app.get("/")
def home():
    return {"status": "rehaan"}

@app.get("/add/{num1}/{num2}")
def add_nums(num1: int, num2: int):
    result = num1 + num2
    return {"data": result}

@app.get("/testonetwothree")
def test():
    return {"hello": "world"}

@app.get("/read/{collection}/{id}")
async def read_document(collection: str, id: str):
    return get_collection_id(collection, id)

# Read a collection:
# @app.get("/read/{collection}")
# async def read_collection(collection: str):
#     return get_collection(collection)

# Simulate the get_collection function
# def get_collection(collection: str):
#     # Simulate a slow operation or a database call
#     return {"collection": collection, "data": f"Data from {collection}"}

# Cache initialization with Redis
@app.on_event("startup")
async def startup_event():
    redis = Redis(host="localhost", port=6379, decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# Cached endpoint
@app.get("/read/{collection}")
@cache(expire=60) 
async def read_collection(collection: str):
    print("caching")
    return get_collection(collection)

# Read a sub-collection
@app.get("/read/{collection}/{id}/{subcollection}")
async def read_sub_collection(collection: str, id: str, subcollection: str):
    return get_sub_collection(collection, id, subcollection)

# Delete (delete the document itself, not the info, so only need the document parameter):
@app.get("/delete/{collection}/{id}")
async def delete_info(collection: str, id: str):
    return remove_id(collection, id)

class SendMassEmail(BaseModel):
    collection: str
    subject: str
    body: str

@app.post("/emailall/")
def email_all(email: SendMassEmail):
    sendees = get_collection_python(email.collection)
    emails = []
    if email.collection == "Clubs":
        for s in sendees: 
            emails.append(s["president_email"])
            if len(s["vice_presidents_emails"]) > 0:
                for v in s["vice_presidents_emails"]:
                    emails.append(v)
        try:
            send_mail(emails, email.subject, email.body)
            return {"status": 0}
        except Exception as e:
            return {"status": -1, "error_message": e}
    else:             
        for s in sendees: emails.append(s["email"])
        try:
            send_mail(emails, email.subject, email.body)
            return {"status": 0}
        except Exception as e:
            return {"status": -1, "error_message": e}