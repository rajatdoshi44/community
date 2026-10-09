from fastapi import APIRouter, Depends
from my_database.db import get_db
from sqlalchemy.orm import Session
from apps.family_unit_api.model import (
    create_family_unit_model,
    fetch_family_unit_by_id_model,
    fetch_family_units_list,
    llm_create_family_unit_model,
    update_family_unit_model,
)
from apps.family_unit_api.type import FamilyUnitType
from shared_core.utility.api_response import (
    TYPE_SUCCESS_RESPONSE,
    TYPE_ERROR_RESPONSE,
)

router = APIRouter(
    prefix="/family-units",
    tags=["family-units"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/list",
    response_model=TYPE_SUCCESS_RESPONSE[list[FamilyUnitType]] | TYPE_ERROR_RESPONSE[str],
)
async def read_family_units(db: Session = Depends(get_db)):
    return fetch_family_units_list(db)


@router.post(
    "/create",
    response_model=TYPE_SUCCESS_RESPONSE[FamilyUnitType] | TYPE_ERROR_RESPONSE[str],
)
async def create_family_unit(family_unit: FamilyUnitType, db: Session = Depends(get_db)):
    return create_family_unit_model(db, family_unit)


@router.post(
    "/update",
    response_model=TYPE_SUCCESS_RESPONSE[FamilyUnitType] | TYPE_ERROR_RESPONSE[str],
)
def update_family_unit(family_unit: FamilyUnitType, db: Session = Depends(get_db)):
    return update_family_unit_model(db, family_unit)


@router.get(
    "/{id}",
    response_model=TYPE_SUCCESS_RESPONSE[FamilyUnitType] | TYPE_ERROR_RESPONSE[str],
)
async def read_family_unit(id: int, db: Session = Depends(get_db)):
    return fetch_family_unit_by_id_model(db, id)


@router.post(
    "/llm-create",
    response_model=TYPE_SUCCESS_RESPONSE[FamilyUnitType] | TYPE_ERROR_RESPONSE[str],
)
async def llm_create_family_unit(user_prompt: str, db: Session = Depends(get_db)):
    return llm_create_family_unit_model(user_prompt, db)


@router.get("/health")
async def health_check():
    return {"status": "Family Unit API is healthy"}
