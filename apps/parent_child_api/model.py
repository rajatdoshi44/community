from my_database.model.parent_child import ParentChild
from my_database.model.member import Members
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
from fastapi.encoders import jsonable_encoder

from shared_core.utility.api_response import (
    SUCCESS_RESPONSE,
    ERROR_RESPONSE,
)

Father = aliased(Members)
Child = aliased(Members)


def fetch_parent_children_list(db):
    try:
        parent_children = db.query(ParentChild).all()
        return SUCCESS_RESPONSE(parent_children, "Parent-child records fetched successfully", 200)
    except Exception as e:
        print(f"Error fetching parent-child records: {e}")
        return ERROR_RESPONSE(str(e), "Error fetching parent-child records", 500)


def create_parent_child_model(db, parent_child_data):
    try:
        new_parent_child = ParentChild(**parent_child_data.dict())
        db.add(new_parent_child)
        db.commit()
        db.refresh(new_parent_child)
        return SUCCESS_RESPONSE(new_parent_child, "Parent-child record created successfully", 201)
    except Exception as e:
        return ERROR_RESPONSE(str(e), "Error creating parent-child record", 500)


def update_parent_child_model(db, parent_child_data):
    try:
        parent_child = (
            db.query(ParentChild)
            .filter(ParentChild.parent_child_id == parent_child_data.parent_child_id)
            .first()
        )
        if not parent_child:
            return ERROR_RESPONSE(
                "Parent-child record not found", "Error updating parent-child record", 404
            )

        for key, value in parent_child_data.dict(exclude_unset=True).items():
            setattr(parent_child, key, value)

        db.commit()
        db.refresh(parent_child)
        return SUCCESS_RESPONSE(parent_child, "Parent-child record updated successfully", 200)
    except Exception as e:
        print(f"Error updating parent-child record: {e}")
        return ERROR_RESPONSE(str(e), "Error updating parent-child record", 500)


def fetch_parent_child_by_id_model(db, parent_child_id):
    try:
        parent_child = (
            db.query(ParentChild).filter(ParentChild.parent_child_id == parent_child_id).first()
        )
        if not parent_child:
            return ERROR_RESPONSE(
                "Parent-child record not found", "Error fetching parent-child record", 404
            )
        return SUCCESS_RESPONSE(parent_child, "Parent-child record fetched successfully", 200)
    except Exception as e:
        print(f"Error fetching parent-child record: {e}")
        return ERROR_RESPONSE(str(e), "Error fetching parent-child record", 500)


def get_member_family_tree_model(member, db):
    member_id = member.member_id if hasattr(member, "member_id") else member
    root_id = member_id
    ancestors = set()

    while root_id not in ancestors:
        ancestors.add(root_id)
        parent = (
            db.query(Father.member_id)
            .join(ParentChild, ParentChild.father_id == Father.member_id)
            .filter(ParentChild.child_id == root_id)
            .first()
        )
        if not parent:
            break
        root_id = parent.member_id

    def build_tree_node(current_id, path):
        current_member = db.query(Members).filter(Members.member_id == current_id).first()
        children = (
            db.query(Child)
            .join(ParentChild, ParentChild.child_id == Child.member_id)
            .filter(ParentChild.father_id == current_id)
            .all()
        )
        next_path = path | {current_id}
        return {
            "first_name": current_member.first_name,
            "mobile_number": current_member.mobile_number,
            "child_list": [
                build_tree_node(child.member_id, next_path)
                if child.member_id not in next_path
                else {
                    "first_name": child.first_name,
                    "mobile_number": child.mobile_number,
                    "child_list": [],
                }
                for child in children
            ],
        }

    return {"tree": build_tree_node(root_id, set())}


# def get_member_family_tree_model(member, db):
#     try:
#         member_to_parent = {}
#         member_to_child = []
#         member_tree = {}
#         response = {"parents": [], "self": {}, "child": []}
#         is_parent_available = parent_tracker(member.member_id, db, member_to_parent)
#         is_child_available = child_tracker(member.member_id, db, member_to_child, member_tree)

#         if is_parent_available:
#             response["parents"] = [member_to_parent]

#         if is_child_available:
#             response["child"] = member_to_child

#         print(f"result = {member_to_parent}")
#         return response
#     except Exception as E:
#         str(E)


# def get_member_family_tree_model(
#     target_member_id, db, visited_members=None, collected_records=None
# ):
#     # अगर ऑब्जेक्ट है तो ID निकालें, वर्ना सीधा इस्तेमाल करें
#     actual_id = (
#         target_member_id.member_id if hasattr(target_member_id, "member_id") else target_member_id
#     )

#     if visited_members is None:
#         visited_members = set()
#     if collected_records is None:
#         collected_records = {}

#     if actual_id in visited_members:
#         return collected_records

#     visited_members.add(actual_id)

#     # क्वेरी में joinedload का इस्तेमाल (ताकि Members टेबल जॉइन हो जाए)
#     records = (
#         db.query(ParentChild)
#         .options(
#             joinedload(ParentChild.father),
#             joinedload(ParentChild.mother),
#             joinedload(ParentChild.child),
#         )
#         .filter(
#             or_(
#                 ParentChild.child_id == actual_id,
#                 ParentChild.father_id == actual_id,
#                 ParentChild.mother_id == actual_id,
#             ),
#             ParentChild.is_active == True,
#         )
#         .all()
#     )

#     for record in records:
#         if record.parent_child_id not in collected_records:
#             # यहाँ हम सीधा ऑब्जेक्ट सेव करने की बजाय, एक साफ़ डिक्शनरी सेव कर रहे हैं
#             # नोट: first_name और last_name को अपने Members टेबल के कॉलम नाम से मैच कर लें
#             collected_records[record.parent_child_id] = {
#                 "parent_child_id": record.parent_child_id,
#                 "father_id": record.father_id,
#                 "father_first_name": record.father.first_name if record.father else None,
#                 "father_last_name": record.father.last_name if record.father else None,
#                 "mother_id": record.mother_id,
#                 "mother_first_name": record.mother.first_name if record.mother else None,
#                 "mother_last_name": record.mother.last_name if record.mother else None,
#                 "child_id": record.child_id,
#                 "child_first_name": record.child.first_name if record.child else None,
#                 "child_last_name": record.child.last_name if record.child else None,
#             }

#         # --- RECURSION ---
#         if record.father_id:
#             get_member_family_tree_model(record.father_id, db, visited_members, collected_records)

#         if record.mother_id:
#             get_member_family_tree_model(record.mother_id, db, visited_members, collected_records)

#         if record.child_id:
#             get_member_family_tree_model(record.child_id, db, visited_members, collected_records)

#     # लिस्ट में डिक्शनरी का डेटा रिटर्न कर देगा, FastAPI इसे बिना किसी एरर के JSON बना देगा
#     return list(collected_records.values())
