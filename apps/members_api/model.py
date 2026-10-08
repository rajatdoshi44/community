from shared_core.utility.api_response import (
    SUCCESS_RESPONSE,
    ERROR_RESPONSE,
)
from my_database.model.member import Members
from shared_core.llm.main import llm_model
from apps.members_api.type import MemberType


def fetch_members_list(db):
    try:
        members = db.query(Members).all()
        return SUCCESS_RESPONSE(members, "Members fetched successfully", 200)
    except Exception as e:
        print(f"Error fetching members: {e}")
        return ERROR_RESPONSE(str(e), "Error fetching members", 500)


def create_member_model(db, member_data):
    try:
        new_member = Members(**member_data.dict())
        db.add(new_member)
        db.commit()
        db.refresh(new_member)
        print(f"New member created: {new_member}")
        return SUCCESS_RESPONSE(new_member, "Member created successfully", 201)
    except Exception as e:
        return ERROR_RESPONSE(str(e), "Error creating member", 500)


def update_member_model(db, member_data):
    try:
        member = db.query(Members).filter(Members.member_id == member_data.member_id).first()
        if not member:
            return ERROR_RESPONSE("Member not found", "Error updating member", 404)

        for key, value in member_data.dict(exclude_unset=True).items():
            setattr(member, key, value)

        db.commit()
        db.refresh(member)
        return SUCCESS_RESPONSE(member, "Member updated successfully", 200)
    except Exception as e:
        print(f"Error updating member: {e}")
        return ERROR_RESPONSE(str(e), "Error updating member", 500)


def fetch_member_by_id_model(db, member_id):
    try:
        member = db.query(Members).filter(Members.member_id == member_id).first()
        if not member:
            return ERROR_RESPONSE("Member not found", "Error fetching member", 404)
        return SUCCESS_RESPONSE(member, "Member fetched successfully", 200)
    except Exception as e:
        print(f"Error fetching member: {e}")
        return ERROR_RESPONSE(str(e), "Error fetching member", 500)


def llm_create_model(user_prompt: str, db):
    try:
        prompt = f"Extract the member details carefully from this text and when you return schema, please do not add member_id: {user_prompt}"
        response = llm_model(
            prompt,
            model="gemini-3.5-flash-lite",
            temperature=0.0,
            config={
                "response_mime_type": "application/json",
                "response_schema": MemberType,
                "temperature": 0.0,
            },
        )
        return create_member_model(db, response.parsed)
    except Exception as e:
        print(f"Error creating LLM: {e}")
        return ERROR_RESPONSE(str(e), "Error creating LLM", 500)
