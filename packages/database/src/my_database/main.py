from sqlalchemy import engine

from my_database.model.member import Members
from my_database.model.parent_child import ParentChild
from my_database.model.family_units import FamilyUnits
from my_database.model.split_family import SplitFamily
from my_database.model.family_tracker import FamilyTracker
from my_database.db import Base, engine


def test():
    print("Testing database connection...")


def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    test()
    setup_database()
