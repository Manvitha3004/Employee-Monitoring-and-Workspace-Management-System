"""
Employee Tracking Module
Tracks employee presence, manages entry/exit events, and monitors absence.
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
import pickle


logger = logging.getLogger(__name__)


@dataclass
class EmployeePresence:
    """Represents current presence state of an employee."""
    employee_id: str
    log_id: Optional[int] = None
    entry_time: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    camera_id: Optional[int] = None
    is_present: bool = False
    absence_timer_started: bool = False
    absence_start_time: Optional[datetime] = None
    alert_sent: bool = False


class EmployeeTracker:
    """Tracks employee presence and absence."""
    
    def __init__(self, database_manager, config_manager, alert_manager):
        """
        Initialize employee tracker.
        
        Args:
            database_manager: Database manager instance
            config_manager: Configuration manager instance
            alert_manager: Alert manager instance
        """
        self.db = database_manager
        self.config = config_manager
        self.alert_manager = alert_manager
        
        self.presence_states: Dict[str, EmployeePresence] = {}
        self.lock = threading.Lock()
        
        # Configuration
        self.absence_timeout = config_manager.get_absence_timeout()
        self.presence_buffer = config_manager.get_presence_buffer()
        self.cooldown = config_manager.get('tracking.entry_exit_cooldown', 10)
        
        # Monitoring thread
        self.running = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start absence monitoring thread."""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Employee tracking monitoring started")
    
    def stop_monitoring(self):
        """Stop absence monitoring thread."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        logger.info("Employee tracking monitoring stopped")
    
    def update_detection(self, employee_id: str, camera_id: int):
        """
        Update employee detection.
        
        Args:
            employee_id: Employee identifier
            camera_id: Camera that detected the employee
        """
        with self.lock:
            current_time = datetime.now()
            
            if employee_id not in self.presence_states:
                # New employee detected
                self.presence_states[employee_id] = EmployeePresence(
                    employee_id=employee_id
                )
            
            state = self.presence_states[employee_id]
            state.last_seen = current_time
            state.camera_id = camera_id
            
            # Handle entry
            if not state.is_present:
                self._handle_entry(state, current_time, camera_id)
            
            # Reset absence tracking if employee returns
            if state.absence_timer_started:
                self._handle_return(state)
    
    def _handle_entry(self, state: EmployeePresence, entry_time: datetime, camera_id: int):
        """Handle employee entry."""
        # Check cooldown
        if state.entry_time:
            time_since_last = (entry_time - state.entry_time).total_seconds()
            if time_since_last < self.cooldown:
                return
        
        # Log entry in database
        log_id = self.db.log_entry(state.employee_id, camera_id)
        
        state.is_present = True
        state.entry_time = entry_time
        state.log_id = log_id
        state.absence_timer_started = False
        state.absence_start_time = None
        state.alert_sent = False
        
        logger.info(f"Employee {state.employee_id} entered (camera {camera_id})")
        
        # Log system event
        self.db.log_system_event('employee_entry', 
                                f"Employee {state.employee_id} entered via camera {camera_id}")
    
    def _handle_return(self, state: EmployeePresence):
        """Handle employee return after absence timer started."""
        if state.absence_timer_started and not state.alert_sent:
            logger.info(f"Employee {state.employee_id} returned before timeout")
        
        state.absence_timer_started = False
        state.absence_start_time = None
        state.alert_sent = False
    
    def _monitor_loop(self):
        """Main monitoring loop for absence detection."""
        while self.running:
            try:
                self._check_absences()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(1)
    
    def _check_absences(self):
        """Check for employee absences and trigger alerts."""
        with self.lock:
            current_time = datetime.now()
            
            for employee_id, state in list(self.presence_states.items()):
                if not state.is_present or not state.last_seen:
                    continue
                
                time_since_seen = (current_time - state.last_seen).total_seconds()
                
                # Start absence timer if not seen for buffer period
                if time_since_seen >= self.presence_buffer and not state.absence_timer_started:
                    state.absence_timer_started = True
                    state.absence_start_time = current_time
                    state.is_present = False
                    
                    # Log exit
                    if state.log_id:
                        self.db.log_exit(state.log_id)
                    
                    logger.info(f"Employee {employee_id} marked as absent, timer started")
                    self.db.log_system_event('employee_exit', 
                                            f"Employee {employee_id} no longer detected")
                
                # Check if absence timeout exceeded
                if state.absence_timer_started and not state.alert_sent:
                    absence_duration = (current_time - state.absence_start_time).total_seconds()
                    
                    if absence_duration >= self.absence_timeout:
                        # Trigger alert
                        self._trigger_absence_alert(state, absence_duration)
    
    def _trigger_absence_alert(self, state: EmployeePresence, absence_duration: float):
        """Trigger absence alert for employee."""
        state.alert_sent = True
        
        # Create alert in database
        alert_id = self.db.create_alert(state.employee_id, int(absence_duration))
        
        # Send notification via alert manager
        self.alert_manager.send_absence_alert(
            state.employee_id,
            int(absence_duration),
            alert_id
        )
        
        logger.warning(f"Absence alert triggered for employee {state.employee_id} "
                      f"(absent for {absence_duration:.0f} seconds)")
        
        self.db.log_system_event('absence_alert', 
                                f"Alert sent for employee {state.employee_id}")
    
    def get_present_employees(self) -> List[str]:
        """Get list of currently present employees."""
        with self.lock:
            return [emp_id for emp_id, state in self.presence_states.items() 
                   if state.is_present]
    
    def get_absent_employees(self) -> List[Dict[str, any]]:
        """Get list of absent employees with timer info."""
        with self.lock:
            absent = []
            current_time = datetime.now()
            
            for emp_id, state in self.presence_states.items():
                if state.absence_timer_started:
                    absence_duration = 0
                    if state.absence_start_time:
                        absence_duration = (current_time - state.absence_start_time).total_seconds()
                    
                    absent.append({
                        'employee_id': emp_id,
                        'absence_start': state.absence_start_time.isoformat() if state.absence_start_time else None,
                        'absence_duration': int(absence_duration),
                        'timeout_remaining': max(0, self.absence_timeout - absence_duration),
                        'alert_sent': state.alert_sent
                    })
            
            return absent
    
    def get_employee_status(self, employee_id: str) -> Optional[Dict[str, any]]:
        """Get current status of specific employee."""
        with self.lock:
            state = self.presence_states.get(employee_id)
            if not state:
                return None
            
            status = {
                'employee_id': employee_id,
                'is_present': state.is_present,
                'entry_time': state.entry_time.isoformat() if state.entry_time else None,
                'last_seen': state.last_seen.isoformat() if state.last_seen else None,
                'camera_id': state.camera_id,
                'absence_timer_started': state.absence_timer_started
            }
            
            if state.absence_timer_started and state.absence_start_time:
                absence_duration = (datetime.now() - state.absence_start_time).total_seconds()
                status['absence_duration'] = int(absence_duration)
                status['timeout_remaining'] = max(0, self.absence_timeout - absence_duration)
                status['alert_sent'] = state.alert_sent
            
            return status
    
    def get_all_statuses(self) -> List[Dict[str, any]]:
        """Get status of all tracked employees."""
        with self.lock:
            return [self.get_employee_status(emp_id) 
                   for emp_id in self.presence_states.keys()]
    
    def reset_employee(self, employee_id: str):
        """Reset tracking state for employee."""
        with self.lock:
            if employee_id in self.presence_states:
                del self.presence_states[employee_id]
                logger.info(f"Reset tracking state for employee {employee_id}")
    
    def register_employee_encoding(self, employee_id: str, face_encoding, name: str = None, department: str = None):
        """
        Register new employee with face encoding.
        
        Args:
            employee_id: Employee identifier
            face_encoding: Face encoding data
            name: Employee name
            department: Employee department
        """
        try:
            # Serialize face encoding
            encoding_bytes = pickle.dumps(face_encoding)
            
            # Add to database
            emp_name = name or employee_id
            self.db.add_employee(employee_id, emp_name, encoding_bytes, department)
            
            logger.info(f"Registered employee {employee_id}")
            self.db.log_system_event('employee_registered', 
                                    f"New employee registered: {employee_id}")
            
        except Exception as e:
            logger.error(f"Error registering employee: {e}")
