"""
Database Upgrade Script
Adds missing columns to existing database.
"""

import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def upgrade_database(db_path='data/employees.db'):
    """Add department column if it doesn't exist."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if department column exists
        cursor.execute("PRAGMA table_info(employees)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'department' not in columns:
            print("Adding 'department' column to employees table...")
            cursor.execute("ALTER TABLE employees ADD COLUMN department TEXT")
            conn.commit()
            print("✅ Database upgraded successfully!")
        else:
            print("✅ Database already up to date.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error upgrading database: {e}")
        return False
    
    return True

if __name__ == '__main__':
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'data/employees.db'
    
    print(f"Upgrading database: {db_path}")
    upgrade_database(db_path)
