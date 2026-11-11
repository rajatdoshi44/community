from typing import List, Literal

from pydantic import BaseModel, Field


class MemberType(BaseModel):
    member_id: int | None = None
    first_name: str
    last_name: str
    mobile_number: str
    gender: bool
    is_active: bool


class MemberSearch(MemberType):
    first_name: str


# LLM Search Prompt Model
class LLMSearchConditional(BaseModel):
    field: Literal["first_name", "last_name", "mobile_number"] = Field(
        description="Use 'first_name' for person's name, 'last_name' for their last name, 'mobile_number' for their phone number"
    )
    operator: Literal["eq", "like", "gt", "lt"] = Field(description="Operator to use")
    value: str = Field(description="Value to search for")


class QueryBuilder(BaseModel):
    logical_operator: Literal["AND", "OR"] = Field(
        description="Logical operator to join multiple conditions. Use 'AND' if both must be true, 'OR' if either can be true."
    )
    conditions: List[LLMSearchConditional] = Field(
        description="List of filter conditions"
    )
