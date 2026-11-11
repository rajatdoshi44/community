import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from apps.parent_child_api.main import app
from apps.parent_child_api.model import get_member_family_tree_model
from apps.parent_child_api.type import (
    GetFamilyMemberTreeRequestType,
    GetFamilyMemberTreeResponseType,
)
from my_database.db import Base
from my_database.model.member import Members
from my_database.model.parent_child import ParentChild


class ParentChildApiTests(unittest.TestCase):
    def test_routes_registered(self):
        paths = app.openapi().get("paths", {})
        self.assertIn("/parent-child/list", paths)
        self.assertIn("/parent-child/create", paths)
        self.assertIn("/parent-child/update", paths)
        self.assertIn("/parent-child/{id}", paths)
        self.assertIn("/parent-child/health", paths)

    def test_family_tree_returns_one_complete_tree(self):
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            db.add_all(
                [
                    Members(member_id=1, first_name="Grandparent", mobile_number="1001"),
                    Members(member_id=2, first_name="Parent", mobile_number="1002"),
                    Members(member_id=3, first_name="Child", mobile_number="1003"),
                    Members(member_id=4, first_name="Grandchild", mobile_number="1004"),
                    Members(member_id=5, first_name="Sibling", mobile_number="1005"),
                ]
            )
            db.add_all(
                [
                    ParentChild(father_id=1, mother_id=1, child_id=2),
                    ParentChild(father_id=2, mother_id=2, child_id=3),
                    ParentChild(father_id=3, mother_id=3, child_id=4),
                    ParentChild(father_id=3, mother_id=3, child_id=5),
                ]
            )
            db.commit()

            result = get_member_family_tree_model(
                GetFamilyMemberTreeRequestType(member_id=4), db
            )

        tree = GetFamilyMemberTreeResponseType.model_validate(result)
        self.assertEqual(tree.tree.first_name, "Grandparent")
        self.assertEqual(tree.tree.mobile_number, "1001")
        self.assertEqual(tree.tree.child_list[0].mobile_number, "1002")
        self.assertEqual(tree.tree.child_list[0].child_list[0].mobile_number, "1003")
        self.assertEqual(
            {
                child.first_name
                for child in tree.tree.child_list[0].child_list[0].child_list
            },
            {"Grandchild", "Sibling"},
        )
        self.assertEqual(
            {
                child.mobile_number
                for child in tree.tree.child_list[0].child_list[0].child_list
            },
            {"1004", "1005"},
        )
        self.assertEqual(
            result.keys(),
            {"tree"},
        )


if __name__ == "__main__":
    unittest.main()
