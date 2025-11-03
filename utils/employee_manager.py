"""
Utility Scripts for Employee Management
Provides command-line tools for managing employees.
"""

import sys
import os
import argparse
import pickle

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import DatabaseManager
from src.detection import FaceDetector


def register_employee(db_path, employee_id, name, photo_path=None):
    """Register a new employee."""
    db = DatabaseManager(db_path)
    
    try:
        if photo_path and os.path.exists(photo_path):
            # Load face encoding
            detector = FaceDetector(recognition_enabled=True)
            success = detector.add_known_face_from_image(employee_id, photo_path)
            
            if success:
                encoding = detector.known_faces[employee_id]
                encoding_bytes = pickle.dumps(encoding)
                db.add_employee(employee_id, name, encoding_bytes)
                print(f"✓ Employee {employee_id} registered with face recognition")
            else:
                print(f"✗ Failed to extract face from photo")
                print(f"  Registering employee without face recognition...")
                db.add_employee(employee_id, name)
                print(f"✓ Employee {employee_id} registered (no face recognition)")
        else:
            db.add_employee(employee_id, name)
            print(f"✓ Employee {employee_id} registered")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True


def list_employees(db_path):
    """List all employees."""
    db = DatabaseManager(db_path)
    
    employees = db.get_all_employees()
    
    if not employees:
        print("No employees registered")
        return
    
    print("\nRegistered Employees:")
    print("-" * 80)
    print(f"{'ID':<15} {'Name':<30} {'Face Recognition':<20} {'Active'}")
    print("-" * 80)
    
    for emp in employees:
        has_face = "✓" if emp.get('face_encoding') else "✗"
        active = "✓" if emp.get('active') else "✗"
        print(f"{emp['employee_id']:<15} {emp['name']:<30} {has_face:<20} {active}")
    
    print("-" * 80)
    print(f"Total: {len(employees)} employees")


def delete_employee(db_path, employee_id):
    """Deactivate an employee."""
    db = DatabaseManager(db_path)
    
    try:
        db.update_employee(employee_id, active=0)
        print(f"✓ Employee {employee_id} deactivated")
    except Exception as e:
        print(f"✗ Error: {e}")


def view_logs(db_path, employee_id=None, limit=20):
    """View presence logs."""
    db = DatabaseManager(db_path)
    
    kwargs = {'limit': limit}
    if employee_id:
        kwargs['employee_id'] = employee_id
    
    logs = db.get_presence_logs(**kwargs)
    
    if not logs:
        print("No logs found")
        return
    
    print("\nPresence Logs:")
    print("-" * 120)
    print(f"{'Employee ID':<15} {'Entry Time':<25} {'Exit Time':<25} {'Duration':<15} {'Camera'}")
    print("-" * 120)
    
    for log in logs:
        duration = f"{log['duration_seconds']}s" if log['duration_seconds'] else "Active"
        exit_time = log['exit_time'] or "Still present"
        camera = f"Camera {log['camera_id']}" if log['camera_id'] else "N/A"
        
        print(f"{log['employee_id']:<15} {log['entry_time']:<25} {exit_time:<25} {duration:<15} {camera}")
    
    print("-" * 120)


def view_alerts(db_path, unacknowledged_only=False):
    """View alerts."""
    db = DatabaseManager(db_path)
    
    if unacknowledged_only:
        alerts = db.get_unacknowledged_alerts()
    else:
        alerts = db.get_recent_alerts(hours=24)
    
    if not alerts:
        print("No alerts found")
        return
    
    print("\nAlerts:")
    print("-" * 100)
    print(f"{'ID':<8} {'Employee ID':<15} {'Alert Time':<25} {'Duration (min)':<15} {'Acknowledged'}")
    print("-" * 100)
    
    for alert in alerts:
        duration_min = alert['absence_duration_seconds'] // 60
        ack = "✓" if alert['acknowledged'] else "✗"
        
        print(f"{alert['id']:<8} {alert['employee_id']:<15} {alert['alert_time']:<25} {duration_min:<15} {ack}")
    
    print("-" * 100)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Employee Management Utilities')
    parser.add_argument('--db', default='data/employees.db', help='Database path')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Register employee
    register_parser = subparsers.add_parser('register', help='Register new employee')
    register_parser.add_argument('employee_id', help='Employee ID')
    register_parser.add_argument('name', help='Employee name')
    register_parser.add_argument('--photo', help='Path to employee photo')
    
    # List employees
    subparsers.add_parser('list', help='List all employees')
    
    # Delete employee
    delete_parser = subparsers.add_parser('delete', help='Deactivate employee')
    delete_parser.add_argument('employee_id', help='Employee ID')
    
    # View logs
    logs_parser = subparsers.add_parser('logs', help='View presence logs')
    logs_parser.add_argument('--employee', help='Filter by employee ID')
    logs_parser.add_argument('--limit', type=int, default=20, help='Number of logs to show')
    
    # View alerts
    alerts_parser = subparsers.add_parser('alerts', help='View alerts')
    alerts_parser.add_argument('--unacknowledged', action='store_true', 
                             help='Show only unacknowledged alerts')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'register':
        register_employee(args.db, args.employee_id, args.name, args.photo)
    elif args.command == 'list':
        list_employees(args.db)
    elif args.command == 'delete':
        delete_employee(args.db, args.employee_id)
    elif args.command == 'logs':
        view_logs(args.db, args.employee, args.limit)
    elif args.command == 'alerts':
        view_alerts(args.db, args.unacknowledged)


if __name__ == '__main__':
    main()
