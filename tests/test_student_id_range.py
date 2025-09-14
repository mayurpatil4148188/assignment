# tests/test_student_id_range.py
from models.student import Student
from database import db


def test_first_and_last_student_id(app):
    with app.app_context():
        # Get first student id (smallest primary key)
        first_id = db.session.query(Student.id).order_by(Student.id.asc()).first()[0]

        # Get last student id (largest primary key)
        last_id = db.session.query(Student.id).order_by(Student.id.desc()).first()[0]

        print("First ID:", first_id)
        print("Last ID:", last_id)

        # Basic assertions to ensure IDs are valid integers
        assert isinstance(first_id, int)
        assert isinstance(last_id, int)
        assert first_id <= last_id
