from pydantic import BaseModel, ConfigDict


class SplitFamilyType(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    parent_family_id: int
    family_id: int
    parent_id: int
    child_id: int
