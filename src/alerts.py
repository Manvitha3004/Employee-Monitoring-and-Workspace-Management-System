"""
Alert Manager
Handles absence alerts through various notification channels.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Set
from plyer import notification
import winsound


logger = logging.getLogger(__name__)


class AlertManager:
    """Manages absence alerts and notifications."""
    
    def __init__(self, config_manager):
        """
        Initialize alert manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager
        self.alert_settings = config_manager.get_alert_settings()
        
        self.enabled = self.alert_settings.get('enabled', True)
        self.sound_enabled = self.alert_settings.get('sound_enabled', True)
        self.notification_enabled = self.alert_settings.get('notification_enabled', True)
        self.repeat_interval = self.alert_settings.get('alert_repeat_interval', 300)
        
        # Track recent alerts to prevent spam
        self.recent_alerts: Dict[str, datetime] = {}
        self.lock = threading.Lock()
    
    def send_absence_alert(self, employee_id: str, absence_duration: int, alert_id: int):
        """
        Send absence alert for employee.
        
        Args:
            employee_id: Employee identifier
            absence_duration: Duration of absence in seconds
            alert_id: Database alert ID
        """
        if not self.enabled:
            return
        
        # Check if we recently sent alert for this employee
        if not self._should_send_alert(employee_id):
            logger.debug(f"Skipping duplicate alert for {employee_id}")
            return
        
        # Format duration
        duration_minutes = absence_duration // 60
        
        # Send notifications
        if self.notification_enabled:
            self._send_desktop_notification(employee_id, duration_minutes)
        
        if self.sound_enabled:
            self._play_alert_sound()
        
        # Update recent alerts
        with self.lock:
            self.recent_alerts[employee_id] = datetime.now()
        
        logger.info(f"Alert sent for employee {employee_id} (absent {duration_minutes} min)")
    
    def _should_send_alert(self, employee_id: str) -> bool:
        """Check if alert should be sent based on repeat interval."""
        with self.lock:
            if employee_id not in self.recent_alerts:
                return True
            
            last_alert = self.recent_alerts[employee_id]
            time_since_last = (datetime.now() - last_alert).total_seconds()
            
            return time_since_last >= self.repeat_interval
    
    def _send_desktop_notification(self, employee_id: str, duration_minutes: int):
        """Send desktop notification."""
        try:
            notification.notify(
                title="Employee Absence Alert",
                message=f"Employee {employee_id} has been absent for {duration_minutes} minutes",
                app_name="Employee Monitor",
                timeout=10
            )
        except Exception as e:
            logger.error(f"Error sending desktop notification: {e}")
    
    def _play_alert_sound(self):
        """Play alert sound."""
        try:
            # Play system beep (Windows)
            frequency = 1000  # Hz
            duration = 500  # ms
            winsound.Beep(frequency, duration)
        except Exception as e:
            logger.error(f"Error playing alert sound: {e}")
    
    def send_custom_alert(self, title: str, message: str, play_sound: bool = True):
        """
        Send custom alert.
        
        Args:
            title: Alert title
            message: Alert message
            play_sound: Whether to play sound
        """
        if not self.enabled:
            return
        
        if self.notification_enabled:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Employee Monitor",
                    timeout=10
                )
            except Exception as e:
                logger.error(f"Error sending custom notification: {e}")
        
        if play_sound and self.sound_enabled:
            self._play_alert_sound()
    
    def clear_employee_alerts(self, employee_id: str):
        """Clear recent alerts for employee."""
        with self.lock:
            if employee_id in self.recent_alerts:
                del self.recent_alerts[employee_id]
    
    def get_alert_status(self) -> Dict[str, any]:
        """Get current alert system status."""
        with self.lock:
            return {
                'enabled': self.enabled,
                'sound_enabled': self.sound_enabled,
                'notification_enabled': self.notification_enabled,
                'repeat_interval': self.repeat_interval,
                'recent_alerts_count': len(self.recent_alerts)
            }
    
    def update_settings(self, **kwargs):
        """Update alert settings."""
        if 'enabled' in kwargs:
            self.enabled = kwargs['enabled']
        if 'sound_enabled' in kwargs:
            self.sound_enabled = kwargs['sound_enabled']
        if 'notification_enabled' in kwargs:
            self.notification_enabled = kwargs['notification_enabled']
        if 'repeat_interval' in kwargs:
            self.repeat_interval = kwargs['repeat_interval']
        
        logger.info("Alert settings updated")
