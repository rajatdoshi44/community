from click import prompt
from fastapi import APIRouter, Depends, File, UploadFile
from my_database import db
from my_database.db import get_db
from my_database.model import member
from sqlalchemy.orm import Session
from apps.members_api.model import (
    create_member_model,
    fetch_member_by_id_model,
    fetch_members_list,
    llm_search_members_model,
    update_member_model,
    llm_create_model,
    fetch_member_by_mobile_number_model,
    fetch_member_by_member_name_model,
    llm_create_member_model,
)
from apps.members_api.type import MemberType
from shared_core.utility.api_response import (
    TYPE_SUCCESS_RESPONSE,
    TYPE_ERROR_RESPONSE,
)

router = APIRouter(
    prefix="/members",
    tags=["members"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/list", response_model=TYPE_SUCCESS_RESPONSE[list[MemberType]] | TYPE_ERROR_RESPONSE[str]
)
async def read_members(db: Session = Depends(get_db)):
    return fetch_members_list(db)


@router.post("/create", response_model=TYPE_SUCCESS_RESPONSE[MemberType] | TYPE_ERROR_RESPONSE[str])
async def create_member(member: MemberType, db: Session = Depends(get_db)):
    return create_member_model(db, member)


@router.post("/update", response_model=TYPE_SUCCESS_RESPONSE[MemberType] | TYPE_ERROR_RESPONSE[str])
def update_member(member: MemberType, db: Session = Depends(get_db)):
    return update_member_model(db, member)


@router.get("/:id", response_model=TYPE_SUCCESS_RESPONSE[MemberType] | TYPE_ERROR_RESPONSE[str])
async def read_member(id: int, db: Session = Depends(get_db)):
    return fetch_member_by_id_model(db, id)


@router.get(
    "/:mobileNumber", response_model=TYPE_SUCCESS_RESPONSE[MemberType] | TYPE_ERROR_RESPONSE[str]
)
async def fetch_member_by_mobile_number(mobileNumber: int, db: Session = Depends(get_db)):
    return fetch_member_by_mobile_number_model(db, mobileNumber)


@router.post(
    "/llm/create", response_model=TYPE_SUCCESS_RESPONSE[MemberType] | TYPE_ERROR_RESPONSE[str]
)
async def llm_create(prompt: str, db: Session = Depends(get_db)):
    return llm_create_model(prompt, db)


@router.post(
    "/member-search",
    response_model=TYPE_SUCCESS_RESPONSE[list[MemberType]] | TYPE_ERROR_RESPONSE[str],
)
async def fetch_member_by_member_name(member: MemberType, db: Session = Depends(get_db)):
    return fetch_member_by_member_name_model(db=db, member=member)


@router.post(
    "/llm/member-search",
    response_model=TYPE_SUCCESS_RESPONSE[list[MemberType]] | TYPE_ERROR_RESPONSE[str],
)
async def llm_search_members(prompt: str, db: Session = Depends(get_db)):
    return llm_search_members_model(prompt, db)


@router.post(
    "/llm/create-member",
    response_model=TYPE_SUCCESS_RESPONSE[list[MemberType]] | TYPE_ERROR_RESPONSE[str],
)
async def llm_create_member(image: UploadFile = File(...), db: Session = Depends(get_db)):
    return await llm_create_member_model(image, db)


@router.get("/health")
async def health_check():
    return {"status": "Members API is healthy"}
