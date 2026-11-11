from my_database.db import Base
from my_database.model.family_units import FamilyUnits as _FamilyUnits
from my_database.model.member import Members
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class SplitFamily(Base):
    __tablename__ = "split_family"

    id = Column("split_family_id", Integer, primary_key=True, index=True)
    parent_family_id = Column(
        "parent_family_id",
        Integer,
        ForeignKey(
            "FAMILY_UNITS.family_unit_id",
        ),
        nullable=False,
    )
    family_id = Column(
        "family_unit_id", Integer, ForeignKey("FAMILY_UNITS.family_unit_id"), nullable=False
    )
    parent_id = Column("parent_id", Integer, ForeignKey("MEMBERS.member_id"), nullable=False)
    child_id = Column("child_id", Integer, ForeignKey("MEMBERS.member_id"), nullable=False)

    parent = relationship(Members, foreign_keys=[parent_id])
    child = relationship(Members, foreign_keys=[child_id])
