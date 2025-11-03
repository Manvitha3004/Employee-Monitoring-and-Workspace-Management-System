"""
Unit Tests for Employee Monitoring System
"""

import pytest
import os
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config_manager import ConfigManager
from src.database import DatabaseManager


class TestConfigManager:
    """Tests for ConfigManager."""
    
    def test_load_config(self):
        """Test loading configuration."""
        config = ConfigManager('config.yaml')
        assert config.config is not None
        assert 'cameras' in config.config
        assert 'detection' in config.config
    
    def test_get_value(self):
        """Test getting configuration values."""
        config = ConfigManager('config.yaml')
        
        # Test simple key
        cameras = config.get('cameras')
        assert cameras is not None
        
        # Test nested key
        method = config.get('detection.method')
        assert method in ['face', 'person', 'both']
        
        # Test default value
        unknown = config.get('unknown.key', 'default')
        assert unknown == 'default'
    
    def test_get_cameras(self):
        """Test getting camera list."""
        config = ConfigManager('config.yaml')
        cameras = config.get_cameras()
        assert isinstance(cameras, list)
    
    def test_get_absence_timeout(self):
        """Test getting absence timeout."""
        config = ConfigManager('config.yaml')
        timeout = config.get_absence_timeout()
        assert isinstance(timeout, int)
        assert timeout > 0


class TestDatabaseManager:
    """Tests for DatabaseManager."""
    
    @pytest.fixture
    def db(self, tmp_path):
        """Create temporary database for testing."""
        db_path = tmp_path / "test.db"
        return DatabaseManager(str(db_path))
    
    def test_database_initialization(self, db):
        """Test database initialization."""
        # Check if database file exists
        assert os.path.exists(db.db_path)
    
    def test_add_employee(self, db):
        """Test adding employee."""
        emp_id = db.add_employee('EMP001', 'John Doe')
        assert emp_id > 0
        
        # Verify employee exists
        employee = db.get_employee('EMP001')
        assert employee is not None
        assert employee['name'] == 'John Doe'
    
    def test_duplicate_employee(self, db):
        """Test adding duplicate employee."""
        db.add_employee('EMP001', 'John Doe')
        
        # Should raise exception for duplicate
        with pytest.raises(Exception):
            db.add_employee('EMP001', 'Jane Doe')
    
    def test_get_all_employees(self, db):
        """Test getting all employees."""
        db.add_employee('EMP001', 'John Doe')
        db.add_employee('EMP002', 'Jane Smith')
        
        employees = db.get_all_employees()
        assert len(employees) == 2
    
    def test_log_entry_exit(self, db):
        """Test logging entry and exit."""
        # Add employee
        db.add_employee('EMP001', 'John Doe')
        
        # Log entry
        log_id = db.log_entry('EMP001', camera_id=1)
        assert log_id > 0
        
        # Verify active presence
        presence = db.get_active_presence('EMP001')
        assert presence is not None
        assert presence['employee_id'] == 'EMP001'
        assert presence['exit_time'] is None
        
        # Log exit
        db.log_exit(log_id)
        
        # Verify exit logged
        presence = db.get_active_presence('EMP001')
        assert presence is None
    
    def test_create_alert(self, db):
        """Test creating absence alert."""
        db.add_employee('EMP001', 'John Doe')
        
        alert_id = db.create_alert('EMP001', absence_duration=1200)
        assert alert_id > 0
        
        # Verify alert exists
        alerts = db.get_unacknowledged_alerts()
        assert len(alerts) == 1
        assert alerts[0]['employee_id'] == 'EMP001'
    
    def test_acknowledge_alert(self, db):
        """Test acknowledging alert."""
        db.add_employee('EMP001', 'John Doe')
        alert_id = db.create_alert('EMP001', 1200)
        
        # Acknowledge
        db.acknowledge_alert(alert_id)
        
        # Verify acknowledged
        alerts = db.get_unacknowledged_alerts()
        assert len(alerts) == 0
    
    def test_get_presence_logs(self, db):
        """Test getting presence logs."""
        db.add_employee('EMP001', 'John Doe')
        
        # Create some logs
        log_id1 = db.log_entry('EMP001', 1)
        db.log_exit(log_id1)
        
        log_id2 = db.log_entry('EMP001', 1)
        
        # Get logs
        logs = db.get_presence_logs(employee_id='EMP001')
        assert len(logs) >= 2
    
    def test_get_current_occupancy(self, db):
        """Test getting current occupancy."""
        db.add_employee('EMP001', 'John Doe')
        db.add_employee('EMP002', 'Jane Smith')
        
        # Both enter
        db.log_entry('EMP001', 1)
        db.log_entry('EMP002', 1)
        
        occupancy = db.get_current_occupancy()
        assert occupancy == 2
        
        # One exits
        log = db.get_active_presence('EMP001')
        db.log_exit(log['id'])
        
        occupancy = db.get_current_occupancy()
        assert occupancy == 1
    
    def test_employee_stats(self, db):
        """Test getting employee statistics."""
        db.add_employee('EMP001', 'John Doe')
        
        # Create log entry
        log_id = db.log_entry('EMP001', 1)
        db.log_exit(log_id)
        
        # Get stats
        stats = db.get_employee_stats('EMP001', days=30)
        assert stats['visits'] >= 1
        assert 'total_duration' in stats


class TestIntegration:
    """Integration tests."""
    
    def test_system_workflow(self, tmp_path):
        """Test complete workflow."""
        # Create test database
        db_path = tmp_path / "test.db"
        db = DatabaseManager(str(db_path))
        
        # Register employee
        db.add_employee('EMP001', 'John Doe')
        
        # Employee enters
        log_id = db.log_entry('EMP001', camera_id=1)
        assert log_id > 0
        
        # Verify presence
        occupancy = db.get_current_occupancy()
        assert occupancy == 1
        
        # Employee exits
        db.log_exit(log_id)
        
        # Verify absence
        occupancy = db.get_current_occupancy()
        assert occupancy == 0
        
        # Create alert
        alert_id = db.create_alert('EMP001', 1200)
        
        # Verify alert
        alerts = db.get_unacknowledged_alerts()
        assert len(alerts) == 1
        
        # Acknowledge
        db.acknowledge_alert(alert_id)
        
        # Verify no unacknowledged alerts
        alerts = db.get_unacknowledged_alerts()
        assert len(alerts) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
