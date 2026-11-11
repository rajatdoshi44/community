from fastapi import APIRouter, Depends
from my_database.db import get_db
from sqlalchemy.orm import Session
from apps.parent_child_api.model import (
    create_parent_child_model,
    fetch_parent_child_by_id_model,
    fetch_parent_children_list,
    update_parent_child_model,
    get_member_family_tree_model,
)
from apps.parent_child_api.type import (
    ParentChildType,
    GetFamilyMemberTreeRequestType,
    GetFamilyMemberTreeResponseType,
)
from shared_core.utility.api_response import (
    TYPE_SUCCESS_RESPONSE,
    TYPE_ERROR_RESPONSE,
)

router = APIRouter(
    prefix="/parent-child",
    tags=["parent-child"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/list",
    response_model=TYPE_SUCCESS_RESPONSE[list[ParentChildType]] | TYPE_ERROR_RESPONSE[str],
)
async def read_parent_children(db: Session = Depends(get_db)):
    return fetch_parent_children_list(db)


@router.post(
    "/create",
    response_model=TYPE_SUCCESS_RESPONSE[ParentChildType] | TYPE_ERROR_RESPONSE[str],
)
async def create_parent_child(parent_child: ParentChildType, db: Session = Depends(get_db)):
    return create_parent_child_model(db, parent_child)


@router.post(
    "/update",
    response_model=TYPE_SUCCESS_RESPONSE[ParentChildType] | TYPE_ERROR_RESPONSE[str],
)
def update_parent_child(parent_child: ParentChildType, db: Session = Depends(get_db)):
    return update_parent_child_model(db, parent_child)


@router.get(
    "/{id}",
    response_model=TYPE_SUCCESS_RESPONSE[ParentChildType] | TYPE_ERROR_RESPONSE[str],
)
async def read_parent_child(id: int, db: Session = Depends(get_db)):
    return fetch_parent_child_by_id_model(db, id)


@router.post("/get-member-family-tree", response_model=GetFamilyMemberTreeResponseType)
def get_member_family_tree(member: GetFamilyMemberTreeRequestType, db: Session = Depends(get_db)):
    return get_member_family_tree_model(member, db)


@router.get("/health")
async def health_check():
    return {"status": "Parent-child API is healthy"}
