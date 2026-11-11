import asyncio
from io import BytesIO
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import UploadFile
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from apps.members_api.model import llm_create_member_model, llm_search_members_model
from apps.members_api.type import LLMSearchConditional, MemberType, QueryBuilder
from my_database.db import Base
from my_database.model.member import Members


class MembersApiTypeTests(unittest.TestCase):
    def test_query_builder_parses_filter_conditions(self):
        query = QueryBuilder.model_validate(
            {
                "logical_operator": "AND",
                "conditions": [
                    {
                        "field": "first_name",
                        "operator": "eq",
                        "value": "Asha",
                    }
                ],
            }
        )

        self.assertIsInstance(query.conditions[0], LLMSearchConditional)
        self.assertEqual(query.conditions[0].value, "Asha")


class LLMMemberSearchTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.db.add_all(
            [
                Members(first_name="Asha", last_name="Rao", mobile_number="1001"),
                Members(first_name="Asha", last_name="Shah", mobile_number="1002"),
                Members(first_name="Ravi", last_name="Rao", mobile_number="1003"),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def search(self, logical_operator, conditions):
        query = QueryBuilder.model_validate(
            {"logical_operator": logical_operator, "conditions": conditions}
        )
        with patch(
            "apps.members_api.model.llm_model",
            return_value=SimpleNamespace(parsed=query),
        ):
            return llm_search_members_model("find a member", self.db)

    def test_and_conditions_filter_all_fields(self):
        result = self.search(
            "AND",
            [
                {"field": "first_name", "operator": "eq", "value": "Asha"},
                {"field": "last_name", "operator": "eq", "value": "Rao"},
            ],
        )

        self.assertTrue(result["success"])
        self.assertEqual([member.mobile_number for member in result["data"]], ["1001"])

    def test_or_conditions_match_either_condition(self):
        result = self.search(
            "OR",
            [
                {"field": "first_name", "operator": "eq", "value": "Asha"},
                {"field": "last_name", "operator": "eq", "value": "Rao"},
            ],
        )

        self.assertTrue(result["success"])
        self.assertEqual(
            {member.mobile_number for member in result["data"]},
            {"1001", "1002", "1003"},
        )

    def test_like_condition_matches_case_insensitive_substring(self):
        result = self.search(
            "AND",
            [{"field": "first_name", "operator": "like", "value": "AS"}],
        )

        self.assertEqual(
            {member.mobile_number for member in result["data"]},
            {"1001", "1002"},
        )

    def test_comparison_conditions_filter_string_fields(self):
        greater_result = self.search(
            "AND",
            [{"field": "first_name", "operator": "gt", "value": "Asha"}],
        )
        less_result = self.search(
            "AND",
            [{"field": "first_name", "operator": "lt", "value": "Ravi"}],
        )

        self.assertEqual(
            {member.mobile_number for member in greater_result["data"]},
            {"1003"},
        )
        self.assertEqual(
            {member.mobile_number for member in less_result["data"]},
            {"1001", "1002"},
        )

    def test_empty_conditions_return_validation_error(self):
        result = self.search("AND", [])

        self.assertFalse(result.success)
        self.assertEqual(result.status, 422)

    def test_create_members_from_image_persists_parsed_list(self):
        image_data = BytesIO()
        Image.new("RGB", (1, 1)).save(image_data, format="PNG")
        upload = UploadFile(
            filename="members.png",
            file=BytesIO(image_data.getvalue()),
        )
        parsed_members = [
            MemberType(
                first_name="Asha",
                last_name="Rao",
                mobile_number="1004",
                gender=False,
                is_active=True,
            )
        ]

        with patch(
            "apps.members_api.model.llm_model",
            return_value=SimpleNamespace(parsed=parsed_members),
        ):
            result = asyncio.run(llm_create_member_model(upload, self.db))

        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0].member_id, 4)
        self.assertEqual(
            self.db.query(Members).filter_by(mobile_number="1004").count(),
            1,
        )


if __name__ == "__main__":
    unittest.main()
