import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from apps.family_tracker_api.main import app
from my_database.db import Base, get_db
from my_database.model.family_units import FamilyUnits
from my_database.model.member import Members


class FamilyTrackerApiTests(unittest.TestCase):
    def test_crud_routes_registered(self):
        paths = app.openapi().get("paths", {})
        self.assertIn("/family-tracker/list", paths)
        self.assertIn("/family-tracker/create", paths)
        self.assertIn("/family-tracker/update", paths)
        self.assertIn("/family-tracker/{id}", paths)
        self.assertIn("/family-tracker/health", paths)
        self.assertIn("delete", paths["/family-tracker/{id}"])

    def test_crud_operations(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            db.add_all(
                [
                    FamilyUnits(family_unit_id=1, family_name="First family"),
                    FamilyUnits(family_unit_id=2, family_name="Second family"),
                    Members(
                        member_id=1,
                        first_name="Test",
                        last_name="Member",
                        mobile_number="555-0100",
                        gender=False,
                        is_active=True,
                    ),
                ]
            )
            db.commit()

        def override_get_db():
            with Session(engine) as db:
                yield db

        app.dependency_overrides[get_db] = override_get_db
        self.addCleanup(app.dependency_overrides.clear)
        self.addCleanup(engine.dispose)

        with TestClient(app) as client:
            created = client.post(
                "/family-tracker/create",
                json={"family_id": 1, "member_id": 1},
            )
            self.assertEqual(created.status_code, 200)
            self.assertTrue(created.json()["success"])
            tracker_id = created.json()["data"]["family_tracker_id"]

            listed = client.get("/family-tracker/list")
            self.assertEqual(len(listed.json()["data"]), 1)

            fetched = client.get(f"/family-tracker/{tracker_id}")
            self.assertEqual(fetched.json()["data"]["family_id"], 1)

            updated = client.post(
                "/family-tracker/update",
                json={
                    "family_tracker_id": tracker_id,
                    "family_id": 2,
                    "member_id": 1,
                },
            )
            self.assertEqual(updated.json()["data"]["family_id"], 2)

            deleted = client.delete(f"/family-tracker/{tracker_id}")
            self.assertTrue(deleted.json()["success"])

            missing = client.get(f"/family-tracker/{tracker_id}")
            self.assertFalse(missing.json()["success"])

        Base.metadata.drop_all(engine)


if __name__ == "__main__":
    unittest.main()
