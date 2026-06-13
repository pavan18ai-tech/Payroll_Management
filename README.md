# Payroll_Management
# Payroll Management System

A complete Payroll Management System with Flask backend, MySQL database, and modern web interface.

## Features

- ✅ Employee Management (CRUD operations)
- ✅ Attendance Tracking with auto-salary update trigger
- ✅ Leave Management with 10-day limit trigger  
- ✅ Salary Processing with stored procedures
- ✅ 10 Complex SQL Queries (JOINs, GROUP BY, Subqueries, etc.)
- ✅ Modern Responsive UI

## Tech Stack

- **Backend:** Python Flask
- **Database:** MySQL
- **Frontend:** HTML, Tailwind CSS, JavaScript
- **Database Features:** Stored Procedures, Triggers

## Quick Setup

```bash
# 1. Install dependencies
pip install flask flask-cors mysql-connector-python

# 2. Run the app
python app.py

# 3. Open browser
http://localhost:5000
Database Setup
Run the SQL schema to create:

Tables (Employee, Department, Salary, Attendance, Leave, Bonus)

Stored Procedures (CalculateMonthlySalary, GeneratePayslip)

Triggers (UpdateSalaryAfterAttendance, PreventExcessLeave)

Project Structure
├── app.py              # Flask backend
├── templates/
│   └── index.html      # Frontend UI
└── README.md
Author
Pavan Bhat - @pavan18ai-tech

Live Demo
Visit: https://github.com/pavan18ai-tech/Payroll_Management

## Push to GitHub:

```powershell
cd D:\Payroll_system
echo "# Payroll Management System" > README.md
echo "" >> README.md
echo "A complete Payroll Management System with Flask, MySQL, triggers, and stored procedures." >> README.md
git add README.md
git commit -m "Add README"
git push origin main
