"""SQLite database setup and connection management."""
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path="employee_records.db"):
        self.db_path = Path(db_path)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.initialize()

    def initialize(self):
        with self.connection:
            self.connection.executescript("""
                CREATE TABLE IF NOT EXISTS departments (
                    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS employees (
                    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL,
                    department_id INTEGER,
                    designation TEXT NOT NULL,
                    salary REAL NOT NULL CHECK(salary >= 0),
                    joining_date TEXT NOT NULL,
                    FOREIGN KEY (department_id) REFERENCES departments(department_id)
                        ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS attendance (
                    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    attendance_date TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('Present', 'Absent', 'Leave')),
                    UNIQUE(employee_id, attendance_date),
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS payroll (
                    payroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    pay_month TEXT NOT NULL,
                    basic_salary REAL NOT NULL CHECK(basic_salary >= 0),
                    bonus REAL NOT NULL DEFAULT 0 CHECK(bonus >= 0),
                    deductions REAL NOT NULL DEFAULT 0 CHECK(deductions >= 0),
                    net_salary REAL NOT NULL CHECK(net_salary >= 0),
                    UNIQUE(employee_id, pay_month),
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                        ON DELETE CASCADE
                );
            """)
            self.connection.execute(
                "INSERT OR IGNORE INTO departments(name) VALUES (?)", ("General",)
            )

    def execute(self, query, params=()):
        return self.connection.execute(query, params)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()
