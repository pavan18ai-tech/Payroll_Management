from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration - YOUR EXISTING PAYROLL DATABASE
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '@BROTHERs#2025',
    'database': 'payroll_system'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

# =====================================================================
# EMPLOYEE MANAGEMENT API
# =====================================================================

@app.route('/api/employees', methods=['GET'])
def get_employees():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT e.*, d.department_name 
            FROM Employee e
            LEFT JOIN Department d ON e.department_id = d.department_id
            ORDER BY e.employee_id DESC
        """)
        employees = cursor.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': employees})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/employees/<int:emp_id>', methods=['GET'])
def get_employee(emp_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT e.*, d.department_name, s.basic_salary, s.allowances, s.deductions, s.net_salary
            FROM Employee e
            LEFT JOIN Department d ON e.department_id = d.department_id
            LEFT JOIN Salary s ON e.employee_id = s.employee_id
            WHERE e.employee_id = %s
        """, (emp_id,))
        employee = cursor.fetchone()
        conn.close()
        return jsonify({'success': True, 'data': employee})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/employees', methods=['POST'])
def add_employee():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    data = request.json
    
    try:
        cursor.execute(
            "INSERT INTO Employee (name, department_id, designation) VALUES (%s, %s, %s)",
            (data['name'], data['department_id'], data['designation'])
        )
        conn.commit()
        emp_id = cursor.lastrowid
        
        # Create default salary record
        cursor.execute(
            "INSERT INTO Salary (employee_id, basic_salary, allowances, deductions, net_salary) VALUES (%s, %s, %s, %s, %s)",
            (emp_id, 30000, 5000, 2000, 33000)
        )
        conn.commit()
        
        conn.close()
        return jsonify({'success': True, 'message': 'Employee added successfully', 'employee_id': emp_id})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/employees/<int:emp_id>', methods=['PUT'])
def update_employee(emp_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    data = request.json
    
    try:
        cursor.execute(
            "UPDATE Employee SET name=%s, department_id=%s, designation=%s WHERE employee_id=%s",
            (data['name'], data['department_id'], data['designation'], emp_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Employee updated successfully'})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/employees/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Salary WHERE employee_id=%s", (emp_id,))
        cursor.execute("DELETE FROM Attendance WHERE employee_id=%s", (emp_id,))
        cursor.execute("DELETE FROM `Leave` WHERE employee_id=%s", (emp_id,))
        cursor.execute("DELETE FROM Bonus WHERE employee_id=%s", (emp_id,))
        cursor.execute("DELETE FROM Employee WHERE employee_id=%s", (emp_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Employee deleted successfully'})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================================
# DEPARTMENT API
# =====================================================================

@app.route('/api/departments', methods=['GET'])
def get_departments():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Department ORDER BY department_id")
        departments = cursor.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': departments})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================================
# SALARY API
# =====================================================================

@app.route('/api/salaries', methods=['GET'])
def get_salaries():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT s.*, e.name as employee_name
            FROM Salary s
            JOIN Employee e ON s.employee_id = e.employee_id
            ORDER BY s.salary_id DESC
        """)
        salaries = cursor.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': salaries})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/salaries/<int:emp_id>', methods=['PUT'])
def update_salary(emp_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    data = request.json
    
    try:
        net = data['basic_salary'] + data['allowances'] - data['deductions']
        cursor.execute(
            "UPDATE Salary SET basic_salary=%s, allowances=%s, deductions=%s, net_salary=%s WHERE employee_id=%s",
            (data['basic_salary'], data['allowances'], data['deductions'], net, emp_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Salary updated successfully'})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================================
# ATTENDANCE API
# =====================================================================

@app.route('/api/attendance', methods=['POST'])
def add_attendance():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    data = request.json
    
    try:
        cursor.execute(
            "INSERT INTO Attendance (employee_id, month, days_present) VALUES (%s, %s, %s)",
            (data['employee_id'], data['month'], data['days_present'])
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Attendance added! Trigger executed - Salary updated'})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/attendance/employee/<int:emp_id>', methods=['GET'])
def get_attendance(emp_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM Attendance WHERE employee_id = %s ORDER BY attendance_id DESC",
            (emp_id,)
        )
        attendance = cursor.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': attendance})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================================
# LEAVE API (WITH TRIGGER VALIDATION)
# =====================================================================

@app.route('/api/leaves', methods=['POST'])
def add_leave():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    data = request.json
    
    try:
        cursor.execute(
            "INSERT INTO `Leave` (employee_id, leave_days, leave_type) VALUES (%s, %s, %s)",
            (data['employee_id'], data['leave_days'], data['leave_type'])
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Leave request submitted successfully'})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/leaves/employee/<int:emp_id>', methods=['GET'])
def get_leaves(emp_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM `Leave` WHERE employee_id = %s ORDER BY leave_id DESC",
            (emp_id,)
        )
        leaves = cursor.fetchall()
        
        # Calculate total leaves
        total = sum(leave['leave_days'] for leave in leaves)
        
        conn.close()
        return jsonify({'success': True, 'data': leaves, 'total_leaves': total})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================================
# BONUS API
# =====================================================================

@app.route('/api/bonuses', methods=['POST'])
def add_bonus():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    data = request.json
    
    try:
        cursor.execute(
            "INSERT INTO Bonus (employee_id, bonus_amount) VALUES (%s, %s)",
            (data['employee_id'], data['bonus_amount'])
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Bonus added successfully'})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================================
# STORED PROCEDURES
# =====================================================================

@app.route('/api/calculate-salary/<int:emp_id>', methods=['POST'])
def calculate_salary_procedure(emp_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.callproc('CalculateMonthlySalary', [emp_id])
        
        # Get result from stored procedure
        result = None
        for res in cursor.stored_results():
            result = res.fetchall()
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Salary calculated successfully', 'data': result})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-payslip/<int:emp_id>', methods=['GET'])
def generate_payslip_procedure(emp_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.callproc('GeneratePayslip', [emp_id])
        
        payslip = None
        for result in cursor.stored_results():
            payslip = result.fetchall()
        
        conn.close()
        return jsonify({'success': True, 'data': payslip})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================================
# QUERIES (1-10 from your requirements)
# =====================================================================

@app.route('/api/queries/<int:query_id>', methods=['GET'])
def execute_query(query_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    queries = {
        1: "SELECT * FROM Employee",
        2: "SELECT e.*, d.department_name FROM Employee e JOIN Department d ON e.department_id = d.department_id WHERE d.department_name = %s",
        3: """SELECT e.employee_id, e.name, e.designation, s.basic_salary, s.allowances, s.deductions, s.net_salary
              FROM Employee e INNER JOIN Salary s ON e.employee_id = s.employee_id""",
        4: """SELECT e.name, d.department_name, e.designation, s.basic_salary, s.net_salary
              FROM Employee e
              JOIN Department d ON e.department_id = d.department_id
              JOIN Salary s ON e.employee_id = s.employee_id""",
        5: """SELECT d.department_name, COUNT(e.employee_id) AS employee_count
              FROM Department d
              LEFT JOIN Employee e ON d.department_id = e.department_id
              GROUP BY d.department_id""",
        6: """SELECT d.department_name, AVG(s.net_salary) AS avg_salary
              FROM Department d
              JOIN Employee e ON d.department_id = e.department_id
              JOIN Salary s ON e.employee_id = s.employee_id
              GROUP BY d.department_id
              HAVING avg_salary > 50000""",
        7: """SELECT e.name, s.net_salary
              FROM Employee e
              JOIN Salary s ON e.employee_id = s.employee_id
              WHERE s.net_salary > (SELECT AVG(net_salary) FROM Salary)""",
        8: """SELECT e1.name, e1.department_id, s1.net_salary
              FROM Employee e1
              JOIN Salary s1 ON e1.employee_id = s1.employee_id
              WHERE s1.net_salary > (
                  SELECT s2.net_salary 
                  FROM Employee e2 
                  JOIN Salary s2 ON e2.employee_id = s2.employee_id 
                  WHERE e2.name = %s AND e2.department_id = e1.department_id
              )""",
        9: """SELECT e.employee_id, e.name, e.designation, s.basic_salary, s.net_salary
              FROM Employee e
              LEFT JOIN Salary s ON e.employee_id = s.employee_id""",
        10: """SELECT d.department_id, d.department_name
               FROM Department d
               WHERE NOT EXISTS (SELECT 1 FROM Employee e WHERE e.department_id = d.department_id)"""
    }
    
    selected_query = queries.get(query_id)
    if not selected_query:
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid query ID'}), 404
    
    try:
        if query_id == 2:
            dept_param = request.args.get('department_name', 'IT')
            cursor.execute(selected_query, (dept_param,))
        elif query_id == 8:
            emp_param = request.args.get('employee_name', 'John Doe')
            cursor.execute(selected_query, (emp_param,))
        else:
            cursor.execute(selected_query)
        
        results = cursor.fetchall()
        
        # Convert decimal to float for JSON serialization
        for row in results:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
        
        conn.close()
        return jsonify({'success': True, 'data': results})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================================
# DASHBOARD STATISTICS
# =====================================================================

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Total employees
        cursor.execute("SELECT COUNT(*) as total FROM Employee")
        total_employees = cursor.fetchone()['total']
        
        # Total departments
        cursor.execute("SELECT COUNT(*) as total FROM Department")
        total_departments = cursor.fetchone()['total']
        
        # Average salary
        cursor.execute("SELECT AVG(net_salary) as avg_salary FROM Salary")
        avg_salary = cursor.fetchone()['avg_salary']
        if avg_salary:
            avg_salary = float(avg_salary)
        else:
            avg_salary = 0
        
        # Total salary payout
        cursor.execute("SELECT SUM(net_salary) as total FROM Salary")
        total_payout = cursor.fetchone()['total']
        if total_payout:
            total_payout = float(total_payout)
        else:
            total_payout = 0
        
        # Attendance this month
        cursor.execute("SELECT COUNT(*) as total FROM Attendance WHERE month = MONTHNAME(CURDATE())")
        attendance_count = cursor.fetchone()['total']
        
        conn.close()
        return jsonify({
            'success': True,
            'data': {
                'total_employees': total_employees,
                'total_departments': total_departments,
                'avg_salary': avg_salary,
                'total_payout': total_payout,
                'attendance_count': attendance_count
            }
        })
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

from decimal import Decimal

if __name__ == '__main__':
    app.run(debug=True, port=5000)