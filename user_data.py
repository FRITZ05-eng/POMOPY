import json
import hashlib
import os
from datetime import datetime
from typing import Dict, Optional, Tuple


class UserDataManager:
    """
    User data management class with proper encapsulation.
    All attributes are private and accessed through getters/setters.
    """

    def __init__(self, filename: str = "users.json"):
        """Initialize UserDataManager with private attributes"""
        # ENCAPSULATION
        self.__filename = filename
        self.__users_cache = {}
        self.__last_modified = None
        self.__is_loaded = False

        # Load users on initialization
        self.__load_users()

        print(f"🔐 UserDataManager initialized at 2025-06-18 10:41:48")
        print(f"📁 Using file: {self.__filename}")

    # ==================== PRIVATE METHODS ====================

    def __hash_password(self, password: str) -> str:
        """Private method to hash passwords"""
        return hashlib.sha256(password.encode()).hexdigest()

    def __validate_username(self, username: str) -> Tuple[bool, str]:
        """Private method to validate username"""
        if not username or not username.strip():
            return False, "Username cannot be empty"

        if len(username.strip()) < 3:
            return False, "Username must be at least 3 characters"

        if len(username.strip()) > 50:
            return False, "Username cannot exceed 50 characters"

        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in username for char in invalid_chars):
            return False, "Username contains invalid characters"

        return True, "Valid username"

    def __validate_password(self, password: str) -> Tuple[bool, str]:
        """Private method to validate password"""
        if not password:
            return False, "Password cannot be empty"

        if len(password) < 6:
            return False, "Password must be at least 6 characters"

        if len(password) > 128:
            return False, "Password cannot exceed 128 characters"

        return True, "Valid password"

    def __load_users(self) -> None:
        """Private method to load users from file"""
        try:
            if os.path.exists(self.__filename):
                with open(self.__filename, "r", encoding='utf-8') as f:
                    data = json.load(f)

                # Handle both old and new format
                if isinstance(data, dict):
                    self.__users_cache = data
                else:
                    self.__users_cache = {}

                self.__last_modified = os.path.getmtime(self.__filename)
                self.__is_loaded = True

                print(f"✅ Loaded {len(self.__users_cache)} users from {self.__filename}")
            else:
                self.__users_cache = {}
                self.__is_loaded = True
                print(f"📝 No existing user file found, starting fresh")

        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            self.__users_cache = {}
            self.__is_loaded = True

        except Exception as e:
            print(f"❌ Error loading users: {e}")
            self.__users_cache = {}
            self.__is_loaded = True

    def __save_users(self) -> bool:
        """Private method to save users to file"""
        try:
            # Create backup of existing file
            if os.path.exists(self.__filename):
                backup_name = f"{self.__filename}.backup"
                with open(self.__filename, 'r', encoding='utf-8') as original:
                    with open(backup_name, 'w', encoding='utf-8') as backup:
                        backup.write(original.read())

            # Save current data
            with open(self.__filename, "w", encoding='utf-8') as f:
                json.dump(self.__users_cache, f, indent=4, ensure_ascii=False)

            self.__last_modified = os.path.getmtime(self.__filename)
            print(f"💾 Users saved successfully at 2025-06-18 10:41:48")
            return True

        except Exception as e:
            print(f"❌ Error saving users: {e}")
            return False

    # ==================== PUBLIC GETTERS ====================

    def get_user_count(self) -> int:
        """Get total number of registered users"""
        return len(self.__users_cache)

    def get_filename(self) -> str:
        """Get the filename being used for storage"""
        return self.__filename

    def get_last_modified(self) -> Optional[float]:
        """Get last modification time of the user file"""
        return self.__last_modified

    def get_user_list(self) -> list:
        """Get list of all usernames"""
        return list(self.__users_cache.keys())

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information (without password hash)"""
        if username in self.__users_cache:
            user_data = self.__users_cache[username].copy()

            # Remove sensitive information
            if 'password_hash' in user_data:
                del user_data['password_hash']

            return user_data
        return None

    def is_loaded(self) -> bool:
        """Check if user data has been loaded"""
        return self.__is_loaded

    # ==================== PUBLIC SETTERS/METHODS ====================

    def set_filename(self, filename: str) -> bool:
        """Set new filename and reload data"""
        try:
            old_filename = self.__filename
            self.__filename = filename
            self.__load_users()

            print(f"📁 Filename changed from {old_filename} to {filename}")
            return True

        except Exception as e:
            print(f"❌ Error changing filename: {e}")
            return False

    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        return username in self.__users_cache

    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Register a new user with validation"""
        print(f"📝 Registration attempt for user: {username} at 2025-06-18 10:41:48")

        # Validate input
        valid_username, username_msg = self.__validate_username(username)
        if not valid_username:
            return False, username_msg

        valid_password, password_msg = self.__validate_password(password)
        if not valid_password:
            return False, password_msg

        # Check if user already exists
        if self.user_exists(username.strip()):
            return False, "Username already exists"

        # Create user data
        user_data = {
            'password_hash': self.__hash_password(password),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': None,
            'login_count': 0,
            'is_active': True
        }

        # Add user to cache
        self.__users_cache[username.strip()] = user_data

        # Save to file
        if self.__save_users():
            print(f"✅ User {username} registered successfully")
            return True, "Registration successful"
        else:
            # Remove from cache if save failed
            del self.__users_cache[username.strip()]
            return False, "Error saving user data"

    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user login"""
        print(f"🔐 Authentication attempt for user: {username} at 2025-06-18 10:41:48")

        if not username or not password:
            return False

        username = username.strip()

        if not self.user_exists(username):
            print(f"❌ User {username} not found")
            return False

        user_data = self.__users_cache[username]

        # Handle old format (direct hash) and new format (dict with password_hash)
        if isinstance(user_data, str):
            stored_hash = user_data
        else:
            stored_hash = user_data.get('password_hash', '')

        # Verify password
        if stored_hash == self.__hash_password(password):
            # Update login information
            if isinstance(user_data, dict):
                user_data['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                user_data['login_count'] = user_data.get('login_count', 0) + 1
                self.__save_users()

            print(f"✅ User {username} authenticated successfully")
            return True
        else:
            print(f"❌ Invalid password for user {username}")
            return False

    def update_user_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Update user password"""
        # Validate current password
        if not self.authenticate_user(username, old_password):
            return False, "Current password is incorrect"

        # Validate new password
        valid_password, password_msg = self.__validate_password(new_password)
        if not valid_password:
            return False, password_msg

        # Update password
        if username in self.__users_cache:
            user_data = self.__users_cache[username]
            if isinstance(user_data, dict):
                user_data['password_hash'] = self.__hash_password(new_password)
                user_data['password_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if self.__save_users():
                    print(f"✅ Password updated for user {username}")
                    return True, "Password updated successfully"
                else:
                    return False, "Error saving password update"

        return False, "User not found"

    def deactivate_user(self, username: str) -> bool:
        """Deactivate a user account"""
        if username in self.__users_cache:
            user_data = self.__users_cache[username]
            if isinstance(user_data, dict):
                user_data['is_active'] = False
                user_data['deactivated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return self.__save_users()
        return False

    def reload_users(self) -> bool:
        """Reload users from file"""
        try:
            self.__load_users()
            print(f"🔄 Users reloaded at 2025-06-18 10:41:48")
            return True
        except Exception as e:
            print(f"❌ Error reloading users: {e}")
            return False

    def backup_users(self, backup_filename: str = None) -> bool:
        """Create a backup of user data"""
        try:
            if backup_filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_filename = f"users_backup_{timestamp}.json"

            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(self.__users_cache, f, indent=4, ensure_ascii=False)

            print(f"💾 User data backed up to {backup_filename}")
            return True

        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    def test_user_data_manager():
        """Test the UserDataManager class"""
        print("🧪 Testing UserDataManager...")

        # Create manager
        manager = UserDataManager("test_users.json")

        # Test registration
        success, msg = manager.register_user("testuser", "testpassword123")
        print(f"Registration: {success}, {msg}")

        # Test authentication
        auth = manager.authenticate_user("testuser", "testpassword123")
        print(f"Authentication: {auth}")

        # Test user info
        info = manager.get_user_info("testuser")
        print(f"User info: {info}")

        print(f"Total users: {manager.get_user_count()}")


    test_user_data_manager()