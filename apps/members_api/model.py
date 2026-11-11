import io
from PIL import Image
import json

from sqlalchemy import and_, or_

from shared_core.utility.api_response import (
    SUCCESS_RESPONSE,
    ERROR_RESPONSE,
)
from my_database.model.member import Members
from shared_core.llm.main import llm_model
from apps.members_api.type import MemberType, QueryBuilder


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


def fetch_member_by_mobile_number_model(db, mobile_number):
    try:
        member = db.query(Members).filter(Members.mobile_number == mobile_number).first()
        if not member:
            return ERROR_RESPONSE("Member not found", "Error fetching member", 404)
        return SUCCESS_RESPONSE(member, "Member fetched successfully", 200)
    except Exception as e:
        print(f"Error fetching member: {e}")
        return ERROR_RESPONSE(str(e), "Error fetching member", 500)


def fetch_member_by_member_name_model(db, member):
    try:
        members = db.query(Members).filter(Members.first_name.icontains(member.first_name)).all()
        return SUCCESS_RESPONSE(members, "Members fetched successfully", 200)
    except Exception as e:
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


def llm_search_members_model(user_prompt: str, db):
    try:
        prompt = (
            "Convert the member search request into filters. Return only the requested "
            f"search criteria and do not add member_id: {user_prompt}"
        )
        response = llm_model(
            prompt,
            model="gemini-3.5-flash-lite",
            temperature=0.0,
            config={
                "response_mime_type": "application/json",
                "response_schema": QueryBuilder,
                "temperature": 0.0,
            },
        )
        query_builder = QueryBuilder.model_validate(response.parsed)
        if not query_builder.conditions:
            return ERROR_RESPONSE(
                "At least one search condition is required",
                "Unable to search members",
                422,
            )

        filters = []
        for condition in query_builder.conditions:
            column = getattr(Members, condition.field)
            if condition.operator == "eq":
                filters.append(column == condition.value)
            elif condition.operator == "like":
                filters.append(column.ilike(f"%{condition.value}%"))
            elif condition.operator == "gt":
                filters.append(column > condition.value)
            elif condition.operator == "lt":
                filters.append(column < condition.value)

        query = db.query(Members)
        if query_builder.logical_operator == "AND":
            query = query.filter(and_(*filters))
        else:
            query = query.filter(or_(*filters))

        members = query.all()
        return SUCCESS_RESPONSE(members, "Members fetched successfully", 200)
    except Exception as e:
        print(f"Error searching members with LLM: {e}")
        return ERROR_RESPONSE(str(e), "Error searching members with LLM", 500)


async def llm_create_member_model(image, db):
    try:
        print(f"Received image: {image.filename}, content type: {image.content_type}")
        prompt = (
            "Extract the member details carefully from this image and when you return "
            "schema, please do not add member_id"
        )
        image_bytes = await image.read()
        img = Image.open(io.BytesIO(image_bytes))
        response = llm_model(
            [prompt, img],
            model="gemini-3.5-flash-lite",
            temperature=0.0,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[MemberType],
                "temperature": 0.0,
            },
        )
        members = [MemberType.model_validate(member) for member in response.parsed]
        new_members = [Members(**member.model_dump(exclude={"member_id"})) for member in members]
        db.add_all(new_members)
        db.commit()
        for member in new_members:
            db.refresh(member)
        return SUCCESS_RESPONSE(new_members, "Members created successfully", 201)
    except Exception as e:
        db.rollback()
        print(f"Error creating members from image: {e}")
        return ERROR_RESPONSE(str(e), "Error creating members from image", 500)
