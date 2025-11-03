// Employee Monitoring System - Frontend JavaScript

const API_BASE = 'http://localhost:5000/api';
let updateInterval = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    startAutoUpdate();
});

function initializeApp() {
    updateSystemStatus();
    loadCameras();
    loadAllEmployees();
    loadEmployeeStatus();
    loadAlerts();
    loadLogs();
}

function setupEventListeners() {
    // System toggle
    document.getElementById('toggle-system').addEventListener('click', toggleSystem);
    
    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            switchTab(tab);
        });
    });
    
    // Refresh logs
    document.getElementById('refresh-logs').addEventListener('click', loadLogs);
    
    // Refresh cameras
    document.getElementById('refresh-cameras').addEventListener('click', loadCameras);
    
    // Filter logs
    document.getElementById('filter-employee').addEventListener('input', loadLogs);
}

function startAutoUpdate() {
    // Update every 5 seconds
    updateInterval = setInterval(() => {
        updateSystemStatus();
        loadAllEmployees();
        loadEmployeeStatus();
        loadAlerts();
    }, 5000);
}

// System Control
async function toggleSystem() {
    const btn = document.getElementById('toggle-system');
    const isRunning = btn.textContent === 'Stop System';
    
    try {
        const endpoint = isRunning ? '/stop' : '/start';
        const response = await fetch(API_BASE + endpoint, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            setTimeout(updateSystemStatus, 500);
        }
    } catch (error) {
        console.error('Error toggling system:', error);
    }
}

async function updateSystemStatus() {
    try {
        const response = await fetch(API_BASE + '/status');
        const data = await response.json();
        
        if (data.success) {
            const status = data.data;
            
            // Update status badge
            const badge = document.getElementById('system-status');
            const btn = document.getElementById('toggle-system');
            
            if (status.running) {
                badge.textContent = 'System Online';
                badge.className = 'status-badge online';
                btn.textContent = 'Stop System';
                btn.className = 'btn btn-secondary';
            } else {
                badge.textContent = 'System Offline';
                badge.className = 'status-badge offline';
                btn.textContent = 'Start System';
                btn.className = 'btn btn-primary';
            }
            
            // Update dashboard stats
            document.getElementById('occupancy').textContent = status.employees.present;
            document.getElementById('camera-count').textContent = status.cameras.active;
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Camera Feeds
async function loadCameras() {
    try {
        const response = await fetch(API_BASE + '/cameras');
        const data = await response.json();
        
        if (data.success) {
            const grid = document.getElementById('camera-grid');
            grid.innerHTML = '';
            
            if (data.data.length === 0) {
                grid.innerHTML = '<div class="empty-state">No cameras configured</div>';
                return;
            }
            
            data.data.forEach(camera => {
                const cameraDiv = document.createElement('div');
                cameraDiv.className = 'camera-feed';
                cameraDiv.innerHTML = `
                    <div class="camera-header">
                        ${camera.name} (ID: ${camera.id})
                        <span style="float: right;">${camera.active ? '🟢 Active' : '🔴 Offline'}</span>
                    </div>
                    ${camera.active ? 
                        `<img class="camera-frame" src="${API_BASE}/cameras/${camera.id}/stream" alt="${camera.name}">` :
                        '<div class="empty-state">Camera offline</div>'
                    }
                `;
                grid.appendChild(cameraDiv);
            });
        }
    } catch (error) {
        console.error('Error loading cameras:', error);
    }
}

// All Employees
async function loadAllEmployees() {
    try {
        const response = await fetch(API_BASE + '/employees');
        const data = await response.json();
        
        if (data.success) {
            const allTable = document.getElementById('all-employees');
            if (!allTable) return; // Element might not exist yet
            
            allTable.innerHTML = '';
            
            if (data.data.length === 0) {
                allTable.innerHTML = '<tr><td colspan="5" class="empty-state">No employees registered</td></tr>';
                return;
            }
            
            data.data.forEach(emp => {
                const row = document.createElement('tr');
                const status = emp.active ? '<span class="status-indicator online">Active</span>' : '<span class="status-indicator offline">Inactive</span>';
                const created = new Date(emp.created_at).toLocaleString();
                
                row.innerHTML = `
                    <td>${emp.employee_id}</td>
                    <td>${emp.name}</td>
                    <td>${emp.department || 'N/A'}</td>
                    <td>${status}</td>
                    <td>${created}</td>
                `;
                allTable.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading all employees:', error);
    }
}

// Employee Status
async function loadEmployeeStatus() {
    try {
        const response = await fetch(API_BASE + '/employees/status');
        const data = await response.json();
        
        if (data.success) {
            const statuses = data.data;
            
            // Separate present and absent
            const present = statuses.filter(s => s.is_present);
            const absent = statuses.filter(s => s.absence_timer_started);
            
            // Update present employees
            const presentTable = document.getElementById('present-employees');
            presentTable.innerHTML = '';
            
            if (present.length === 0) {
                presentTable.innerHTML = '<tr><td colspan="4" class="empty-state">No employees present</td></tr>';
            } else {
                present.forEach(emp => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${emp.employee_id}</td>
                        <td>${formatDateTime(emp.entry_time)}</td>
                        <td>${formatDateTime(emp.last_seen)}</td>
                        <td>Camera ${emp.camera_id || 'N/A'}</td>
                    `;
                    presentTable.appendChild(row);
                });
            }
            
            // Update absent employees
            const absentTable = document.getElementById('absent-employees');
            absentTable.innerHTML = '';
            
            if (absent.length === 0) {
                absentTable.innerHTML = '<tr><td colspan="5" class="empty-state">No employees on absence timer</td></tr>';
            } else {
                absent.forEach(emp => {
                    const row = document.createElement('tr');
                    const timeoutRemaining = emp.timeout_remaining || 0;
                    const alertStatus = emp.alert_sent ? 
                        '<span class="status-indicator alert">Alert Sent</span>' : 
                        '<span class="status-indicator absent">Monitoring</span>';
                    
                    row.innerHTML = `
                        <td>${emp.employee_id}</td>
                        <td>${formatDateTime(emp.absence_start)}</td>
                        <td>${formatDuration(emp.absence_duration)}</td>
                        <td>${formatDuration(timeoutRemaining)}</td>
                        <td>${alertStatus}</td>
                    `;
                    absentTable.appendChild(row);
                });
            }
        }
    } catch (error) {
        console.error('Error loading employee status:', error);
    }
}

// Alerts
async function loadAlerts() {
    try {
        const response = await fetch(API_BASE + '/alerts?unacknowledged=true');
        const data = await response.json();
        
        if (data.success) {
            const alertsList = document.getElementById('alerts-list');
            const alertCount = document.getElementById('alert-count');
            
            alertCount.textContent = data.data.length;
            alertsList.innerHTML = '';
            
            if (data.data.length === 0) {
                alertsList.innerHTML = '<div class="empty-state">No unacknowledged alerts</div>';
                return;
            }
            
            data.data.forEach(alert => {
                const alertDiv = document.createElement('div');
                alertDiv.className = `alert-item ${alert.acknowledged ? 'acknowledged' : ''}`;
                alertDiv.innerHTML = `
                    <div class="alert-content">
                        <div class="alert-title">
                            ⚠️ Employee ${alert.employee_id} - Absent for ${Math.floor(alert.absence_duration_seconds / 60)} minutes
                        </div>
                        <div class="alert-time">${formatDateTime(alert.alert_time)}</div>
                    </div>
                    ${!alert.acknowledged ? 
                        `<button class="btn btn-success" onclick="acknowledgeAlert(${alert.id})">Acknowledge</button>` : 
                        '<span>✓ Acknowledged</span>'
                    }
                `;
                alertsList.appendChild(alertDiv);
            });
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

async function acknowledgeAlert(alertId) {
    try {
        const response = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            loadAlerts();
        }
    } catch (error) {
        console.error('Error acknowledging alert:', error);
    }
}

// Logs
async function loadLogs() {
    try {
        const employeeFilter = document.getElementById('filter-employee').value;
        let url = `${API_BASE}/logs?limit=50`;
        
        if (employeeFilter) {
            url += `&employee_id=${employeeFilter}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            const logsTable = document.getElementById('logs-table');
            logsTable.innerHTML = '';
            
            if (data.data.length === 0) {
                logsTable.innerHTML = '<tr><td colspan="5" class="empty-state">No logs found</td></tr>';
                return;
            }
            
            data.data.forEach(log => {
                const row = document.createElement('tr');
                const duration = log.duration_seconds ? formatDuration(log.duration_seconds) : 'Active';
                
                row.innerHTML = `
                    <td>${log.employee_id}</td>
                    <td>${formatDateTime(log.entry_time)}</td>
                    <td>${log.exit_time ? formatDateTime(log.exit_time) : 'Still present'}</td>
                    <td>${duration}</td>
                    <td>Camera ${log.camera_id || 'N/A'}</td>
                `;
                logsTable.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

// Tab Switching
function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });
    
    // Update panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

// Utility Functions
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

function formatDuration(seconds) {
    if (!seconds) return '0s';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}
