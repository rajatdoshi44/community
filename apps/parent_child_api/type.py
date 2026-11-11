from pydantic import BaseModel


class ParentChildType(BaseModel):
    parent_child_id: int | None = None
    father_id: int
    mother_id: int
    child_id: int
    is_active: bool = True


class GetFamilyMemberTreeRequestType(BaseModel):
    member_id: int


class ParentType(BaseModel):
    father_name: str
    mother_name: str
    child_name: str


class PersonalDetailType(BaseModel):
    first_name: str
    mobile_number: str | None = None
    child_list: list[PersonalDetailType]


class GetFamilyMemberTreeResponseType(BaseModel):
    tree: PersonalDetailType
