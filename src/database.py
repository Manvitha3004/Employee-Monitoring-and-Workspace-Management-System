"""
Database Manager
Handles all database operations for employee tracking and logging.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import contextmanager


class DatabaseManager:
    """Manages SQLite database for employee tracking."""
    
    def __init__(self, db_path: str = "data/employees.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_directory()
        self._initialize_database()
    
    def _ensure_directory(self):
        """Ensure database directory exists."""
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Employees table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    department TEXT,
                    face_encoding BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active INTEGER DEFAULT 1
                )
            ''')
            
            # Presence logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS presence_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT NOT NULL,
                    camera_id INTEGER,
                    entry_time TIMESTAMP NOT NULL,
                    exit_time TIMESTAMP,
                    duration_seconds INTEGER,
                    status TEXT DEFAULT 'present',
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                )
            ''')
            
            # Absence alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS absence_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT NOT NULL,
                    alert_time TIMESTAMP NOT NULL,
                    absence_duration_seconds INTEGER,
                    acknowledged INTEGER DEFAULT 0,
                    acknowledged_at TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                )
            ''')
            
            # System events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_presence_employee 
                ON presence_logs(employee_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_presence_entry 
                ON presence_logs(entry_time)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_alerts_employee 
                ON absence_alerts(employee_id)
            ''')
    
    # Employee management
    def add_employee(self, employee_id: str, name: str, face_encoding: bytes = None, department: str = None) -> int:
        """
        Add a new employee to the database.
        
        Args:
            employee_id: Unique employee identifier
            name: Employee name
            face_encoding: Serialized face encoding (optional)
            department: Employee department (optional)
            
        Returns:
            Database ID of created employee
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO employees (employee_id, name, department, face_encoding)
                VALUES (?, ?, ?, ?)
            ''', (employee_id, name, department, face_encoding))
            return cursor.lastrowid
    
    def get_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get employee by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM employees WHERE employee_id = ? AND active = 1
            ''', (employee_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_employees(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all employees."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM employees'
            if active_only:
                query += ' WHERE active = 1'
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_employee(self, employee_id: str, **kwargs):
        """Update employee information."""
        if not kwargs:
            return
        
        allowed_fields = ['name', 'department', 'face_encoding', 'active']
        fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        fields['updated_at'] = datetime.now()
        
        set_clause = ', '.join([f"{k} = ?" for k in fields.keys()])
        values = list(fields.values()) + [employee_id]
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE employees SET {set_clause}
                WHERE employee_id = ?
            ''', values)
    
    # Presence logging
    def log_entry(self, employee_id: str, camera_id: int = None) -> int:
        """
        Log employee entry.
        
        Args:
            employee_id: Employee identifier
            camera_id: Camera that detected the employee
            
        Returns:
            Log entry ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO presence_logs (employee_id, camera_id, entry_time, status)
                VALUES (?, ?, ?, 'present')
            ''', (employee_id, camera_id, datetime.now()))
            return cursor.lastrowid
    
    def log_exit(self, log_id: int):
        """
        Log employee exit and calculate duration.
        
        Args:
            log_id: Presence log ID to update
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get entry time
            cursor.execute('SELECT entry_time FROM presence_logs WHERE id = ?', (log_id,))
            row = cursor.fetchone()
            if not row:
                return
            
            entry_time = datetime.fromisoformat(row['entry_time'])
            exit_time = datetime.now()
            duration = int((exit_time - entry_time).total_seconds())
            
            cursor.execute('''
                UPDATE presence_logs 
                SET exit_time = ?, duration_seconds = ?, status = 'absent'
                WHERE id = ?
            ''', (exit_time, duration, log_id))
    
    def get_active_presence(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get current active presence log for employee."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM presence_logs 
                WHERE employee_id = ? AND exit_time IS NULL
                ORDER BY entry_time DESC LIMIT 1
            ''', (employee_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_presence_logs(self, employee_id: str = None, 
                         start_date: datetime = None,
                         end_date: datetime = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get presence logs with optional filtering.
        
        Args:
            employee_id: Filter by employee (optional)
            start_date: Filter logs after this date (optional)
            end_date: Filter logs before this date (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of presence log records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM presence_logs WHERE 1=1'
            params = []
            
            if employee_id:
                query += ' AND employee_id = ?'
                params.append(employee_id)
            
            if start_date:
                query += ' AND entry_time >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND entry_time <= ?'
                params.append(end_date)
            
            query += ' ORDER BY entry_time DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # Absence alerts
    def create_alert(self, employee_id: str, absence_duration: int) -> int:
        """
        Create absence alert.
        
        Args:
            employee_id: Employee identifier
            absence_duration: Duration of absence in seconds
            
        Returns:
            Alert ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO absence_alerts 
                (employee_id, alert_time, absence_duration_seconds)
                VALUES (?, ?, ?)
            ''', (employee_id, datetime.now(), absence_duration))
            return cursor.lastrowid
    
    def acknowledge_alert(self, alert_id: int):
        """Mark alert as acknowledged."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE absence_alerts 
                SET acknowledged = 1, acknowledged_at = ?
                WHERE id = ?
            ''', (datetime.now(), alert_id))
    
    def get_unacknowledged_alerts(self) -> List[Dict[str, Any]]:
        """Get all unacknowledged alerts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM absence_alerts 
                WHERE acknowledged = 0
                ORDER BY alert_time DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_alerts(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM absence_alerts 
                WHERE alert_time >= ?
                ORDER BY alert_time DESC LIMIT ?
            ''', (cutoff, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    # System events
    def log_system_event(self, event_type: str, event_data: str = None):
        """Log system event."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO system_events (event_type, event_data)
                VALUES (?, ?)
            ''', (event_type, event_data))
    
    # Statistics
    def get_current_occupancy(self) -> int:
        """Get current number of employees present."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(DISTINCT employee_id) as count
                FROM presence_logs 
                WHERE exit_time IS NULL
            ''')
            row = cursor.fetchone()
            return row['count'] if row else 0
    
    def get_employee_stats(self, employee_id: str, days: int = 30) -> Dict[str, Any]:
        """Get employee statistics."""
        cutoff = datetime.now() - timedelta(days=days)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total visits
            cursor.execute('''
                SELECT COUNT(*) as visits,
                       SUM(duration_seconds) as total_duration,
                       AVG(duration_seconds) as avg_duration
                FROM presence_logs 
                WHERE employee_id = ? AND entry_time >= ?
            ''', (employee_id, cutoff))
            stats = dict(cursor.fetchone())
            
            # Alerts count
            cursor.execute('''
                SELECT COUNT(*) as alerts
                FROM absence_alerts 
                WHERE employee_id = ? AND alert_time >= ?
            ''', (employee_id, cutoff))
            stats['alerts'] = cursor.fetchone()['alerts']
            
            return stats
    
    def cleanup_old_logs(self, retention_days: int):
        """Delete logs older than retention period."""
        cutoff = datetime.now() - timedelta(days=retention_days)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM presence_logs WHERE entry_time < ?
            ''', (cutoff,))
            cursor.execute('''
                DELETE FROM absence_alerts WHERE alert_time < ?
            ''', (cutoff,))
            cursor.execute('''
                DELETE FROM system_events WHERE timestamp < ?
            ''', (cutoff,))
