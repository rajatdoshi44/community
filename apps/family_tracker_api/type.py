from pydantic import BaseModel, ConfigDict
from apps.family_unit_api.type import FamilyUnitType


class FamilyTrackerType(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    family_tracker_id: int | None = None
    family_id: int
    member_id: int


class GetFamilyDetailRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    family_id: int


class GetFamilyDetailResponse(BaseModel):
    family_tracker_id: int
    member_id: int
    family_id: int
    family_name: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


# class GetFamilyDetailResponse(BaseModel):
