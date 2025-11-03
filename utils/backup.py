"""
Backup Utility
Creates backups of the database and configuration.
"""

import sys
import os
import shutil
from datetime import datetime


def create_backup(source_dir='.', backup_dir='backups'):
    """
    Create backup of database and configuration.
    
    Args:
        source_dir: Source directory
        backup_dir: Backup destination directory
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"Creating backup at: {backup_dir}")
    print(f"Timestamp: {timestamp}")
    print()
    
    files_backed_up = 0
    
    # Backup database
    db_path = os.path.join(source_dir, 'data', 'employees.db')
    if os.path.exists(db_path):
        backup_path = os.path.join(backup_dir, f'employees_{timestamp}.db')
        shutil.copy2(db_path, backup_path)
        size_mb = os.path.getsize(backup_path) / (1024 * 1024)
        print(f"✓ Database backed up: {backup_path} ({size_mb:.2f} MB)")
        files_backed_up += 1
    else:
        print("⚠ Database not found, skipping...")
    
    # Backup configuration
    config_path = os.path.join(source_dir, 'config.yaml')
    if os.path.exists(config_path):
        backup_path = os.path.join(backup_dir, f'config_{timestamp}.yaml')
        shutil.copy2(config_path, backup_path)
        print(f"✓ Configuration backed up: {backup_path}")
        files_backed_up += 1
    else:
        print("⚠ Configuration not found, skipping...")
    
    # Cleanup old backups (keep last 10)
    print()
    print("Cleaning up old backups...")
    cleanup_old_backups(backup_dir, keep=10)
    
    print()
    print(f"✓ Backup complete! ({files_backed_up} files backed up)")


def cleanup_old_backups(backup_dir, keep=10):
    """Remove old backups, keeping only the most recent ones."""
    if not os.path.exists(backup_dir):
        return
    
    # Get all backup files
    files = []
    for f in os.listdir(backup_dir):
        if f.endswith('.db') or f.endswith('.yaml'):
            full_path = os.path.join(backup_dir, f)
            files.append((full_path, os.path.getmtime(full_path)))
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: x[1], reverse=True)
    
    # Remove old files
    for file_path, _ in files[keep:]:
        try:
            os.remove(file_path)
            print(f"  Removed old backup: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"  Failed to remove {file_path}: {e}")


def restore_backup(backup_file, restore_dir='.'):
    """
    Restore from backup.
    
    Args:
        backup_file: Path to backup file
        restore_dir: Directory to restore to
    """
    if not os.path.exists(backup_file):
        print(f"✗ Backup file not found: {backup_file}")
        return False
    
    filename = os.path.basename(backup_file)
    
    # Determine destination
    if filename.endswith('.db'):
        dest_path = os.path.join(restore_dir, 'data', 'employees.db')
    elif filename.endswith('.yaml'):
        dest_path = os.path.join(restore_dir, 'config.yaml')
    else:
        print(f"✗ Unknown backup file type: {filename}")
        return False
    
    # Create backup of current file
    if os.path.exists(dest_path):
        current_backup = dest_path + '.before_restore'
        shutil.copy2(dest_path, current_backup)
        print(f"✓ Current file backed up to: {current_backup}")
    
    # Restore
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy2(backup_file, dest_path)
    print(f"✓ Restored: {dest_path}")
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup utility')
    parser.add_argument('--source', default='.', help='Source directory')
    parser.add_argument('--backup-dir', default='backups', help='Backup directory')
    parser.add_argument('--restore', help='Restore from backup file')
    
    args = parser.parse_args()
    
    if args.restore:
        restore_backup(args.restore, args.source)
    else:
        create_backup(args.source, args.backup_dir)
