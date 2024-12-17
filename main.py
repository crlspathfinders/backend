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
from upstash_redis import Redis
from models.redismodel import get_redis_collection, add_redis_collection, get_redis_collection_id, add_redis_collection_id, delete_redis_data
from fastapi.responses import JSONResponse

load_dotenv()
curr_url = os.environ.get("CURR_URL")

# Redis testing:

redis = Redis(url=os.environ.get("REDIS_URL"), token=os.environ.get("REDIS_TOKEN"))

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
    "https://crlspathfinders-backend.vercel.app/cache/Mentors",
    "https://crlspathfinders-frontend-44w5k1duv-rehaan12345s-projects.vercel.app/",
    "https://crlspathfinders-frontend-exrq8i8v2-rehaan12345s-projects.vercel.app/"
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
    coll_id = get_redis_collection_id(collection, id)
    status = coll_id["status"]
    if status == 0: # Found
        return {"status": 0, "collid": coll_id["target_val"]}
    if status == -4: # No collection id found
        coll_id = get_collection_id(collection, id)
        add_id = add_redis_collection_id(collection, coll_id)
        if add_id["status"] == 0:
            return {"status": 0, "collid": coll_id}
        return {"status": -1, "error_message": add_id["error_message"]}
    if status == -1:
        return {"status": -1, "error_message": coll_id["error_message"]}

# Read a collection:
@app.get("/read/{collection}")
async def read_collection(collection: str):
    
    redis_collection = get_redis_collection(collection)
    status = redis_collection["status"]

    if status == 0: # Found
        return {"status": 0, "collection": redis_collection["results"]}

    if status == -3: # No cache (collection not in redis)
        # If not in cache, then add it to cache
        add_collection = add_redis_collection(collection)
        if add_collection["status"] == 0:
            return {"status": 0, "collection": add_collection["collection"]}
        return {"status": -1, "error_message": add_collection["error_message"]}
    
    if status == -1:
        return {"status": -1, "error_message": redis_collection["error_message"]}

# @app.get("/read/{collection}")
# async def read_collection(collection: str):
#     # Attempt to retrieve the collection from Redis
#     redis_collection = get_redis_collection(collection)
#     status = redis_collection["status"]

#     if status == 0:  # Found in cache
#         response = {"status": 0, "collection": redis_collection["results"]}
#         # Add Cache-Control headers to allow caching
#         headers = {"Cache-Control": "public, max-age=3600"}  # Cache for 1 hour
#         print(headers)
#         return JSONResponse(content=response, headers=headers)

#     if status == -3:  # Not in cache (Redis miss)
#         # Attempt to add the collection to Redis
#         add_collection = add_redis_collection(collection)
#         if add_collection["status"] == 0:
#             response = {"status": 0, "collection": add_collection["collection"]}
#             headers = {"Cache-Control": "public, max-age=3600"}  # Cache for 1 hour
#             return JSONResponse(content=response, headers=headers)
#         # Return error if adding to Redis fails
#         response = {"status": -1, "error_message": add_collection["error_message"]}
#         headers = {"Cache-Control": "no-store"}  # Avoid caching errors
#         return JSONResponse(content=response, headers=headers)

#     if status == -1:  # General error from Redis
#         response = {"status": -1, "error_message": redis_collection["error_message"]}
#         headers = {"Cache-Control": "no-store"}  # Avoid caching errors
#         return JSONResponse(content=response, headers=headers)

# Read a sub-collection
@app.get("/read/{collection}/{id}/{subcollection}")
async def read_sub_collection(collection: str, id: str, subcollection: str):
    return get_sub_collection(collection, id, subcollection)

# Delete (delete the document itself, not the info, so only need the document parameter):
@app.get("/delete/{collection}/{id}")
async def delete_info(collection: str, id: str):
    del_redis = delete_redis_data(collection, id)
    print(del_redis)
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