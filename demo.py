"""
Demo Script - Quick Test of Employee Monitoring System
This script demonstrates the system functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import DatabaseManager

def demo():
    """Run a quick demo."""
    print("=" * 60)
    print("Employee Monitoring System - Quick Demo")
    print("=" * 60)
    print()
    
    # Initialize database
    db = DatabaseManager("data/employees.db")
    
    # Register demo employees
    print("1. Registering demo employees...")
    try:
        db.add_employee("EMP001", "John Doe")
        print("   ✓ Registered: EMP001 - John Doe")
    except:
        print("   ℹ Employee EMP001 already exists")
    
    try:
        db.add_employee("EMP002", "Jane Smith")
        print("   ✓ Registered: EMP002 - Jane Smith")
    except:
        print("   ℹ Employee EMP002 already exists")
    
    try:
        db.add_employee("EMP003", "Mike Johnson")
        print("   ✓ Registered: EMP003 - Mike Johnson")
    except:
        print("   ℹ Employee EMP003 already exists")
    
    print()
    
    # Show employee list
    print("2. Current Employees:")
    employees = db.get_all_employees()
    for emp in employees:
        status = "Active" if emp['active'] else "Inactive"
        print(f"   - {emp['employee_id']}: {emp['name']} ({status})")
    
    print()
    
    # Simulate some activity
    print("3. Simulating employee activity...")
    
    # Employee 1 enters
    log_id1 = db.log_entry("EMP001", camera_id=1)
    print("   ✓ EMP001 entered (Camera 1)")
    
    # Employee 2 enters
    log_id2 = db.log_entry("EMP002", camera_id=1)
    print("   ✓ EMP002 entered (Camera 1)")
    
    print()
    
    # Check current occupancy
    occupancy = db.get_current_occupancy()
    print(f"4. Current Occupancy: {occupancy} employee(s)")
    
    print()
    
    # Show presence logs
    print("5. Recent Activity Logs:")
    logs = db.get_presence_logs(limit=5)
    for log in logs:
        status = "Still present" if log['exit_time'] is None else "Exited"
        print(f"   - {log['employee_id']}: Entered at {log['entry_time'][:19]} - {status}")
    
    print()
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print()
    print("🌐 Web Interface: http://127.0.0.1:5000")
    print("📊 Check the dashboard to see employees and activity!")
    print()

if __name__ == '__main__':
    demo()
