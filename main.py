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

# cached_mentors = CachedSession(
#     cache_name="cache/Mentors",
#     expire_after=10 # 10 s
# )

cached_mentors = CachedSession(
    backend='sqlite',
    cache_name="cache.sqlite",  # SQLite database file
    expire_after=10
)

@app.get("/cache/{collection}")
def cache_mentors(collection: str):
    print(f"{curr_url}read/{collection}")
    mentors = cached_mentors.get(f"{curr_url}read/{collection}")
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

# Redis testing:
from upstash_redis import Redis

redis = Redis(url="https://welcomed-kiwi-27133.upstash.io", token="AWn9AAIjcDExYTU0MzNlMmExOTg0ZTk0OGM0YmM3YThiNDllMDA0YnAxMA")

# Read a collection:
@app.get("/read/{collection}")
async def read_collection(collection: str):
    # docs = redis.hgetall(collection)

    # results = []
    # for key, value in docs.items():
    #     # Decode the key and value if they are bytes
    #     key_str = key.decode('utf-8') if isinstance(key, bytes) else key
    #     value_str = value.decode('utf-8') if isinstance(value, bytes) else value
        
    #     # If value_str is a valid JSON string, load it into a Python dictionary
    #     try:
    #         # Try to parse the value as JSON
    #         data = json.loads(value_str)
    #     except json.JSONDecodeError:
    #         # If not valid JSON, just keep it as a string
    #         data = value_str

    #     # Append the transformed dictionary to the results list
    #     data["id"] = key_str
    #     results.append(data)

    # # Sort the data list alphabetically by id
    # results.sort(key=lambda x: x["id"])

    # # Convert results to JSON string
    # json_results = json.dumps(results)

    # return json_results
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