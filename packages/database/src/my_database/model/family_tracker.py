from my_database.db import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import UniqueConstraint
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from my_database.model.member import Members
from my_database.model.family_units import FamilyUnits


class FamilyTracker(Base):
    __tablename__ = "FAMILY_TRACKER"

    family_tracker_id = Column("family_tracker_id", Integer, primary_key=True, index=True)
    family_id = Column(
        "family_id", Integer, ForeignKey("FAMILY_UNITS.family_unit_id"), nullable=False
    )
    member_id = Column("member_id", Integer, ForeignKey("MEMBERS.member_id"), nullable=False)
    # 2. यहाँ __table_args__ जोड़ें
    __table_args__ = (UniqueConstraint("family_id", "member_id", name="_family_member_uc"),)
    member = relationship(Members, foreign_keys=[member_id])
    family = relationship(FamilyUnits, foreign_keys=[family_id])
