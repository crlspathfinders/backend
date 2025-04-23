from .model import (
    db,
    get_collection_python,
)

def make_alumni(alumni):
    # alumni is a dict (so the schema can be changed at any time)
    try:
        _, second = db.collection("AlumniNetwork").add(alumni)
        # print(second)
        new_doc_id = second.id
        # print(new_doc_id)
        return {"status": 0, "id": new_doc_id}
    except Exception as e:
        return {"status": -1, "error_message": e}