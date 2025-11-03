"""
Database Cleanup Utility
Removes old logs and maintains database health.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import DatabaseManager


def cleanup_database(db_path, retention_days=90, vacuum=True):
    """
    Clean up old database records.
    
    Args:
        db_path: Path to database
        retention_days: Keep records for this many days
        vacuum: Whether to vacuum database after cleanup
    """
    print(f"Cleaning up database: {db_path}")
    print(f"Retention period: {retention_days} days")
    print()
    
    db = DatabaseManager(db_path)
    
    try:
        # Clean up old logs
        print("Removing old logs...")
        db.cleanup_old_logs(retention_days)
        print("✓ Old logs removed")
        
        # Get statistics
        total_employees = len(db.get_all_employees())
        current_occupancy = db.get_current_occupancy()
        
        print()
        print("Database Statistics:")
        print(f"- Total employees: {total_employees}")
        print(f"- Current occupancy: {current_occupancy}")
        
        # Vacuum database if requested
        if vacuum:
            print()
            print("Vacuuming database...")
            with db._get_connection() as conn:
                conn.execute('VACUUM')
            print("✓ Database vacuumed")
        
        print()
        print("✓ Cleanup complete!")
        
    except Exception as e:
        print(f"✗ Error during cleanup: {e}")
        return False
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database cleanup utility')
    parser.add_argument('--db', default='data/employees.db', help='Database path')
    parser.add_argument('--retention', type=int, default=90, 
                       help='Keep records for N days')
    parser.add_argument('--no-vacuum', action='store_true', 
                       help='Skip database vacuum')
    
    args = parser.parse_args()
    
    cleanup_database(args.db, args.retention, not args.no_vacuum)
