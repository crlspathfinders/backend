from fastapi import APIRouter, Form, FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from models.allinfomodel import update_all_info_collection, add_document_to_all_info_collection
from models.redismodel import add_redis_collection

router = APIRouter(
    tags=["allinfo"]
)

class UpdateAllInfo(BaseModel):
    doc: str
    vals: dict

@router.post("/update/")
def update_all_info(update: UpdateAllInfo):
    result = update_all_info_collection(update.doc, update.vals)
    add_redis_collection("AllInfo")
    if result["status"] == 0:
        return {"status": 0}
    print(result)
    return {"status": -1, "error_message": result["error_message"]}

class AddDocument(BaseModel):
    doc: dict

@router.post("/adddocument/")
def add_document(doc: AddDocument):
    result = add_document_to_all_info_collection(doc.doc)
    if result["status"] == 0: 
        add_redis_collection("AllInfo")
        return {"status": 0}
    return {"status": -1, "error_message": result["error_message"]}