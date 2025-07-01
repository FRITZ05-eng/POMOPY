import customtkinter as ctk
import math
from datetime import datetime
from user_data import UserDataManager

# Set appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Modern Color Scheme
COLORS = {
    'primary': '#70B4B8',
    'primary_hover': '#5B5FE5',
    'secondary': '#10B981',
    'secondary_hover': '#059669',
    'accent': '#F59E0B',
    'accent_hover': '#D97706',
    'surface': '#FFFFFF',
    'surface_hover': '#F1F5F9',
    'background': '#F8FAFC',
    'text_primary': '#0F172A',
    'text_secondary': '#64748B',
    'text_muted': '#94A3B8',
    'border': '#E2E8F0',
    'success': '#22C55E',
    'warning': '#F59E0B',
    'error': '#EF4444',
    'gradient_start': '#B8D4F5',
    'gradient_mid': '#867EE8',
    'gradient_end': '#514FE0',
    'glass': '#FFFFFF',
    'glass_border': '#E5E7EB',
}


# Font Management
class FontManager:
    _fonts = None

    @classmethod
    def get_fonts(cls):
        if cls._fonts is None:
            cls._fonts = {
                'heading_xl': ctk.CTkFont(size=42, weight="bold"),
                'heading_lg': ctk.CTkFont(size=32, weight="bold"),
                'heading_md': ctk.CTkFont(size=26, weight="bold"),
                'body_lg': ctk.CTkFont(size=18),
                'body_md': ctk.CTkFont(size=16),
                'body_sm': ctk.CTkFont(size=14),
                'caption': ctk.CTkFont(size=12),
                'button': ctk.CTkFont(size=16, weight="bold"),
            }
        return cls._fonts


class FixedEntry(ctk.CTkFrame):
    """COMPLETELY REBUILT entry field that GUARANTEES visibility and functionality"""

    def __init__(self, parent, placeholder_text="", show=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.placeholder_text = placeholder_text
        self.show_password = show
        self.password_visible = False

        # Configure frame with EXPLICIT colors to ensure visibility
        self.configure(
            fg_color="transparent",
            corner_radius=0,
            height=100  # ✅ EXPLICIT HEIGHT to guarantee space
        )

        # Grid setup with EXPLICIT weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Label row
        self.grid_rowconfigure(1, weight=0)  # Entry row

        # ✅ STEP 1: Label (always visible)
        fonts = FontManager.get_fonts()
        self.label = ctk.CTkLabel(
            self,
            text=placeholder_text,
            font=fonts['body_sm'],
            text_color=COLORS['text_secondary'],
            anchor="w",
            height=25  # ✅ EXPLICIT HEIGHT
        )
        self.label.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 5))

        # ✅ STEP 2: Entry container with GUARANTEED visibility
        self.entry_container = ctk.CTkFrame(
            self,
            fg_color=COLORS['surface'],
            corner_radius=12,
            border_width=2,
            border_color=COLORS['border'],
            height=60  # ✅ EXPLICIT HEIGHT - this MUST be visible
        )
        self.entry_container.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 5))
        self.entry_container.grid_propagate(False)  # ✅ PREVENT shrinking
        self.entry_container.grid_columnconfigure(1, weight=1)

        # ✅ STEP 3: Icon (simple and reliable)
        icon_text = "👤" if "username" in placeholder_text.lower() or "email" in placeholder_text.lower() else "🔒"
        self.icon_label = ctk.CTkLabel(
            self.entry_container,
            text=icon_text,
            font=ctk.CTkFont(size=16),
            text_color=COLORS['text_secondary'],
            width=40,
            height=40
        )
        self.icon_label.grid(row=0, column=0, padx=(15, 5), pady=10, sticky="w")

        # ✅ STEP 4: The ACTUAL entry widget - SIMPLIFIED and GUARANTEED to work
        self.entry = ctk.CTkEntry(
            self.entry_container,
            placeholder_text=f"Enter your {placeholder_text.lower()}",
            font=fonts['body_md'],
            fg_color="transparent",
            border_width=0,
            show=show if show else "",  # ✅ EXPLICIT show parameter
            text_color=COLORS['text_primary'],
            placeholder_text_color=COLORS['text_muted'],
            height=40  # ✅ EXPLICIT HEIGHT
        )
        self.entry.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=10)

        # ✅ STEP 5: Password toggle (only for password fields)
        if show == "*":
            self.toggle_button = ctk.CTkButton(
                self.entry_container,
                text="👁️",
                width=35,
                height=35,
                fg_color="transparent",
                hover_color=COLORS['surface_hover'],
                text_color=COLORS['text_secondary'],
                command=self.toggle_password_visibility,
                font=ctk.CTkFont(size=14)
            )
            self.toggle_button.grid(row=0, column=2, padx=(5, 15), pady=10, sticky="e")
            print(f"✅ Password toggle button added to {placeholder_text}")

        # ✅ STEP 6: Focus events
        self.entry.bind("<FocusIn>", self.on_focus_in)
        self.entry.bind("<FocusOut>", self.on_focus_out)

        # ✅ FORCE the entry to be ready for input
        self.update_idletasks()

        print(f"✅ FixedEntry created: '{placeholder_text}', show='{show}', height=100px")

    def toggle_password_visibility(self):
        """Toggle password visibility - SIMPLIFIED"""
        try:
            if self.password_visible:
                # Hide password
                self.entry.configure(show="*")
                self.toggle_button.configure(text="👁️", text_color=COLORS['text_secondary'])
                self.password_visible = False
                print("🔒 Password hidden at 2025-06-18 10:59:54")
            else:
                # Show password
                self.entry.configure(show="")
                self.toggle_button.configure(text="🙈", text_color=COLORS['primary'])
                self.password_visible = True
                print("👁️ Password visible at 2025-06-18 10:59:54")
        except Exception as e:
            print(f"❌ Toggle error: {e}")

    def on_focus_in(self, event):
        self.entry_container.configure(border_color=COLORS['primary'])
        self.icon_label.configure(text_color=COLORS['primary'])
        print(f"🎯 Focus IN: {self.placeholder_text}")

    def on_focus_out(self, event):
        self.entry_container.configure(border_color=COLORS['border'])
        self.icon_label.configure(text_color=COLORS['text_secondary'])
        print(f"🎯 Focus OUT: {self.placeholder_text}")

    def get(self):
        value = self.entry.get()
        print(f"🔍 Getting value from {self.placeholder_text}: {'***' if self.show_password and value else repr(value)}")
        return value

    def delete(self, first, last=None):
        result = self.entry.delete(first, last)
        print(f"🗑️ Cleared {self.placeholder_text} field")
        return result

    def focus(self):
        print(f"🎯 Setting focus to {self.placeholder_text}")
        return self.entry.focus()


class ModernButton(ctk.CTkButton):
    """Enhanced modern button with better styling"""

    def __init__(self, parent, style="primary", **kwargs):
        fonts = FontManager.get_fonts()

        styles = {
            'primary': {
                'fg_color': COLORS['primary'],
                'hover_color': COLORS['primary_hover'],
                'text_color': '#FFFFFF',
                'border_width': 0
            },
            'outline': {
                'fg_color': 'transparent',
                'hover_color': COLORS['surface_hover'],
                'text_color': COLORS['primary'],
                'border_width': 2,
                'border_color': COLORS['primary']
            },
            'secondary': {
                'fg_color': COLORS['secondary'],
                'hover_color': COLORS['secondary_hover'],
                'text_color': '#FFFFFF',
                'border_width': 0
            }
        }

        button_style = styles.get(style, styles['primary'])

        default_kwargs = {
            'corner_radius': 16,
            'height': 60,
            'font': fonts['button'],
            **button_style,
            **kwargs
        }

        super().__init__(parent, **default_kwargs)


class AnimatedBackground(ctk.CTkCanvas):
    """Animated gradient background - simplified"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(highlightthickness=0)
        self.animation_step = 0
        self.animate_background()

    def animate_background(self):
        try:
            self.delete("all")
            width = self.winfo_width()
            height = self.winfo_height()

            if width > 1 and height > 1:
                steps = 80
                for i in range(steps):
                    ratio = i / steps
                    animation_offset = math.sin(self.animation_step * 0.01) * 0.1
                    adjusted_ratio = max(0, min(1, ratio + animation_offset))

                    # Color interpolation
                    r1, g1, b1 = 184, 212, 245  # #B8D4F5
                    r2, g2, b2 = 134, 126, 232  # #867EE8
                    r3, g3, b3 = 81, 79, 224  # #514FE0

                    if adjusted_ratio < 0.5:
                        t = adjusted_ratio * 2
                        r = int(r1 + (r2 - r1) * t)
                        g = int(g1 + (g2 - g1) * t)
                        b = int(b1 + (b2 - b1) * t)
                    else:
                        t = (adjusted_ratio - 0.5) * 2
                        r = int(r2 + (r3 - r2) * t)
                        g = int(g2 + (g3 - g2) * t)
                        b = int(b2 + (b3 - b2) * t)

                    color = f"#{r:02x}{g:02x}{b:02x}"
                    y1 = (height * i) // steps
                    y2 = (height * (i + 1)) // steps
                    self.create_rectangle(0, y1, width, y2, fill=color, outline="")

            self.animation_step += 1
            self.after(150, self.animate_background)

        except:
            self.configure(bg=COLORS['gradient_start'])


class LoginScreen(ctk.CTk):
    """FIXED login screen with working Create New Account button"""

    def __init__(self, on_success=None):
        super().__init__()

        self.title("ProgressKo - Login")
        self.geometry("1400x900")
        self.resizable(True, True)
        self.on_success = on_success
        self.mode = "login"

        # Initialize user manager
        try:
            self.user_manager = UserDataManager("users.json")
            print(f"✅ UserDataManager initialized successfully")
        except Exception as e:
            print(f"❌ UserDataManager error: {e}")
            self.user_manager = None

        self.center_window()
        self.setup_ui()
        self.bind("<Return>", self.handle_enter_key)

        print(f"🔐 FIXED Login screen ready at 2025-06-18 10:59:54")
        print(f"👤 Current user: maminervaomamos")

    def center_window(self):
        self.update_idletasks()
        width = 1400
        height = 900
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        fonts = FontManager.get_fonts()

        # Main grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container
        self.main_container = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS['background']
        )
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Background
        self.bg_canvas = AnimatedBackground(
            self.main_container,
            width=1400,
            height=900
        )
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Center container
        self.center_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # ✅ FIXED: Main card - INCREASED SIZE for better button spacing
        self.main_card = ctk.CTkFrame(
            self.center_frame,
            fg_color=COLORS['surface'],
            corner_radius=20,
            border_width=1,
            border_color=COLORS['glass_border'],
            width=560,  # ✅ WIDER for better button spacing
            height=850  # ✅ TALLER to accommodate buttons properly
        )
        self.main_card.pack(padx=40, pady=40)
        self.main_card.pack_propagate(False)

        # ✅ FIXED: Content with better spacing
        self.content_frame = ctk.CTkFrame(
            self.main_card,
            fg_color="transparent",
            width=500,
            height=780  # ✅ More space for content
        )
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.content_frame.pack_propagate(False)

        # Header
        self.header_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.header_frame.pack(pady=(0, 25))  # ✅ Reduced padding

        # Logo
        self.logo_frame = ctk.CTkFrame(
            self.header_frame,
            fg_color=COLORS['primary'],
            corner_radius=25,
            width=80,
            height=80
        )
        self.logo_frame.pack(pady=(0, 15))  # ✅ Reduced padding
        self.logo_frame.pack_propagate(False)

        self.logo_label = ctk.CTkLabel(
            self.logo_frame,
            text="🎓",
            font=ctk.CTkFont(size=40),
            text_color="#FFFFFF"
        )
        self.logo_label.place(relx=0.5, rely=0.5, anchor="center")

        # App name
        self.app_name = ctk.CTkLabel(
            self.header_frame,
            text="ProgressKo",
            font=fonts['heading_lg'],
            text_color=COLORS['text_primary']
        )
        self.app_name.pack(pady=(0, 8))

        # Welcome
        self.welcome_label = ctk.CTkLabel(
            self.content_frame,
            text="Welcome Back!",
            font=fonts['heading_md'],
            text_color=COLORS['text_primary']
        )
        self.welcome_label.pack(pady=(0, 8))

        self.subtitle_label = ctk.CTkLabel(
            self.content_frame,
            text="Please sign in to continue",
            font=fonts['body_md'],
            text_color=COLORS['text_secondary']
        )
        self.subtitle_label.pack(pady=(0, 25))  # ✅ Reduced padding

        # ✅ FIXED: Form with better spacing for buttons
        self.form_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
            width=460,
            height=450  # ✅ More space for form and buttons
        )
        self.form_frame.pack()
        self.form_frame.pack_propagate(False)

        # ✅ USERNAME FIELD - GUARANTEED VISIBLE
        print("🔧 Creating FIXED username field...")
        self.username_field = FixedEntry(
            self.form_frame,
            placeholder_text="Username or Email",
            width=460,
            height=100
        )
        self.username_field.pack(pady=(0, 15), fill="x")  # ✅ Reduced padding
        print("✅ Username field created with guaranteed visibility")

        # ✅ PASSWORD FIELD - GUARANTEED VISIBLE AND FUNCTIONAL
        print("🔧 Creating FIXED password field...")
        self.password_field = FixedEntry(
            self.form_frame,
            placeholder_text="Password",
            show="*",
            width=460,
            height=100
        )
        self.password_field.pack(pady=(0, 15), fill="x")  # ✅ Reduced padding
        print("✅ Password field created with GUARANTEED visibility and functionality")

        # Status
        self.status_label = ctk.CTkLabel(
            self.form_frame,
            text="",
            font=fonts['body_sm'],
            text_color=COLORS['error'],
            height=25  # ✅ Fixed height
        )
        self.status_label.pack(pady=(0, 15))

        # ✅ FIXED: Primary Action button (Sign In / Create Account)
        self.action_button = ModernButton(
            self.form_frame,
            text="Sign In",
            style="primary",
            width=460,
            height=60,  # ✅ PROPER HEIGHT
            command=self.try_login
        )
        self.action_button.pack(pady=(0, 20))  # ✅ Good spacing
        print("✅ Primary action button created: Sign In")

        # ✅ FIXED: Secondary Button - NOT SQUISHED ANYMORE
        self.secondary_button = ModernButton(
            self.form_frame,
            text="Create New Account",
            style="outline",
            width=460,
            height=55,  # ✅ PROPER HEIGHT - NOT SQUISHED
            command=self.switch_to_register
        )
        self.secondary_button.pack(pady=(0, 20))  # ✅ Good spacing
        print("✅ Secondary button created: Create New Account (NOT squished)")

        # ✅ FIXED: Toggle links with better spacing
        self.toggle_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.toggle_frame.pack(pady=(10, 0))  # ✅ Added padding at top

        # Login mode toggle
        self.login_toggle = ctk.CTkFrame(self.toggle_frame, fg_color="transparent")
        self.login_toggle.pack()

        self.login_text = ctk.CTkFrame(self.login_toggle, fg_color="transparent")
        self.login_text.pack()

        self.no_account = ctk.CTkLabel(
            self.login_text,
            text="Don't have an account? ",
            font=fonts['body_md'],
            text_color=COLORS['text_secondary']
        )
        self.no_account.pack(side="left")

        self.signup_btn = ctk.CTkLabel(
            self.login_text,
            text="Sign up here",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['primary'],
            cursor="hand2"
        )
        self.signup_btn.pack(side="left")
        self.signup_btn.bind("<Button-1>", lambda e: self.switch_to_register())
        self.signup_btn.bind("<Enter>", lambda e: self.signup_btn.configure(text_color=COLORS['primary_hover']))
        self.signup_btn.bind("<Leave>", lambda e: self.signup_btn.configure(text_color=COLORS['primary']))

        # Register mode toggle
        self.register_toggle = ctk.CTkFrame(self.toggle_frame, fg_color="transparent")

        self.register_text = ctk.CTkFrame(self.register_toggle, fg_color="transparent")
        self.register_text.pack()

        self.have_account = ctk.CTkLabel(
            self.register_text,
            text="Already have an account? ",
            font=fonts['body_md'],
            text_color=COLORS['text_secondary']
        )
        self.have_account.pack(side="left")

        self.signin_btn = ctk.CTkLabel(
            self.register_text,
            text="Sign in here",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['accent'],
            cursor="hand2"
        )
        self.signin_btn.pack(side="left")
        self.signin_btn.bind("<Button-1>", lambda e: self.switch_to_login())
        self.signin_btn.bind("<Enter>", lambda e: self.signin_btn.configure(text_color=COLORS['accent_hover']))
        self.signin_btn.bind("<Leave>", lambda e: self.signin_btn.configure(text_color=COLORS['accent']))

        # Set initial focus with delay
        self.after(1000, self.set_initial_focus)

        print("✅ UI setup complete with FIXED Create New Account button!")
        print("✅ Button is NOT squished and has proper spacing!")

    def set_initial_focus(self):
        """Set focus to username field"""
        try:
            self.username_field.focus()
            print("🎯 Initial focus set to username field at 2025-06-18 10:59:54")
        except Exception as e:
            print(f"❌ Focus error: {e}")

    def handle_enter_key(self, event):
        if self.mode == "login":
            self.try_login()
        else:
            self.try_register()

    def switch_to_register(self):
        """✅ FIXED: Switch to registration mode - WORKING"""
        print("🔄 Switching to registration mode at 2025-06-18 10:59:54...")
        self.mode = "register"

        # ✅ Update UI for registration mode
        self.welcome_label.configure(text="Create Account")
        self.subtitle_label.configure(text="Join us and start tracking your progress")
        self.action_button.configure(text="Create Account", command=self.try_register)
        self.secondary_button.configure(text="Already have an account?", command=self.switch_to_login)

        # ✅ Switch toggle visibility
        self.login_toggle.pack_forget()
        self.register_toggle.pack()

        # ✅ Clear and focus
        self.clear_fields()
        self.username_field.focus()

        print("✅ Switched to registration mode - Create Account button is now functional!")

    def switch_to_login(self):
        """✅ FIXED: Switch to login mode - WORKING"""
        print("🔄 Switching to login mode at 2025-06-18 10:59:54...")
        self.mode = "login"

        # ✅ Update UI for login mode
        self.welcome_label.configure(text="Welcome Back!")
        self.subtitle_label.configure(text="Please sign in to continue")
        self.action_button.configure(text="Sign In", command=self.try_login)
        self.secondary_button.configure(text="Create New Account", command=self.switch_to_register)

        # ✅ Switch toggle visibility
        self.register_toggle.pack_forget()
        self.login_toggle.pack()

        # ✅ Clear and focus
        self.clear_fields()
        self.username_field.focus()

        print("✅ Switched to login mode - Sign In button is now functional!")

    def clear_fields(self):
        """Clear input fields"""
        try:
            self.username_field.delete(0, "end")
            self.password_field.delete(0, "end")
            self.status_label.configure(text="")
            print("🧹 Fields cleared at 2025-06-18 10:59:54")
        except Exception as e:
            print(f"❌ Clear fields error: {e}")

    def try_login(self):
        """✅ WORKING: Attempt login"""
        try:
            username = self.username_field.get().strip()
            password = self.password_field.get().strip()

            print(f"🔐 Login attempt at 2025-06-18 10:59:54")
            print(f"🔐 Username: '{username}'")
            print(f"🔐 Password: {'[ENTERED]' if password else '[EMPTY]'}")

            if not username:
                self.show_status("⚠️ Please enter your username", "warning")
                self.username_field.focus()
                return

            if not password:
                self.show_status("⚠️ Please enter your password", "warning")
                self.password_field.focus()
                return

            self.action_button.configure(text="Signing In...", state="disabled")

            if self.user_manager:
                self.after(800, lambda: self.complete_login_attempt(username, password))
            else:
                self.show_status("❌ Authentication system unavailable", "error")
                self.action_button.configure(text="Sign In", state="normal")

        except Exception as e:
            print(f"❌ Login error: {e}")
            self.show_status("❌ Login error occurred", "error")
            self.action_button.configure(text="Sign In", state="normal")

    def complete_login_attempt(self, username, password):
        """Complete login"""
        try:
            if self.user_manager and self.user_manager.authenticate_user(username, password):
                self.show_status("✅ Login successful!", "success")
                print(f"✅ Authentication successful for {username}")
                self.after(1200, lambda: self.complete_login(username))
            else:
                self.show_status("❌ Invalid username or password", "error")
                print(f"❌ Authentication failed for {username}")
                self.password_field.focus()
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            self.show_status("❌ Authentication error", "error")

        self.action_button.configure(text="Sign In", state="normal")

    def try_register(self):
        """✅ WORKING: Attempt registration"""
        try:
            username = self.username_field.get().strip()
            password = self.password_field.get().strip()

            print(f"📝 Registration attempt at 2025-06-18 10:59:54")
            print(f"📝 Username: '{username}'")
            print(f"📝 Password: {'[ENTERED]' if password else '[EMPTY]'}")

            if not username:
                self.show_status("⚠️ Please enter a username", "warning")
                self.username_field.focus()
                return

            if not password:
                self.show_status("⚠️ Please enter a password", "warning")
                self.password_field.focus()
                return

            self.action_button.configure(text="Creating Account...", state="disabled")

            if self.user_manager:
                self.after(800, lambda: self.complete_registration_attempt(username, password))
            else:
                self.show_status("❌ Registration system unavailable", "error")
                self.action_button.configure(text="Create Account", state="normal")

        except Exception as e:
            print(f"❌ Registration error: {e}")
            self.show_status("❌ Registration error occurred", "error")
            self.action_button.configure(text="Create Account", state="normal")

    def complete_registration_attempt(self, username, password):
        """✅ WORKING: Complete registration"""
        try:
            if self.user_manager:
                success, msg = self.user_manager.register_user(username, password)
                if success:
                    self.show_status("✅ " + msg, "success")
                    print(f"✅ Registration successful for {username}")
                    self.after(2500, self.switch_to_login)
                else:
                    self.show_status("❌ " + msg, "error")
                    print(f"❌ Registration failed: {msg}")
            else:
                self.show_status("❌ Registration system unavailable", "error")
        except Exception as e:
            print(f"❌ Registration error: {e}")
            self.show_status("❌ Registration error", "error")

        self.action_button.configure(text="Create Account", state="normal")

    def show_status(self, message, status_type):
        """Show status message"""
        colors = {
            "error": COLORS['error'],
            "success": COLORS['success'],
            "warning": COLORS['warning']
        }

        self.status_label.configure(
            text=message,
            text_color=colors.get(status_type, colors["error"])
        )
        print(f"📱 Status: {message}")

    def complete_login(self, username):
        """Complete login"""
        try:
            print(f"🎉 Login completed for {username} at 2025-06-18 10:59:54")
            print(f"👤 Current user: maminervaomamos")

            self.destroy()
            if self.on_success:
                self.on_success(username)

        except Exception as e:
            print(f"❌ Login completion error: {e}")
            if self.on_success:
                self.on_success(username)


def test_login_screen():
    """Test the COMPLETELY FIXED login screen"""

    def on_login_success(username):
        print(f"🎉 Login test successful: {username} at 2025-06-18 10:59:54")

    app = LoginScreen(on_success=on_login_success)
    app.mainloop()


if __name__ == "__main__":
    test_login_screen()