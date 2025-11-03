import sqlite3

conn = sqlite3.connect('data/employees.db')
cursor = conn.cursor()

print("\n=== REGISTERED EMPLOYEES ===")
cursor.execute('SELECT employee_id, name, department, created_at FROM employees')
employees = cursor.fetchall()
if employees:
    for emp in employees:
        print(f"ID: {emp[0]}, Name: {emp[1]}, Dept: {emp[2]}, Created: {emp[3]}")
else:
    print("No employees registered")

print("\n=== PRESENCE LOGS ===")
cursor.execute('SELECT employee_id, entry_time, exit_time FROM presence_logs ORDER BY entry_time DESC LIMIT 5')
logs = cursor.fetchall()
if logs:
    for log in logs:
        print(f"Employee: {log[0]}, Entry: {log[1]}, Exit: {log[2]}")
else:
    print("No presence logs")

print("\n=== TOTAL COUNT ===")
cursor.execute('SELECT COUNT(*) FROM employees')
emp_count = cursor.fetchone()[0]
print(f"Total employees: {emp_count}")

conn.close()
