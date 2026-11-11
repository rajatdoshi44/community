from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from my_database.db import get_db
from apps.family_tracker_api.model import (
    create_family_tracker_model,
    delete_family_tracker_model,
    fetch_family_tracker_by_id_model,
    fetch_family_trackers_list,
    update_family_tracker_model,
    get_family_detail_model,
)
from apps.family_tracker_api.type import (
    FamilyTrackerType,
    GetFamilyDetailRequest,
    GetFamilyDetailResponse,
)
from shared_core.utility.api_response import TYPE_ERROR_RESPONSE, TYPE_SUCCESS_RESPONSE

router = APIRouter(
    prefix="/family-tracker",
    tags=["family-tracker"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/list",
    response_model=TYPE_SUCCESS_RESPONSE[list[FamilyTrackerType]] | TYPE_ERROR_RESPONSE[str],
)
async def read_family_trackers(db: Session = Depends(get_db)):
    return fetch_family_trackers_list(db)


@router.post(
    "/create",
    response_model=TYPE_SUCCESS_RESPONSE[FamilyTrackerType] | TYPE_ERROR_RESPONSE[str],
)
async def create_family_tracker(family_tracker: FamilyTrackerType, db: Session = Depends(get_db)):
    return create_family_tracker_model(db, family_tracker)


@router.post(
    "/update",
    response_model=TYPE_SUCCESS_RESPONSE[FamilyTrackerType] | TYPE_ERROR_RESPONSE[str],
)
def update_family_tracker(family_tracker: FamilyTrackerType, db: Session = Depends(get_db)):
    return update_family_tracker_model(db, family_tracker)


@router.get("/health")
async def health_check():
    return {"status": "Family Tracker API is healthy"}


@router.get(
    "/{id}",
    response_model=TYPE_SUCCESS_RESPONSE[FamilyTrackerType] | TYPE_ERROR_RESPONSE[str],
)
async def read_family_tracker(id: int, db: Session = Depends(get_db)):
    return fetch_family_tracker_by_id_model(db, id)


@router.post("/detail", response_model=list[GetFamilyDetailResponse])
async def get_family_detail(family: GetFamilyDetailRequest, db: Session = Depends(get_db)):
    return get_family_detail_model(family, db)


@router.delete(
    "/{id}",
    response_model=TYPE_SUCCESS_RESPONSE[FamilyTrackerType] | TYPE_ERROR_RESPONSE[str],
)
def delete_family_tracker(id: int, db: Session = Depends(get_db)):
    return delete_family_tracker_model(db, id)
