"""
Academic Progress Tracker - Data Management System
Handles all data persistence, logging, and backup operations
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging


class DataSaver:
    """Enhanced data management system with logging and backup functionality"""

    # Configuration
    DATA_DIR = "academic_data"
    USER_FILE = "user_data.json"
    LOGS_DIR = "logs"
    BACKUPS_DIR = "backups"

    def __init__(self):
        self.setup_directories()
        self.setup_logging()

    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            self.DATA_DIR,
            os.path.join(self.DATA_DIR, self.LOGS_DIR),
            os.path.join(self.DATA_DIR, self.BACKUPS_DIR)
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.join(self.DATA_DIR, self.LOGS_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Setup file handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Configure logger
        self.logger = logging.getLogger('AcademicTracker')
        self.logger.setLevel(logging.INFO)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info("=" * 60)
        self.logger.info("🚀 Academic Progress Tracker Started")
        self.logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"👤 User: user")
        self.logger.info("=" * 60)

    def get_user_file_path(self) -> str:
        """Get full path to user data file"""
        return os.path.join(self.DATA_DIR, self.USER_FILE)

    def save_user_data(self, user_data: Dict[str, Any]) -> bool:
        """Save user data with logging and backup"""
        try:
            file_path = self.get_user_file_path()

            # Create backup before saving
            if os.path.exists(file_path):
                self.create_backup()

            # Save data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)

            # Log success
            user_name = user_data.get('name', 'Unknown')
            subjects_count = len(user_data.get('subjects', []))

            self.logger.info(f"💾 User data saved successfully")
            self.logger.info(f"   👤 User: {user_name}")
            self.logger.info(f"   📚 Subjects: {subjects_count}")
            self.logger.info(f"   📁 File: {file_path}")

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to save user data: {e}")
            return False

    def load_user_data(self) -> Optional[Dict[str, Any]]:
        """Load user data with logging"""
        try:
            file_path = self.get_user_file_path()

            if not os.path.exists(file_path):
                self.logger.info("📝 No existing user data found - new user")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)

            # Log success
            user_name = user_data.get('name', 'Unknown')
            subjects_count = len(user_data.get('subjects', []))

            self.logger.info(f"📂 User data loaded successfully")
            self.logger.info(f"   👤 User: {user_name}")
            self.logger.info(f"   📚 Subjects: {subjects_count}")

            return user_data

        except Exception as e:
            self.logger.error(f"❌ Failed to load user data: {e}")
            return None

    def create_backup(self) -> bool:
        """Create a backup of current user data"""
        try:
            source_file = self.get_user_file_path()
            if not os.path.exists(source_file):
                return False

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"user_data_backup_{timestamp}.json"
            backup_path = os.path.join(self.DATA_DIR, self.BACKUPS_DIR, backup_filename)

            shutil.copy2(source_file, backup_path)

            self.logger.info(f"💾 Backup created: {backup_filename}")

            # Clean old backups (keep last 10)
            self.cleanup_old_backups()

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to create backup: {e}")
            return False

    def cleanup_old_backups(self, keep_count: int = 10):
        """Remove old backup files, keeping only the most recent ones"""
        try:
            backup_dir = os.path.join(self.DATA_DIR, self.BACKUPS_DIR)
            backup_files = []

            for filename in os.listdir(backup_dir):
                if filename.startswith("user_data_backup_") and filename.endswith(".json"):
                    file_path = os.path.join(backup_dir, filename)
                    backup_files.append((file_path, os.path.getctime(file_path)))

            # Sort by creation time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)

            # Remove old backups
            for file_path, _ in backup_files[keep_count:]:
                os.remove(file_path)
                self.logger.info(f"🗑️ Removed old backup: {os.path.basename(file_path)}")

        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup old backups: {e}")

    def log_user_action(self, action: str, details: str = ""):
        """Log user actions"""
        message = f"👤 User Action: {action}"
        if details:
            message += f" - {details}"
        self.logger.info(message)

    def log_subject_action(self, action: str, subject_name: str, details: str = ""):
        """Log subject-related actions"""
        message = f"📚 Subject {action}: {subject_name}"
        if details:
            message += f" - {details}"
        self.logger.info(message)

    def log_grade_action(self, action: str, subject_name: str, component: str, score: float = None,
                         total: float = None):
        """Log grade-related actions"""
        message = f"📝 Grade {action}: {subject_name} - {component}"
        if score is not None and total is not None:
            message += f" ({score}/{total} = {(score / total) * 100:.1f}%)"
        self.logger.info(message)

    def log_app_event(self, event: str, details: str = ""):
        """Log application events"""
        message = f"🎯 App Event: {event}"
        if details:
            message += f" - {details}"
        self.logger.info(message)

    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of data directory"""
        try:
            summary = {
                'data_directory': self.DATA_DIR,
                'user_file_exists': os.path.exists(self.get_user_file_path()),
                'user_file_size': 0,
                'backup_count': 0,
                'log_files': [],
                'last_modified': None
            }

            # User file info
            user_file = self.get_user_file_path()
            if os.path.exists(user_file):
                summary['user_file_size'] = os.path.getsize(user_file)
                summary['last_modified'] = datetime.fromtimestamp(
                    os.path.getmtime(user_file)
                ).strftime('%Y-%m-%d %H:%M:%S')

            # Backup count
            backup_dir = os.path.join(self.DATA_DIR, self.BACKUPS_DIR)
            if os.path.exists(backup_dir):
                backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
                summary['backup_count'] = len(backup_files)

            # Log files
            logs_dir = os.path.join(self.DATA_DIR, self.LOGS_DIR)
            if os.path.exists(logs_dir):
                log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
                summary['log_files'] = log_files

            return summary

        except Exception as e:
            self.logger.error(f"❌ Failed to get data summary: {e}")
            return {}

    def export_data(self, export_path: str) -> bool:
        """Export all data to a specified location"""
        try:
            # Create export directory
            export_dir = os.path.join(export_path, f"academic_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(export_dir, exist_ok=True)

            # Copy all data
            if os.path.exists(self.DATA_DIR):
                shutil.copytree(self.DATA_DIR, os.path.join(export_dir, "data"), dirs_exist_ok=True)

            self.logger.info(f"📤 Data exported to: {export_dir}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to export data: {e}")
            return False

    def print_data_report(self):
        """Print a comprehensive data report"""
        summary = self.get_data_summary()

        print("\n" + "=" * 60)
        print("📊 ACADEMIC DATA REPORT")
        print("=" * 60)
        print(f"📁 Data Directory: {summary.get('data_directory', 'Unknown')}")
        print(f"💾 User File Exists: {'✅' if summary.get('user_file_exists') else '❌'}")

        if summary.get('user_file_size'):
            print(f"📄 User File Size: {summary['user_file_size']} bytes")

        if summary.get('last_modified'):
            print(f"🕐 Last Modified: {summary['last_modified']}")

        print(f"💾 Backup Files: {summary.get('backup_count', 0)}")
        print(f"📝 Log Files: {len(summary.get('log_files', []))}")

        # Show recent log files
        log_files = summary.get('log_files', [])
        if log_files:
            print("\n📝 Recent Log Files:")
            for log_file in sorted(log_files)[-3:]:  # Show last 3
                print(f"   • {log_file}")

        print("=" * 60)


# Global data saver instance
data_saver = DataSaver()


def get_data_saver() -> DataSaver:
    """Get the global data saver instance"""
    return data_saver


# Convenience functions for easy importing
def save_user_data(user_data: Dict[str, Any]) -> bool:
    """Save user data"""
    return data_saver.save_user_data(user_data)


def load_user_data() -> Optional[Dict[str, Any]]:
    """Load user data"""
    return data_saver.load_user_data()


def log_action(action: str, details: str = ""):
    """Log a user action"""
    data_saver.log_user_action(action, details)


def log_subject(action: str, subject_name: str, details: str = ""):
    """Log a subject action"""
    data_saver.log_subject_action(action, subject_name, details)


def log_grade(action: str, subject_name: str, component: str, score: float = None, total: float = None):
    """Log a grade action"""
    data_saver.log_grade_action(action, subject_name, component, score, total)


def log_app(event: str, details: str = ""):
    """Log an app event"""
    data_saver.log_app_event(event, details)


if __name__ == "__main__":
    # Demo the data saver
    print("🚀 Data Saver Demo")

    # Create sample data
    sample_data = {
        'name': 'user',
        'created_date': datetime.now().isoformat(),
        'subjects': [
            {
                'id': '1',
                'name': 'Mathematics',
                'components': [
                    {
                        'name': 'Performance Tasks',
                        'weight': 40.0,
                        'grades': []
                    }
                ]
            }
        ]
    }

    # Test save and load
    print("💾 Testing save...")
    save_user_data(sample_data)

    print("📂 Testing load...")
    loaded_data = load_user_data()

    print("📊 Testing report...")
    data_saver.print_data_report()

    print("✅ Data saver demo complete!")