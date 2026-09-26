"""
Password Generator - Core Logic and Modern GUI
A secure, stylish, and beginner-friendly Python Password Generator.
"""

import string
import secrets
from typing import Tuple, List

try:
    import customtkinter as ctk
    import tkinter as tk
    USE_CUSTOMTKINTER = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USE_CUSTOMTKINTER = False

# Character sets
SAFE_SYMBOLS = "!@#$%^&*()-_=+[]{}?"


def calculate_strength(password: str, has_upper: bool, has_lower: bool, has_digits: bool, has_symbols: bool) -> Tuple[str, float, str]:
    """
    Calculate password strength rating, progress fraction (0.0 to 1.0), and color code.
    Returns: (label, score_ratio, hex_color)
    """
    if not password:
        return "Not generated", 0.0, "#64748B"

    length = len(password)
    categories_count = sum([has_upper, has_lower, has_digits, has_symbols])

    # Strength rules
    if categories_count <= 1 or length < 8:
        return "Weak", 0.25, "#EF4444"  # Red
    elif length < 12:
        return "Medium", 0.50, "#F59E0B"  # Orange/Amber
    elif length < 16 or categories_count < 3:
        return "Strong", 0.75, "#10B981"  # Emerald Green
    else:
        return "Very Strong", 1.00, "#06B6D4"  # Vibrant Cyan


def generate_password(
    length: int = 16,
    include_upper: bool = True,
    include_lower: bool = True,
    include_digits: bool = True,
    include_symbols: bool = False
) -> str:
    """
    Generate a cryptographically secure random password based on specified criteria.
    Guarantees at least one character from each selected category.
    """
    categories: List[str] = []
    guaranteed_chars: List[str] = []

    if include_upper:
        categories.append(string.ascii_uppercase)
        guaranteed_chars.append(secrets.choice(string.ascii_uppercase))
    if include_lower:
        categories.append(string.ascii_lowercase)
        guaranteed_chars.append(secrets.choice(string.ascii_lowercase))
    if include_digits:
        categories.append(string.digits)
        guaranteed_chars.append(secrets.choice(string.digits))
    if include_symbols:
        categories.append(SAFE_SYMBOLS)
        guaranteed_chars.append(secrets.choice(SAFE_SYMBOLS))

    if not categories:
        raise ValueError("Please select at least one character type.")

    if length < len(guaranteed_chars):
        length = len(guaranteed_chars)

    # Combined pool for remaining characters
    combined_pool = "".join(categories)
    remaining_count = length - len(guaranteed_chars)
    remaining_chars = [secrets.choice(combined_pool) for _ in range(remaining_count)]

    all_chars = guaranteed_chars + remaining_chars

    # Secure shuffle using Fisher-Yates algorithm powered by secrets.randbelow
    for i in range(len(all_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        all_chars[i], all_chars[j] = all_chars[j], all_chars[i]

    return "".join(all_chars)


class ModernPasswordGeneratorApp:
    """
    CustomTkinter-powered modern dark-themed Password Generator GUI.
    """
    def __init__(self, root: "ctk.CTk"):
        self.root = root
        self.root.title("Password Generator")
        
        # Center the compact window on desktop screen
        win_width, win_height = 500, 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        pos_x = max(0, (screen_width - win_width) // 2)
        pos_y = max(0, (screen_height - win_height) // 2)
        self.root.geometry(f"{win_width}x{win_height}+{pos_x}+{pos_y}")
        self.root.minsize(440, 640)

        # Set theme and appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Background color
        self.root.configure(fg_color="#0B0F19")

        # Variables
        self.length_var = ctk.IntVar(value=16)
        self.upper_var = ctk.BooleanVar(value=True)
        self.lower_var = ctk.BooleanVar(value=True)
        self.digits_var = ctk.BooleanVar(value=True)
        self.symbols_var = ctk.BooleanVar(value=False)
        self.current_password = ""
        self.copied_timer_id = None

        self._build_ui()

    def _build_ui(self):
        # Center Wrapper to ensure the application card never over-stretches on large displays
        self.center_wrapper = ctk.CTkFrame(self.root, fg_color="#0B0F19")
        self.center_wrapper.pack(expand=True, fill="both", padx=20, pady=20)

        # Main Outer Container (Centered Card, max comfortable desktop width)
        self.main_container = ctk.CTkFrame(
            self.center_wrapper,
            fg_color="#121826",
            corner_radius=20,
            border_width=1,
            border_color="#1E293B",
            width=480
        )
        self.main_container.pack(expand=True, fill="y", anchor="center")

        # 1. Header Title & Subtitle
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Password Generator",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#F8FAFC"
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Generate strong & secure random passwords",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94A3B8"
        )
        subtitle_label.pack(anchor="w")

        # 2. Password Display Card (Click to Copy)
        self.display_card = ctk.CTkFrame(
            self.main_container,
            fg_color="#1E293B",
            corner_radius=14,
            border_width=1,
            border_color="#334155",
            cursor="hand2"
        )
        self.display_card.pack(fill="x", padx=24, pady=10)
        self.display_card.bind("<Button-1>", lambda e: self.on_copy())

        # Top row inside display card: Password & Copy Button
        display_top_row = ctk.CTkFrame(self.display_card, fg_color="transparent")
        display_top_row.pack(fill="x", padx=16, pady=(14, 4))
        display_top_row.bind("<Button-1>", lambda e: self.on_copy())

        self.password_label = ctk.CTkLabel(
            display_top_row,
            text="Your password will appear here",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="normal"),
            text_color="#64748B",
            wraplength=300,
            justify="left"
        )
        self.password_label.pack(side="left", fill="x", expand=True, anchor="w")
        self.password_label.bind("<Button-1>", lambda e: self.on_copy())

        # Copy Action Icon / Button
        self.copy_btn = ctk.CTkButton(
            display_top_row,
            text="📋 Copy",
            width=70,
            height=32,
            corner_radius=8,
            fg_color="#334155",
            hover_color="#475569",
            text_color="#F8FAFC",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.on_copy
        )
        self.copy_btn.pack(side="right", padx=(8, 0))

        # Bottom row inside display card: Click to copy hint & Copied status
        display_bottom_row = ctk.CTkFrame(self.display_card, fg_color="transparent")
        display_bottom_row.pack(fill="x", padx=16, pady=(0, 12))
        display_bottom_row.bind("<Button-1>", lambda e: self.on_copy())

        self.copy_status_label = ctk.CTkLabel(
            display_bottom_row,
            text="Click to copy",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#64748B"
        )
        self.copy_status_label.pack(side="left")
        self.copy_status_label.bind("<Button-1>", lambda e: self.on_copy())

        # 3. Strength Indicator Card
        strength_frame = ctk.CTkFrame(self.main_container, fg_color="#161F33", corner_radius=12)
        strength_frame.pack(fill="x", padx=24, pady=(6, 12))

        strength_header_row = ctk.CTkFrame(strength_frame, fg_color="transparent")
        strength_header_row.pack(fill="x", padx=14, pady=(8, 4))

        strength_title = ctk.CTkLabel(
            strength_header_row,
            text="STRENGTH",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#94A3B8"
        )
        strength_title.pack(side="left")

        self.strength_value_label = ctk.CTkLabel(
            strength_header_row,
            text="Not generated",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#64748B"
        )
        self.strength_value_label.pack(side="right")

        self.strength_bar = ctk.CTkProgressBar(
            strength_frame,
            height=6,
            corner_radius=3,
            fg_color="#0F172A",
            progress_color="#64748B"
        )
        self.strength_bar.pack(fill="x", padx=14, pady=(0, 10))
        self.strength_bar.set(0.0)

        # 4. Length Slider Section
        length_section = ctk.CTkFrame(self.main_container, fg_color="transparent")
        length_section.pack(fill="x", padx=24, pady=6)

        length_header = ctk.CTkFrame(length_section, fg_color="transparent")
        length_header.pack(fill="x", pady=(0, 6))

        length_title_label = ctk.CTkLabel(
            length_header,
            text="LENGTH",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#94A3B8"
        )
        length_title_label.pack(side="left")

        self.length_val_display = ctk.CTkLabel(
            length_header,
            text="16",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#38BDF8"
        )
        self.length_val_display.pack(side="right")

        self.slider = ctk.CTkSlider(
            length_section,
            from_=4,
            to=32,
            number_of_steps=28,
            variable=self.length_var,
            command=self.on_slider_change,
            button_color="#6366F1",
            button_hover_color="#4F46E5",
            progress_color="#6366F1",
            fg_color="#1E293B"
        )
        self.slider.pack(fill="x")

        # 5. Settings Section (Checkboxes / Switches)
        settings_section = ctk.CTkFrame(
            self.main_container,
            fg_color="#161F33",
            corner_radius=12,
            border_width=1,
            border_color="#1E293B"
        )
        settings_section.pack(fill="x", padx=24, pady=12)

        settings_header = ctk.CTkLabel(
            settings_section,
            text="SETTINGS",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#64748B"
        )
        settings_header.pack(anchor="w", padx=14, pady=(10, 4))

        # Build setting toggle rows
        self._build_toggle_row(settings_section, "Include Uppercase", "(A-Z)", self.upper_var)
        self._build_toggle_row(settings_section, "Include Lowercase", "(a-z)", self.lower_var)
        self._build_toggle_row(settings_section, "Include Numbers", "(0-9)", self.digits_var)
        self._build_toggle_row(settings_section, "Include Symbols", "(!@#$...)", self.symbols_var, is_last=True)

        # 6. Action Buttons Section (Generate & Reset)
        actions_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        actions_frame.pack(fill="x", padx=24, pady=(8, 16), side="bottom")

        self.generate_btn = ctk.CTkButton(
            actions_frame,
            text="GENERATE PASSWORD",
            height=46,
            corner_radius=10,
            fg_color="#6366F1",
            hover_color="#4F46E5",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#FFFFFF",
            command=self.on_generate
        )
        self.generate_btn.pack(fill="x", pady=(0, 6))

        # Reset button
        self.reset_btn = ctk.CTkButton(
            actions_frame,
            text="↺ Reset to Defaults",
            height=28,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#1E293B",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#64748B",
            command=self.on_reset
        )
        self.reset_btn.pack()

    def _build_toggle_row(self, parent, label_text: str, hint_text: str, variable: "ctk.BooleanVar", is_last: bool = False):
        row = ctk.CTkFrame(parent, fg_color="transparent", cursor="hand2")
        row.pack(fill="x", padx=14, pady=(4, 10 if is_last else 4))

        # Label container
        labels_box = ctk.CTkFrame(row, fg_color="transparent")
        labels_box.pack(side="left", fill="x", expand=True)

        title = ctk.CTkLabel(
            labels_box,
            text=label_text,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#F1F5F9"
        )
        title.pack(side="left")

        hint = ctk.CTkLabel(
            labels_box,
            text=f" {hint_text}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#64748B"
        )
        hint.pack(side="left")

        # Switch widget
        switch = ctk.CTkSwitch(
            row,
            text="",
            variable=variable,
            width=44,
            switch_width=40,
            switch_height=20,
            progress_color="#6366F1",
            fg_color="#334155"
        )
        switch.pack(side="right")

        # Make entire row clickable
        def toggle_var(event=None):
            variable.set(not variable.get())

        row.bind("<Button-1>", toggle_var)
        title.bind("<Button-1>", toggle_var)
        hint.bind("<Button-1>", toggle_var)

    def on_slider_change(self, value):
        val_int = int(round(value))
        self.length_val_display.configure(text=str(val_int))

    def on_generate(self):
        length = self.length_var.get()
        upper = self.upper_var.get()
        lower = self.lower_var.get()
        digits = self.digits_var.get()
        symbols = self.symbols_var.get()

        # Validation: Check if at least one character set is selected
        if not (upper or lower or digits or symbols):
            self.password_label.configure(
                text="Please select ≥ 1 character type",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color="#EF4444"
            )
            self.strength_value_label.configure(text="Invalid", text_color="#EF4444")
            self.strength_bar.set(0.0)
            self.strength_bar.configure(progress_color="#EF4444")
            self.copy_status_label.configure(text="Cannot copy empty settings", text_color="#EF4444")
            self.current_password = ""
            return

        # Generate password
        try:
            pwd = generate_password(
                length=length,
                include_upper=upper,
                include_lower=lower,
                include_digits=digits,
                include_symbols=symbols
            )
            self.current_password = pwd
            self.password_label.configure(
                text=pwd,
                font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
                text_color="#38BDF8"
            )

            # Update strength
            rating, ratio, color = calculate_strength(pwd, upper, lower, digits, symbols)
            self.strength_value_label.configure(text=rating, text_color=color)
            self.strength_bar.set(ratio)
            self.strength_bar.configure(progress_color=color)

            # Reset copy status text if not in active copied state
            self.copy_status_label.configure(text="Click to copy", text_color="#64748B")
            self.copy_btn.configure(text="📋 Copy", fg_color="#334155")
        except Exception as e:
            self.password_label.configure(
                text="Error generating password",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color="#EF4444"
            )
            self.current_password = ""

    def on_copy(self):
        if not self.current_password:
            return

        # Copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_password)
        self.root.update()  # Persist clipboard content

        # Visual feedback
        self.copy_status_label.configure(text="✓ Password copied to clipboard!", text_color="#10B981")
        self.copy_btn.configure(text="✓ Copied!", fg_color="#10B981")

        # Reset feedback after 2 seconds
        if self.copied_timer_id:
            self.root.after_cancel(self.copied_timer_id)

        self.copied_timer_id = self.root.after(2000, self._reset_copy_feedback)

    def _reset_copy_feedback(self):
        self.copy_status_label.configure(text="Click to copy", text_color="#64748B")
        self.copy_btn.configure(text="📋 Copy", fg_color="#334155")

    def on_reset(self):
        self.length_var.set(16)
        self.slider.set(16)
        self.length_val_display.configure(text="16")
        self.upper_var.set(True)
        self.lower_var.set(True)
        self.digits_var.set(True)
        self.symbols_var.set(False)
        self.current_password = ""

        self.password_label.configure(
            text="Your password will appear here",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="normal"),
            text_color="#64748B"
        )
        self.strength_value_label.configure(text="Not generated", text_color="#64748B")
        self.strength_bar.set(0.0)
        self.strength_bar.configure(progress_color="#64748B")
        self.copy_status_label.configure(text="Click to copy", text_color="#64748B")
        self.copy_btn.configure(text="📋 Copy", fg_color="#334155")


class StandardTkinterApp:
    """
    Standard Tkinter fallback implementation in case CustomTkinter is unavailable.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Password Generator")
        
        # Center the window on desktop screen
        win_width, win_height = 480, 680
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        pos_x = max(0, (screen_width - win_width) // 2)
        pos_y = max(0, (screen_height - win_height) // 2)
        self.root.geometry(f"{win_width}x{win_height}+{pos_x}+{pos_y}")
        self.root.minsize(440, 620)
        self.root.configure(bg="#0B0F19")

        self.length_var = tk.IntVar(value=16)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=False)
        self.current_password = ""

        self._build_ui()

    def _build_ui(self):
        wrapper = tk.Frame(self.root, bg="#0B0F19")
        wrapper.pack(expand=True, fill="both", padx=20, pady=20)

        container = tk.Frame(wrapper, bg="#121826", padx=24, pady=24, width=460)
        container.pack(expand=True, fill="y", anchor="center")

        tk.Label(
            container, text="Password Generator", font=("Segoe UI", 18, "bold"),
            bg="#121826", fg="#F8FAFC"
        ).pack(anchor="w", pady=(0, 2))

        tk.Label(
            container, text="Generate strong & secure random passwords", font=("Segoe UI", 10),
            bg="#121826", fg="#94A3B8"
        ).pack(anchor="w", pady=(0, 15))

        # Display Card
        disp_card = tk.Frame(container, bg="#1E293B", padx=12, pady=12, cursor="hand2")
        disp_card.pack(fill="x", pady=(0, 12))
        disp_card.bind("<Button-1>", lambda e: self.on_copy())

        self.pwd_label = tk.Label(
            disp_card, text="Your password will appear here", font=("Segoe UI", 13),
            bg="#1E293B", fg="#64748B", wraplength=350
        )
        self.pwd_label.pack(fill="x", pady=4)
        self.pwd_label.bind("<Button-1>", lambda e: self.on_copy())

        self.copy_status = tk.Label(
            disp_card, text="Click to copy", font=("Segoe UI", 9),
            bg="#1E293B", fg="#64748B"
        )
        self.copy_status.pack(pady=(2, 0))
        self.copy_status.bind("<Button-1>", lambda e: self.on_copy())

        # Strength
        str_frame = tk.Frame(container, bg="#161F33", padx=10, pady=8)
        str_frame.pack(fill="x", pady=(0, 12))

        tk.Label(str_frame, text="STRENGTH:", font=("Segoe UI", 9, "bold"), bg="#161F33", fg="#94A3B8").pack(side="left")
        self.str_val = tk.Label(str_frame, text="Not generated", font=("Segoe UI", 10, "bold"), bg="#161F33", fg="#64748B")
        self.str_val.pack(side="right")

        # Length slider
        len_frame = tk.Frame(container, bg="#121826")
        len_frame.pack(fill="x", pady=(0, 12))

        len_top = tk.Frame(len_frame, bg="#121826")
        len_top.pack(fill="x")
        tk.Label(len_top, text="LENGTH", font=("Segoe UI", 10, "bold"), bg="#121826", fg="#94A3B8").pack(side="left")
        self.len_lbl = tk.Label(len_top, text="16", font=("Segoe UI", 11, "bold"), bg="#121826", fg="#38BDF8")
        self.len_lbl.pack(side="right")

        self.scale = tk.Scale(
            len_frame, from_=4, to=32, orient="horizontal", variable=self.length_var,
            bg="#1E293B", fg="#F8FAFC", highlightthickness=0,
            command=self.on_scale_change
        )
        self.scale.pack(fill="x", pady=4)

        # Settings
        set_frame = tk.Frame(container, bg="#161F33", padx=12, pady=10)
        set_frame.pack(fill="x", pady=(0, 15))

        for text, var in [
            ("Include Uppercase", self.upper_var),
            ("Include Lowercase", self.lower_var),
            ("Include Numbers", self.digits_var),
            ("Include Symbols", self.symbols_var),
        ]:
            cb = tk.Checkbutton(
                set_frame, text=text, variable=var,
                bg="#161F33", fg="#F8FAFC", selectcolor="#1E293B",
                activebackground="#161F33", activeforeground="#F8FAFC"
            )
            cb.pack(anchor="w", pady=2)

        # Generate Button
        btn = tk.Button(
            container, text="GENERATE PASSWORD", font=("Segoe UI", 11, "bold"),
            bg="#6366F1", fg="#FFFFFF", activebackground="#4F46E5", activeforeground="#FFFFFF",
            relief="flat", pady=8, cursor="hand2", command=self.on_generate
        )
        btn.pack(fill="x")

    def on_scale_change(self, val):
        self.len_lbl.config(text=str(val))

    def on_generate(self):
        upper = self.upper_var.get()
        lower = self.lower_var.get()
        digits = self.digits_var.get()
        symbols = self.symbols_var.get()
        length = self.length_var.get()

        if not (upper or lower or digits or symbols):
            self.pwd_label.config(text="Please select ≥ 1 character type", fg="#EF4444")
            self.str_val.config(text="Invalid", fg="#EF4444")
            self.current_password = ""
            return

        pwd = generate_password(length, upper, lower, digits, symbols)
        self.current_password = pwd
        self.pwd_label.config(text=pwd, fg="#38BDF8")
        rating, _, color = calculate_strength(pwd, upper, lower, digits, symbols)
        self.str_val.config(text=rating, fg=color)
        self.copy_status.config(text="Click to copy", fg="#64748B")

    def on_copy(self):
        if not self.current_password:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_password)
        self.copy_status.config(text="✓ Password copied to clipboard!", fg="#10B981")
        self.root.after(2000, lambda: self.copy_status.config(text="Click to copy", fg="#64748B"))


def main():
    """Main application entry point."""
    if USE_CUSTOMTKINTER:
        root = ctk.CTk()
        app = ModernPasswordGeneratorApp(root)
        root.mainloop()
    else:
        root = tk.Tk()
        app = StandardTkinterApp(root)
        root.mainloop()


if __name__ == "__main__":
    main()
