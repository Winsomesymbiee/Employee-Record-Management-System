"""Business logic and command-line interface using OOP."""
from datetime import date, datetime
import sqlite3


class EmployeeRecordManagementSystem:
    def __init__(self, database):
        self.db = database

    @staticmethod
    def prompt_nonempty(label):
        while True:
            value = input(label).strip()
            if value:
                return value
            print("Input cannot be empty. Please try again.")

    @staticmethod
    def prompt_email():
        while True:
            email = input("Email: ").strip().lower()
            if "@" in email and "." in email.split("@")[-1] and " " not in email:
                return email
            print("Please enter a valid email address.")

    @staticmethod
    def prompt_phone():
        while True:
            phone = input("Phone (digits, optional +): ").strip()
            normalized = phone.replace("+", "", 1).replace("-", "").replace(" ", "")
            if normalized.isdigit() and 7 <= len(normalized) <= 15:
                return phone
            print("Enter a valid phone number (7–15 digits).")

    @staticmethod
    def prompt_number(label, minimum=0):
        while True:
            try:
                value = float(input(label).strip())
                if value >= minimum:
                    return value
                print(f"Value must be at least {minimum}.")
            except ValueError:
                print("Please enter a numeric value.")

    @staticmethod
    def prompt_date(label, fmt="%Y-%m-%d"):
        while True:
            value = input(label).strip()
            try:
                datetime.strptime(value, fmt)
                return value
            except ValueError:
                print(f"Use the format {fmt}.")

    def departments(self):
        rows = self.db.execute("SELECT * FROM departments ORDER BY name").fetchall()
        print("\nDepartments:")
        for row in rows:
            print(f"  {row['department_id']}. {row['name']}")
        return rows

    def add_department(self):
        name = self.prompt_nonempty("Department name: ").title()
        try:
            with self.db.connection:
                self.db.execute("INSERT INTO departments(name) VALUES (?)", (name,))
            print("Department added successfully.")
        except sqlite3.IntegrityError:
            print("That department already exists.")

    def add_employee(self):
        print("\n--- Add Employee ---")
        name = self.prompt_nonempty("Full name: ").title()
        email = self.prompt_email()
        phone = self.prompt_phone()
        self.departments()
        department = input("Department ID (blank for General): ").strip() or "1"
        designation = self.prompt_nonempty("Designation: ").title()
        salary = self.prompt_number("Monthly salary: ")
        joining_date = self.prompt_date("Joining date (YYYY-MM-DD): ")
        try:
            with self.db.connection:
                self.db.execute("""
                    INSERT INTO employees
                    (full_name, email, phone, department_id, designation, salary, joining_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, email, phone, int(department), designation, salary, joining_date))
            print("Employee added successfully.")
        except ValueError:
            print("Department ID must be a number.")
        except sqlite3.IntegrityError as exc:
            print(f"Could not add employee: {exc}")

    def list_employees(self):
        rows = self.db.execute("""
            SELECT e.*, d.name AS department
            FROM employees e LEFT JOIN departments d
            ON e.department_id = d.department_id
            ORDER BY e.employee_id
        """).fetchall()
        if not rows:
            print("\nNo employee records found.")
            return
        print("\n" + "-" * 112)
        print(f"{'ID':<5}{'Name':<23}{'Email':<28}{'Department':<18}{'Designation':<18}{'Salary':>10}")
        print("-" * 112)
        for row in rows:
            print(f"{row['employee_id']:<5}{row['full_name'][:22]:<23}"
                  f"{row['email'][:27]:<28}{(row['department'] or 'Unassigned')[:17]:<18}"
                  f"{row['designation'][:17]:<18}{row['salary']:>10.2f}")
        print("-" * 112)

    def find_employee(self, employee_id):
        return self.db.execute(
            "SELECT * FROM employees WHERE employee_id = ?", (employee_id,)
        ).fetchone()

    def update_employee(self):
        try:
            employee_id = int(input("Employee ID to update: ").strip())
        except ValueError:
            print("Employee ID must be a number.")
            return
        employee = self.find_employee(employee_id)
        if not employee:
            print("Employee not found.")
            return
        print("Press Enter to keep the existing value.")
        name = input(f"Full name [{employee['full_name']}]: ").strip() or employee["full_name"]
        email = input(f"Email [{employee['email']}]: ").strip().lower() or employee["email"]
        phone = input(f"Phone [{employee['phone']}]: ").strip() or employee["phone"]
        designation = input(f"Designation [{employee['designation']}]: ").strip() or employee["designation"]
        salary_text = input(f"Salary [{employee['salary']}]: ").strip()
        salary = employee["salary"] if not salary_text else self.parse_nonnegative(salary_text)
        if salary is None:
            print("Salary must be a non-negative number.")
            return
        department_text = input(f"Department ID [{employee['department_id']}]: ").strip()
        department_id = employee["department_id"] if not department_text else department_text
        joining_date = input(f"Joining date [{employee['joining_date']}]: ").strip() or employee["joining_date"]
        try:
            datetime.strptime(joining_date, "%Y-%m-%d")
            if "@" not in email or "." not in email.split("@")[-1]:
                print("Invalid email address.")
                return
            with self.db.connection:
                self.db.execute("""
                    UPDATE employees SET full_name=?, email=?, phone=?, department_id=?,
                    designation=?, salary=?, joining_date=? WHERE employee_id=?
                """, (name, email, phone, int(department_id), designation, salary,
                      joining_date, employee_id))
            print("Employee updated successfully.")
        except ValueError:
            print("Check department ID and date format (YYYY-MM-DD).")
        except sqlite3.IntegrityError as exc:
            print(f"Could not update employee: {exc}")

    @staticmethod
    def parse_nonnegative(value):
        try:
            number = float(value)
            return number if number >= 0 else None
        except ValueError:
            return None

    def delete_employee(self):
        try:
            employee_id = int(input("Employee ID to delete: ").strip())
        except ValueError:
            print("Employee ID must be a number.")
            return
        employee = self.find_employee(employee_id)
        if not employee:
            print("Employee not found.")
            return
        confirm = input(f"Delete {employee['full_name']} and related records? (y/n): ").strip().lower()
        if confirm == "y":
            with self.db.connection:
                self.db.execute("DELETE FROM employees WHERE employee_id=?", (employee_id,))
            print("Employee and linked attendance/payroll records deleted.")
        else:
            print("Deletion cancelled.")

    def mark_attendance(self):
        try:
            employee_id = int(input("Employee ID: ").strip())
        except ValueError:
            print("Employee ID must be a number.")
            return
        if not self.find_employee(employee_id):
            print("Employee not found.")
            return
        attendance_date = self.prompt_date("Date (YYYY-MM-DD): ")
        status = input("Status (Present/Absent/Leave): ").strip().title()
        if status not in ("Present", "Absent", "Leave"):
            print("Status must be Present, Absent, or Leave.")
            return
        try:
            with self.db.connection:
                self.db.execute("""
                    INSERT INTO attendance(employee_id, attendance_date, status)
                    VALUES (?, ?, ?)
                """, (employee_id, attendance_date, status))
            print("Attendance recorded.")
        except sqlite3.IntegrityError:
            print("Attendance for this employee and date already exists.")

    def view_attendance(self):
        rows = self.db.execute("""
            SELECT a.attendance_date, e.employee_id, e.full_name, a.status
            FROM attendance a JOIN employees e ON a.employee_id=e.employee_id
            ORDER BY a.attendance_date DESC, e.full_name
        """).fetchall()
        if not rows:
            print("No attendance records found.")
            return
        print("\nDate         ID   Employee                  Status")
        print("-" * 58)
        for row in rows:
            print(f"{row['attendance_date']:<13}{row['employee_id']:<5}"
                  f"{row['full_name']:<26}{row['status']}")

    def generate_payroll(self):
        try:
            employee_id = int(input("Employee ID: ").strip())
        except ValueError:
            print("Employee ID must be a number.")
            return
        employee = self.find_employee(employee_id)
        if not employee:
            print("Employee not found.")
            return
        month = input("Pay month (YYYY-MM): ").strip()
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            print("Use YYYY-MM format.")
            return
        bonus = self.prompt_number("Bonus: ")
        deductions = self.prompt_number("Deductions: ")
        basic = float(employee["salary"])
        net = basic + bonus - deductions
        if net < 0:
            print("Deductions cannot exceed basic salary plus bonus.")
            return
        try:
            with self.db.connection:
                self.db.execute("""
                    INSERT INTO payroll(employee_id, pay_month, basic_salary, bonus, deductions, net_salary)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (employee_id, month, basic, bonus, deductions, net))
            print(f"Payroll created. Net salary: {net:.2f}")
        except sqlite3.IntegrityError:
            print("Payroll for this employee and month already exists.")

    def view_payroll(self):
        rows = self.db.execute("""
            SELECT p.*, e.full_name FROM payroll p
            JOIN employees e ON p.employee_id=e.employee_id
            ORDER BY p.pay_month DESC, e.full_name
        """).fetchall()
        if not rows:
            print("No payroll records found.")
            return
        print("\nMonth     ID   Employee                  Basic      Bonus  Deductions   Net")
        print("-" * 82)
        for row in rows:
            print(f"{row['pay_month']:<10}{row['employee_id']:<5}{row['full_name'][:25]:<26}"
                  f"{row['basic_salary']:>10.2f}{row['bonus']:>10.2f}"
                  f"{row['deductions']:>12.2f}{row['net_salary']:>10.2f}")

    def run(self):
        actions = {
            "1": self.add_employee,
            "2": self.list_employees,
            "3": self.update_employee,
            "4": self.delete_employee,
            "5": self.add_department,
            "6": self.departments,
            "7": self.mark_attendance,
            "8": self.view_attendance,
            "9": self.generate_payroll,
            "10": self.view_payroll,
        }
        while True:
            print("""
==============================================
 EMPLOYEE RECORD MANAGEMENT SYSTEM
==============================================
1. Add Employee
2. View All Employees
3. Update Employee
4. Delete Employee
5. Add Department
6. View Departments
7. Mark Attendance
8. View Attendance Records
9. Generate Payroll
10. View Payroll Records
0. Exit
==============================================""")
            choice = input("Enter your choice: ").strip()
            if choice == "0":
                print("Thank you for using the Employee Record Management System!")
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Invalid choice. Please select from the menu.")
