from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from models.peermentormodel import create_link, remove_link, update_link, update_category, create_category, delete_category

router = APIRouter(
    tags=["peermentor"]
)

class Link(BaseModel):
    link_name: str
    link_url: str
    categories: List[str]
    bio: str
    deadline: str

@router.post("/addlink/")
async def add_link(link: Link):
    try:
        # TO-DO later: Make sure the name is unique.
        create_link(link.link_name, link.link_url, link.categories, link.bio, link.deadline)
        print(f"Successfully created pml link: {link.link_name}")
        return {"status": "Successfully created pml link"}
    except Exception as e:
        print(f"Failed to create pml link: {e}")
        return {"status": f"Failed to create pml link: {e}"}
    
@router.get("/deletelink/{link_name}")
async def delete_link(link_name):
    try:
        remove_link(link_name)
        return {"status": "Successfully deleted link"}
    except Exception as e:
        print(f"Failed to delete link: {e}")
        return {"status": f"Failed to delete link: {e}"}
    
class EditLink(BaseModel):
    old_name: str
    new_name: str
    new_url: str
    categories: List[str]
    bio: str
    deadline: str

@router.post("/editlink/")
async def edit_link(edit_link: EditLink):
    try:
        update_link(edit_link.old_name, edit_link.new_name, edit_link.new_url, edit_link.categories, edit_link.bio, edit_link.deadline)
        return {"status": "Successfully edited link"}
    except Exception as e:
        print(f"Failed to edit link: {e}")
        return {"status": f"Failed to edit link: {e}"}
    
class EditCategory(BaseModel):
    old_cat_name: str
    new_cat_name: str

@router.post("/editcategory/")
def edit_category(edit_cat: EditCategory):
    update_category(edit_cat.old_cat_name, edit_cat.new_cat_name)

class NewCategory(BaseModel):
    new_cat: str

@router.post("/addcategory")
def add_category(category: NewCategory):
    create_category(category.new_cat)

@router.post("/deletecategory")
def add_category(category: NewCategory):
    delete_category(category.new_cat)