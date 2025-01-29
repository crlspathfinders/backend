from .model import (
    db,
    get_el_id,
    get_doc,
    storage,
    get_collection_id,
    get_collection_python,
)


def update_all_info_collection(doc, vals):  # vals is a dict
    try:
        all_all_info = get_collection_python("AllInfo")
        all_info_keys = []
        target = None
        for a in all_all_info:
            if a["id"] == doc:
                # print(a)
                curr_keys = list(a.keys())
                # print(curr_keys)
                curr_keys.pop()
                all_info_keys = curr_keys
                # print(all_info_keys)
                target = a
                # print(target)
        try:
            # print(f"old: {target[all_info_keys[0]]}")
            # print(f"new: {vals}")
            # print(f"changed key: {find_changed_key(target[all_info_keys[0]], vals)}")
            changed_key = find_changed_key(target[all_info_keys[0]], vals)
            changed_key_loc = list(vals.keys()).index(changed_key)
        except Exception as e:
            # print(f"not a dict: {e}")
            changed_key_loc = 0
        if target is not None:
            for t in target:
                print(t)
                if t in list(vals.keys()):  # vals.keys() will only ever have one key
                    # print(f"keys: {list(vals.keys())}") # keys
                    # # print(vals[list(vals.keys())[0]]) # new info
                    # print(vals[list(vals.keys())[changed_key_loc]])
                    # print(all_all_info[all_all_info.index(target)]) # correct location inside all info
                    # print(f"at location {list(vals.keys())[changed_key_loc]}") # necessary key to change
                    # print(type(all_all_info[all_all_info.index(target)]))
                    try:
                        all_all_info[all_all_info.index(target)][all_info_keys[0]][list(vals.keys())[changed_key_loc]] = (
                            vals[list(vals.keys())[changed_key_loc]]
                        )
                        print("works")
                    except Exception as e:
                        print(f"doesn't work: {e}")
                        all_all_info[all_all_info.index(target)][list(vals.keys())[0]] = (
                            vals[list(vals.keys())[0]]
                        )
                        # print("now works")
                    final = all_all_info[all_all_info.index(target)]
                    print(f"final: {final}")
                    for k in all_info_keys:
                        db.collection("AllInfo").document(doc).update({k: final[k]})
            return {"status": 0}
        return {"status": -13, "error_message": "No target found"}
    except Exception as e:
        return {"status": -1, "error_message": e}
    
def find_changed_key(old_dict, new_dict):
    changed_keys = []

    for key, old_value in old_dict.items():
        # Check if the key exists in the new dictionary and its value has changed
        if key in new_dict and new_dict[key] != old_value:
            # changed_keys.append(key)
            return key
    
    return changed_keys

def add_document_to_all_info_collection(doc):
    try:
        print(doc)
        first_part = db.collection("AllInfo").document(doc["id"])
        del doc["id"]
        first_part.set(doc)
        return {"status": 0}
    except Exception as e:
        print(e)
        return {"status": -1, "error_message": e}
