from .model import (
    db,
    get_el_id,
    get_collection_id,
    get_collection_python,
)


def create_link(link_name, link_url, categories, bio, deadline):
    collection = "Opportunities"
    try:
        db.collection(collection).add(
            {
                "name": link_name,
                "src": link_url,
                "categories": categories,
                "bio": bio,
                "deadline": deadline,
            }
        )
        return {"status": "Success"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}


def remove_link(name):
    doc_id = get_el_id("Opportunities", name)
    try:
        db.collection("Opportunities").document(doc_id).delete()
        return {"Status": "Successfully removed link"}
    except Exception as e:
        return {"status": f"Failed to remove link: {e}"}


def update_link(oldname, newname, newurl, categories, bio, deadline):
    collection = "Opportunities"
    try:
        doc_id = get_el_id(collection, oldname)
    except Exception as e:
        return {"status": "Failed to find doc_id"}
    try:
        db.collection(collection).document(doc_id).update(
            {
                "name": newname,
                "src": newurl,
                "categories": categories,
                "bio": bio,
                "deadline": deadline,
            }
        )
        return {"status": "Successfully updated link"}
    except Exception as e:
        return {"status": f"Failed: {str(e)}"}


def update_category(old_cat_name, new_cat_name):
    collection = "Demographics"
    doc_id = "Opportunities"
    all_cats = get_collection_id(collection, doc_id)["categories"]
    for i in all_cats:
        if i == old_cat_name:
            all_cats[all_cats.index(i)] = new_cat_name

    try:
        db.collection(collection).document(doc_id).update({"categories": all_cats})
        return {"status": "Successfully edited category"}
    except Exception as e:
        return {"status": f"Failed to edit category: {e}"}


def create_category(cat_name):
    collection = "Demographics"
    doc_id = "Opportunities"
    all_cats = get_collection_id(collection, doc_id)["categories"]
    all_cats.append(cat_name)
    try:
        db.collection(collection).document(doc_id).update({"categories": all_cats})
        return {"status": "Successfully created category"}
    except Exception as e:
        return {"status": f"Failed to create category: {e}"}


def delete_category(cat_name):
    collection = "Demographics"
    doc_id = "Opportunities"
    all_cats = get_collection_id(collection, doc_id)["categories"]
    all_cats.remove(cat_name)
    try:
        db.collection(collection).document(doc_id).update({"categories": all_cats})
        # successfully deleted category by here When deleting category, also have to remove this category from all
        # the opportunity links who have this category listed:
        opportunitiy = get_collection_python("Opportunities")
        for o in opportunitiy:
            if cat_name in o["categories"]:
                curr_cats = o["categories"]
                curr_cats.remove(cat_name)
                db.collection("Opportunities").document(o["id"]).update(
                    {"categories": curr_cats}
                )
        return {"status": "Successfully deleted category"}
    except Exception as e:
        return {"status": f"Failed to delete category: {e}"}
