# Employee Record Management System

A modular command-line administration utility built with **Python, SQLite, and Object-Oriented Programming (OOP)**. It manages employee records, department allocations, attendance, and payroll.

## Features

- **Employee CRUD:** Add, view, update, and delete employee records.
- **Department management:** Add departments and assign employees.
- **Attendance:** Record and view daily Present, Absent, or Leave status.
- **Payroll:** Generate monthly payroll with bonuses and deductions; view payroll records.
- **Input validation:** Validates required fields, email, phone, dates, numeric amounts, and duplicate records.
- **Relational database:** SQLite foreign keys link employee, attendance, department, and payroll records.
- **Modular design:** Database layer and application logic are separated into modules.

## Technology Stack

- Python 3.9+
- SQLite (`sqlite3`, included with Python)
- Object-Oriented Programming

## How to Run

1. Install Python 3.9 or later.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Run:

   ```bash
   python main.py
   ```

The application automatically creates `employee_records.db` and its tables on the first run.

## Project Structure

```text
Employee_Record_Management_System/
├── main.py
├── database.py
├── system.py
├── README.md
└── .gitignore
```

## Database Schema

- `departments`: department ID and unique department name.
- `employees`: employee profile, contact details, designation, salary, joining date, and department reference.
- `attendance`: employee attendance by date, with one entry per employee per date.
- `payroll`: monthly salary calculations, bonuses, deductions, and net salary, with one entry per employee per month.

## Example Workflow

1. Add a department (or use the default `General` department).
2. Add an employee and assign a department.
3. View or update the employee record.
4. Mark attendance for a date.
5. Generate payroll for a month by entering bonus and deductions.
6. View attendance and payroll reports.

## Notes

This is an educational project intended for local demonstration. It uses a console interface and a local SQLite database. Do not use real sensitive employee data in a public repository.
