"""
Employee Record Management System
Python | SQLite | OOP | CRUD Operations

Run: python main.py
"""
from database import Database
from system import EmployeeRecordManagementSystem


def main():
    db = Database()
    app = EmployeeRecordManagementSystem(db)
    try:
        app.run()
    finally:
        db.close()


if __name__ == "__main__":
    main()
