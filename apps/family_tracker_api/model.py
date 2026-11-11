from my_database.model.family_tracker import FamilyTracker
from shared_core.utility.api_response import ERROR_RESPONSE, SUCCESS_RESPONSE
from my_database.model.member import Members
from my_database.model.family_units import FamilyUnits


def fetch_family_trackers_list(db):
    try:
        family_trackers = db.query(FamilyTracker).all()
        return SUCCESS_RESPONSE(family_trackers, "Family tracker records fetched successfully", 200)
    except Exception as e:
        return ERROR_RESPONSE(str(e), "Error fetching family tracker records", 500)


def create_family_tracker_model(db, family_tracker_data):
    try:
        new_family_tracker = FamilyTracker(**family_tracker_data.model_dump(exclude_unset=True))
        db.add(new_family_tracker)
        db.commit()
        db.refresh(new_family_tracker)
        return SUCCESS_RESPONSE(
            new_family_tracker, "Family tracker record created successfully", 201
        )
    except Exception as e:
        db.rollback()
        return ERROR_RESPONSE(str(e), "Error creating family tracker record", 500)


def update_family_tracker_model(db, family_tracker_data):
    try:
        family_tracker = (
            db.query(FamilyTracker)
            .filter(FamilyTracker.family_tracker_id == family_tracker_data.family_tracker_id)
            .first()
        )
        if not family_tracker:
            return ERROR_RESPONSE(
                "Family tracker record not found", "Error updating family tracker record", 404
            )

        for key, value in family_tracker_data.model_dump(exclude_unset=True).items():
            setattr(family_tracker, key, value)

        db.commit()
        db.refresh(family_tracker)
        return SUCCESS_RESPONSE(family_tracker, "Family tracker record updated successfully", 200)
    except Exception as e:
        db.rollback()
        return ERROR_RESPONSE(str(e), "Error updating family tracker record", 500)


def fetch_family_tracker_by_id_model(db, family_tracker_id):
    try:
        family_tracker = (
            db.query(FamilyTracker)
            .filter(FamilyTracker.family_tracker_id == family_tracker_id)
            .first()
        )
        if not family_tracker:
            return ERROR_RESPONSE(
                "Family tracker record not found", "Error fetching family tracker record", 404
            )
        return SUCCESS_RESPONSE(family_tracker, "Family tracker record fetched successfully", 200)
    except Exception as e:
        return ERROR_RESPONSE(str(e), "Error fetching family tracker record", 500)


def delete_family_tracker_model(db, family_tracker_id):
    try:
        family_tracker = (
            db.query(FamilyTracker)
            .filter(FamilyTracker.family_tracker_id == family_tracker_id)
            .first()
        )
        if not family_tracker:
            return ERROR_RESPONSE(
                "Family tracker record not found", "Error deleting family tracker record", 404
            )

        db.delete(family_tracker)
        db.commit()
        return SUCCESS_RESPONSE(family_tracker, "Family tracker record deleted successfully", 200)
    except Exception as e:
        db.rollback()
        return ERROR_RESPONSE(str(e), "Error deleting family tracker record", 500)


def get_family_detail_model(family, db):
    try:
        family = (
            db.query(
                FamilyTracker.family_tracker_id,
                FamilyTracker.member_id,
                FamilyTracker.family_id,
                FamilyUnits.family_name,
                Members.first_name,
                Members.last_name,
            )
            .join(FamilyUnits, FamilyTracker.family_id == FamilyUnits.family_unit_id)
            .join(Members, Members.member_id == FamilyTracker.member_id)
            .filter(FamilyTracker.family_id == family.family_id)
            .all()
        )
        print(family)
        return family
    except Exception as e:
        return str(e)
