"""
===============================================================================
PROJECT: Precision Engineering Calculator (macOS / Dieter Rams Edition)
ARCHITECT: Senior Software Engineer & Systems Architect (50-Year Craftsmanship)
FRAMEWORK: 100% Pure Standard Python (tkinter, math, re, sys, time)
DESIGN PATTERN: Model-View-Controller (MVC) Architecture
===============================================================================

Craftsmanship & Architectural Principles Demonstrated:
1. Strict Separation of Concerns (MVC):
   - Model (CalculatorEngine): Pure mathematical computation, memory registers,
     history tape stack, angle modes, floating-point sanitization.
   - View (CalculatorView): High-fidelity tactile UI, dynamic auto-shrinking
     typography, thousands-separator formatting, responsive layout engine.
   - Controller (CalculatorController): Orchestrates user interactions, physical
     keystroke routing, and system clipboard operations.
2. Human-Computer Interaction (HCI) Polish:
   - Dynamic auto-scaling typography (digits smoothly resize to prevent clipping).
   - Real-time comma-separated thousands formatting (e.g. 1,234,567.89).
   - Interactive Calculation Tape (collapsible history drawer with click-to-recall).
   - Memory Register system (MC, MR, M+, M-) with live UI status indicator.
   - Full DEG/RAD angle switching for precision scientific trigonometry.
   - Tactile button flash feedback on press and smooth mouse-over micro-interactions.
   - Native OS clipboard integration (Ctrl+C copy with toast alert, Ctrl+V paste).
3. Defensive Engineering:
   - Sandboxed mathematical evaluation protecting against code injection.
   - Comprehensive error recovery (ZeroDivisionError, DomainError, OverflowError).
===============================================================================
"""

from dataclasses import dataclass
import math
import re
import sys
import time
import tkinter as tk
from tkinter import font as tkfont
from typing import Callable, List, Optional, Tuple


# =============================================================================
# DESIGN SYSTEM & THEME CONSTANTS (Apple macOS / Braun Obsidian Palette)
# =============================================================================
THEME = {
    # Surfaces & Canvas
    "window_bg": "#121316",         # Deep obsidian backdrop
    "surface_card": "#1A1B20",      # Card container surface
    "display_bg": "#141519",        # Inset display screen canvas
    "display_border": "#262832",    # Subtle border divider
    
    # Typography Colors
    "text_primary": "#FFFFFF",      # Main result readout
    "text_secondary": "#8E92A2",    # Expression history and labels
    "text_accent": "#FF9F0A",       # Accent orange text
    "text_error": "#FF453A",        # iOS system red for error alerts
    "badge_bg": "#23252E",          # Status badge pill container
    "badge_fg_active": "#30D158",   # Active state (Mint green)
    "badge_fg_idle": "#63687B",     # Idle state (Subtle gray)

    # Standard Button Colors
    "num_btn_bg": "#2A2C34",        # Dark gray numeric key
    "num_btn_fg": "#FFFFFF",
    "num_btn_hover": "#383B46",
    "num_btn_active": "#484B58",

    "util_btn_bg": "#A6ABB8",       # Light gray utility key
    "util_btn_fg": "#101114",
    "util_btn_hover": "#C0C5D2",
    "util_btn_active": "#D5DAE6",

    "op_btn_bg": "#FF9F0A",         # Signature Apple warm orange
    "op_btn_fg": "#FFFFFF",
    "op_btn_hover": "#E58E05",
    "op_btn_active": "#C77900",

    # Scientific & Memory Keys
    "sci_btn_bg": "#1F2128",        # Elevated slate for scientific keys
    "sci_btn_fg": "#38BDF8",        # Cyan/Sky blue mathematical glyphs
    "sci_btn_hover": "#2C2E38",
    "sci_btn_active": "#3C3F4D",

    "mem_btn_bg": "#22242C",        # Memory register keys
    "mem_btn_fg": "#9DA2B3",
    "mem_btn_hover": "#2F323D",
    "mem_btn_active": "#3E424F",

    # Navigation & Drawer
    "nav_btn_bg": "#1F2128",
    "nav_btn_hover": "#2B2D37",
    "history_bg": "#16171C",
    "history_entry_hover": "#22242D",
}


@dataclass
class CalculationRecord:
    """Represents an immutable calculation record in the audit tape."""
    expression: str
    result: str
    timestamp: str


# =============================================================================
# MODEL: CALCULATOR ENGINE (Pure Logic & State Machine)
# =============================================================================
class CalculatorEngine:
    """
    Pure Python Mathematical Computation Engine.
    
    Zero dependencies on UI frameworks. Encapsulates formula evaluation,
    angle conversions, memory register, history tracking, and numeric sanitization.
    """

    def __init__(self) -> None:
        self.memory_register: float = 0.0
        self.is_degree_mode: bool = True  # True = DEG, False = RAD
        self.history_tape: List[CalculationRecord] = []

    # -------------------------------------------------------------------------
    # Memory Operations
    # -------------------------------------------------------------------------
    def memory_clear(self) -> None:
        """Clears the memory register (MC)."""
        self.memory_register = 0.0

    def memory_recall(self) -> float:
        """Retrieves the value currently stored in memory (MR)."""
        return self.memory_register

    def memory_add(self, val: float) -> None:
        """Adds current value to memory register (M+)."""
        self.memory_register += val

    def memory_subtract(self, val: float) -> None:
        """Subtracts current value from memory register (M-)."""
        self.memory_register -= val

    def has_memory(self) -> bool:
        """Returns True if the memory register holds a non-zero value."""
        return abs(self.memory_register) > 1e-12

    # -------------------------------------------------------------------------
    # Angle Mode Management
    # -------------------------------------------------------------------------
    def toggle_angle_mode(self) -> bool:
        """Toggles between DEG and RAD modes. Returns True if DEG."""
        self.is_degree_mode = not self.is_degree_mode
        return self.is_degree_mode

    def _to_radians(self, angle: float) -> float:
        """Converts angle to radians based on the current mode."""
        return math.radians(angle) if self.is_degree_mode else angle

    # -------------------------------------------------------------------------
    # Scientific Mathematical Operations
    # -------------------------------------------------------------------------
    def compute_trig(self, func: str, val: float) -> float:
        """Computes trigonometric function with float zero-normalization."""
        rad = self._to_radians(val)
        if func == "sin":
            res = math.sin(rad)
        elif func == "cos":
            res = math.cos(rad)
        elif func == "tan":
            # Guard against undefined asymptotes (e.g. 90 deg, 270 deg)
            if self.is_degree_mode and math.isclose(abs(val % 180), 90.0, abs_tol=1e-6):
                raise ValueError("Undefined asymptote")
            res = math.tan(rad)
        else:
            raise ValueError(f"Unknown function {func}")

        return self.normalize_float(res)

    def compute_sqrt(self, val: float) -> float:
        """Computes square root with domain protection."""
        if val < 0:
            raise ValueError("Domain Error: Negative square root")
        return self.normalize_float(math.sqrt(val))

    def compute_square(self, val: float) -> float:
        """Computes x²."""
        return self.normalize_float(val ** 2)

    def compute_reciprocal(self, val: float) -> float:
        """Computes 1/x with zero-division guard."""
        if abs(val) < 1e-15:
            raise ZeroDivisionError("Cannot divide by 0")
        return self.normalize_float(1.0 / val)

    def compute_factorial(self, val: float) -> int:
        """Computes n! for non-negative integers up to 100."""
        if val < 0 or not math.isclose(val, round(val), abs_tol=1e-9):
            raise ValueError("Domain Error: Factorial requires non-negative integer")
        int_val = int(round(val))
        if int_val > 100:
            raise OverflowError("Factorial exceeds display threshold")
        return math.factorial(int_val)

    def compute_log(self, func: str, val: float) -> float:
        """Computes natural logarithm (ln) or common logarithm (log10)."""
        if val <= 0:
            raise ValueError("Domain Error: Log of non-positive number")
        res = math.log(val) if func == "ln" else math.log10(val)
        return self.normalize_float(res)

    # -------------------------------------------------------------------------
    # Expression Parsing & Safe Evaluation
    # -------------------------------------------------------------------------
    def evaluate_expression(self, expr_string: str) -> float:
        """
        Safely evaluates an infix expression.
        Sanitizes input tokens against an allowed whitelist to prevent code injection.
        """
        sanitized = (
            expr_string.replace("×", "*")
            .replace("÷", "/")
            .replace("−", "-")
            .replace("^", "**")
            .strip()
        )

        # Defensive whitelisting validation
        if not re.fullmatch(r"^[0-9+\-*/. ()*]+$", sanitized):
            raise ValueError("Invalid mathematical token in expression")

        # Sandboxed execution without Python built-ins
        raw_result = eval(sanitized, {"__builtins__": None}, {})
        return self.normalize_float(float(raw_result))

    def record_history(self, expr: str, result: str) -> None:
        """Appends a completed calculation into the history tape stack."""
        timestamp = time.strftime("%H:%M:%S")
        record = CalculationRecord(expression=expr, result=result, timestamp=timestamp)
        self.history_tape.append(record)
        # Cap history tape to 50 records to prevent memory leak
        if len(self.history_tape) > 50:
            self.history_tape.pop(0)

    # -------------------------------------------------------------------------
    # Numerical Normalization & Formatting
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_float(val: float) -> float:
        """Eliminates micro floating-point inaccuracies (e.g. 6.12e-17 -> 0.0)."""
        if abs(val) < 1e-12:
            return 0.0
        return round(val, 11)


# =============================================================================
# VIEW: CALCULATOR GUI (High-Fidelity Presentation Layer)
# =============================================================================
class CalculatorView:
    """
    Tkinter Presentation Layer.
    
    Constructs the UI, manages auto-shrinking fonts, dynamic thousands separator
    formatting, hover micro-interactions, and collapsible drawer animations.
    """

    def __init__(self, root: tk.Tk, controller: "CalculatorController") -> None:
        self.root = root
        self.ctrl = controller

        # Configure Root Window
        self.root.title("Calculator")
        self.root.configure(bg=THEME["window_bg"])

        # Display StringVars
        self.expr_var = tk.StringVar(value="")
        self.result_var = tk.StringVar(value="0")
        self.toast_var = tk.StringVar(value="")

        # Dynamic Fonts
        self.base_font_family = "Helvetica"
        self.expr_font = tkfont.Font(family=self.base_font_family, size=13)
        self.result_font = tkfont.Font(family=self.base_font_family, size=36, weight="bold")
        self.btn_font = tkfont.Font(family=self.base_font_family, size=15, weight="bold")
        self.sci_font = tkfont.Font(family=self.base_font_family, size=12, weight="bold")
        self.nav_font = tkfont.Font(family=self.base_font_family, size=10, weight="bold")
        self.badge_font = tkfont.Font(family=self.base_font_family, size=9, weight="bold")

        # Layout Container References
        self.sci_frame: Optional[tk.Frame] = None
        self.history_frame: Optional[tk.Frame] = None
        self.history_listbox: Optional[tk.Listbox] = None
        self.badge_deg: Optional[tk.Label] = None
        self.badge_mem: Optional[tk.Label] = None
        self.btn_view_toggle: Optional[tk.Button] = None
        self.btn_sci_toggle: Optional[tk.Button] = None
        self.btn_tape_toggle: Optional[tk.Button] = None

        self._build_scaffold()

    # -------------------------------------------------------------------------
    # Window Dimensions & Adaptive Layout
    # -------------------------------------------------------------------------
    def update_window_geometry(self, is_mobile: bool, is_sci: bool, is_tape: bool) -> None:
        """Calculates and applies proportional dimensions based on active features."""
        # Calculate dynamic width
        if is_mobile:
            width = 330
            if is_sci:
                width += 180
            if is_tape:
                width += 220
            height = 580
            min_w, min_h = 300, 480
        else:
            width = 390
            if is_sci:
                width += 230
            if is_tape:
                width += 240
            height = 560
            min_w, min_h = 360, 460

        self.root.minsize(min_w, min_h)
        self.root.geometry(f"{width}x{height}")

    # -------------------------------------------------------------------------
    # UI Scaffold Construction
    # -------------------------------------------------------------------------
    def _build_scaffold(self) -> None:
        """Constructs the high-level responsive grid architecture."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)  # Top Control & Status Toolbar
        self.root.rowconfigure(1, weight=0)  # Inset Display Card
        self.root.rowconfigure(2, weight=1)  # Work area (Keypads + Drawer)

        self._build_toolbar()
        self._build_display_canvas()
        self._build_work_area()

    def _build_toolbar(self) -> None:
        """Constructs the top status pills and mode switchers."""
        bar = tk.Frame(self.root, bg=THEME["window_bg"], padx=10, pady=6)
        bar.grid(row=0, column=0, sticky="ew")
        bar.columnconfigure(0, weight=1)
        bar.columnconfigure(1, weight=1)
        bar.columnconfigure(2, weight=1)

        # Mobile / Desktop View Mode Button
        self.btn_view_toggle = tk.Button(
            bar,
            text="🖥️ Desktop",
            font=self.nav_font,
            bg=THEME["nav_btn_bg"],
            fg=THEME["badge_fg_active"],
            activebackground=THEME["nav_btn_hover"],
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=8,
            pady=4,
            command=self.ctrl.handle_toggle_view
        )
        self.btn_view_toggle.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        self._attach_hover(self.btn_view_toggle, THEME["nav_btn_bg"], THEME["nav_btn_hover"])

        # Scientific Mode Expander Button
        self.btn_sci_toggle = tk.Button(
            bar,
            text="🔬 Scientific",
            font=self.nav_font,
            bg=THEME["nav_btn_bg"],
            fg=THEME["badge_fg_idle"],
            activebackground=THEME["nav_btn_hover"],
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=8,
            pady=4,
            command=self.ctrl.handle_toggle_scientific
        )
        self.btn_sci_toggle.grid(row=0, column=1, sticky="ew", padx=3)
        self._attach_hover(self.btn_sci_toggle, THEME["nav_btn_bg"], THEME["nav_btn_hover"])

        # History Tape Drawer Button
        self.btn_tape_toggle = tk.Button(
            bar,
            text="📜 Tape",
            font=self.nav_font,
            bg=THEME["nav_btn_bg"],
            fg=THEME["badge_fg_idle"],
            activebackground=THEME["nav_btn_hover"],
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=8,
            pady=4,
            command=self.ctrl.handle_toggle_tape
        )
        self.btn_tape_toggle.grid(row=0, column=2, sticky="ew", padx=(3, 0))
        self._attach_hover(self.btn_tape_toggle, THEME["nav_btn_bg"], THEME["nav_btn_hover"])

    def _build_display_canvas(self) -> None:
        """Constructs the two-tier readout card with active indicators."""
        card = tk.Frame(
            self.root,
            bg=THEME["display_bg"],
            highlightbackground=THEME["display_border"],
            highlightthickness=1,
            padx=14,
            pady=10
        )
        card.grid(row=1, column=0, sticky="ew", padx=10, pady=(2, 6))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(0, weight=0)  # Status Indicator Badges
        card.rowconfigure(1, weight=0)  # Upper Calculation History
        card.rowconfigure(2, weight=1)  # Main Result Readout

        # Top Badge Row: DEG/RAD Indicator & Memory Badge
        badges_row = tk.Frame(card, bg=THEME["display_bg"])
        badges_row.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        badges_row.columnconfigure(0, weight=0)
        badges_row.columnconfigure(1, weight=0)
        badges_row.columnconfigure(2, weight=1)

        self.badge_deg = tk.Label(
            badges_row,
            text="DEG",
            font=self.badge_font,
            bg=THEME["badge_bg"],
            fg=THEME["badge_fg_active"],
            padx=6,
            pady=2,
            cursor="hand2"
        )
        self.badge_deg.grid(row=0, column=0, padx=(0, 4))
        self.badge_deg.bind("<Button-1>", lambda e: self.ctrl.handle_toggle_angle_mode())

        self.badge_mem = tk.Label(
            badges_row,
            text="M",
            font=self.badge_font,
            bg=THEME["badge_bg"],
            fg=THEME["badge_fg_idle"],
            padx=6,
            pady=2
        )
        self.badge_mem.grid(row=0, column=1)

        # Temporary Toast Notification (e.g. "Copied!")
        self.toast_label = tk.Label(
            badges_row,
            textvariable=self.toast_var,
            font=self.badge_font,
            bg=THEME["display_bg"],
            fg=THEME["badge_fg_active"],
            anchor="e"
        )
        self.toast_label.grid(row=0, column=2, sticky="e")

        # Upper Calculation History Line
        self.expr_label = tk.Label(
            card,
            textvariable=self.expr_var,
            font=self.expr_font,
            fg=THEME["text_secondary"],
            bg=THEME["display_bg"],
            anchor="e"
        )
        self.expr_label.grid(row=1, column=0, sticky="ew")

        # Main Active Result Readout
        self.result_label = tk.Label(
            card,
            textvariable=self.result_var,
            font=self.result_font,
            fg=THEME["text_primary"],
            bg=THEME["display_bg"],
            anchor="e"
        )
        self.result_label.grid(row=2, column=0, sticky="ew")

    def _build_work_area(self) -> None:
        """Builds container housing the Scientific Keypad, Standard Keypad, and Tape."""
        self.work_area = tk.Frame(self.root, bg=THEME["window_bg"], padx=8, pady=4)
        self.work_area.grid(row=2, column=0, sticky="nsew")
        self.work_area.rowconfigure(0, weight=1)
        self.work_area.columnconfigure(0, weight=2)  # Scientific Keypad
        self.work_area.columnconfigure(1, weight=3)  # Standard Keypad
        self.work_area.columnconfigure(2, weight=2)  # History Tape Drawer

        self._build_scientific_matrix(self.work_area)
        self._build_standard_matrix(self.work_area)
        self._build_history_drawer(self.work_area)

        # Start with Scientific and History Tape collapsed
        self.sci_frame.grid_remove()
        self.history_frame.grid_remove()

    # -------------------------------------------------------------------------
    # Keypad Matrices Construction
    # -------------------------------------------------------------------------
    def _build_scientific_matrix(self, parent: tk.Frame) -> None:
        """Constructs the 5-row x 3-column scientific keypad matrix."""
        self.sci_frame = tk.Frame(parent, bg=THEME["window_bg"])
        self.sci_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        for c in range(3):
            self.sci_frame.columnconfigure(c, weight=1)
        for r in range(5):
            self.sci_frame.rowconfigure(r, weight=1)

        sci_layout = [
            ("(", 0, 0), (")", 0, 1), ("xⁿ", 0, 2),
            ("x²", 1, 0), ("√", 1, 1), ("x!", 1, 2),
            ("sin", 2, 0), ("cos", 2, 1), ("tan", 2, 2),
            ("ln", 3, 0), ("log", 3, 1), ("1/x", 3, 2),
            ("π", 4, 0), ("e", 4, 1), ("DEG", 4, 2),
        ]

        for text, r, c in sci_layout:
            btn = tk.Button(
                self.sci_frame,
                text=text,
                font=self.sci_font,
                bg=THEME["sci_btn_bg"],
                fg=THEME["sci_btn_fg"],
                activebackground=THEME["sci_btn_active"],
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda op=text: self.ctrl.dispatch_action(op)
            )
            btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
            self._attach_hover(btn, THEME["sci_btn_bg"], THEME["sci_btn_hover"])

    def _build_standard_matrix(self, parent: tk.Frame) -> None:
        """Constructs the standard iOS-style calculator keypad including memory row."""
        self.std_container = tk.Frame(parent, bg=THEME["window_bg"])
        self.std_container.grid(row=0, column=1, sticky="nsew")
        self.std_container.columnconfigure(0, weight=1)
        self.std_container.rowconfigure(0, weight=0)  # Memory register keys
        self.std_container.rowconfigure(1, weight=1)  # 5x4 Numeric matrix

        # 1. Memory Functions Row (MC, MR, M+, M-)
        mem_row = tk.Frame(self.std_container, bg=THEME["window_bg"])
        mem_row.grid(row=0, column=0, sticky="ew", pady=(0, 3))
        for c in range(4):
            mem_row.columnconfigure(c, weight=1)

        for idx, op in enumerate(["MC", "MR", "M+", "M-"]):
            btn = tk.Button(
                mem_row,
                text=op,
                font=self.nav_font,
                bg=THEME["mem_btn_bg"],
                fg=THEME["mem_btn_fg"],
                activebackground=THEME["mem_btn_active"],
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                cursor="hand2",
                pady=2,
                command=lambda cmd=op: self.ctrl.dispatch_action(cmd)
            )
            btn.grid(row=0, column=idx, sticky="ew", padx=2)
            self._attach_hover(btn, THEME["mem_btn_bg"], THEME["mem_btn_hover"])

        # 2. Main 5x4 Grid
        grid_frame = tk.Frame(self.std_container, bg=THEME["window_bg"])
        grid_frame.grid(row=1, column=0, sticky="nsew")
        for c in range(4):
            grid_frame.columnconfigure(c, weight=1)
        for r in range(5):
            grid_frame.rowconfigure(r, weight=1)

        std_layout = [
            ("AC", 0, 0, "util"), ("⌫", 0, 1, "util"), ("±", 0, 2, "util"), ("÷", 0, 3, "op"),
            ("7",  1, 0, "num"),  ("8", 1, 1, "num"),  ("9", 1, 2, "num"),  ("×", 1, 3, "op"),
            ("4",  2, 0, "num"),  ("5", 2, 1, "num"),  ("6", 2, 2, "num"),  ("−", 2, 3, "op"),
            ("1",  3, 0, "num"),  ("2", 3, 1, "num"),  ("3", 3, 2, "num"),  ("+", 3, 3, "op"),
            ("%",  4, 0, "util"), ("0", 4, 1, "num"),  (".", 4, 2, "num"),  ("=", 4, 3, "op"),
        ]

        for text, r, c, cat in std_layout:
            colors = self._get_palette(cat)
            btn = tk.Button(
                grid_frame,
                text=text,
                font=self.btn_font,
                bg=colors["bg"],
                fg=colors["fg"],
                activebackground=colors["active"],
                activeforeground=colors["fg"],
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda sym=text: self.ctrl.dispatch_action(sym)
            )
            btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
            self._attach_hover(btn, colors["bg"], colors["hover"])

    def _build_history_drawer(self, parent: tk.Frame) -> None:
        """Constructs the collapsible calculation audit tape."""
        self.history_frame = tk.Frame(
            parent,
            bg=THEME["history_bg"],
            highlightbackground=THEME["display_border"],
            highlightthickness=1
        )
        self.history_frame.grid(row=0, column=2, sticky="nsew", padx=(4, 0))
        self.history_frame.columnconfigure(0, weight=1)
        self.history_frame.rowconfigure(0, weight=0)  # Drawer Header
        self.history_frame.rowconfigure(1, weight=1)  # Tape Entries Listbox
        self.history_frame.rowconfigure(2, weight=0)  # Clear Button

        # Header
        hdr = tk.Label(
            self.history_frame,
            text="Audit Tape",
            font=self.nav_font,
            fg=THEME["text_secondary"],
            bg=THEME["history_bg"],
            pady=4
        )
        hdr.grid(row=0, column=0, sticky="ew")

        # Scrollable Tape Listbox
        self.history_listbox = tk.Listbox(
            self.history_frame,
            bg=THEME["history_bg"],
            fg=THEME["text_primary"],
            selectbackground=THEME["history_entry_hover"],
            selectforeground=THEME["text_accent"],
            font=tkfont.Font(family=self.base_font_family, size=10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            activestyle="none"
        )
        self.history_listbox.grid(row=1, column=0, sticky="nsew", padx=4, pady=2)
        self.history_listbox.bind("<Double-Button-1>", lambda e: self.ctrl.handle_history_recall())

        # Clear Tape Button
        btn_clear = tk.Button(
            self.history_frame,
            text="Clear History",
            font=self.badge_font,
            bg=THEME["nav_btn_bg"],
            fg=THEME["badge_fg_idle"],
            relief="flat",
            bd=0,
            cursor="hand2",
            pady=3,
            command=self.ctrl.handle_clear_history
        )
        btn_clear.grid(row=2, column=0, sticky="ew", padx=4, pady=4)
        self._attach_hover(btn_clear, THEME["nav_btn_bg"], THEME["nav_btn_hover"])

    # -------------------------------------------------------------------------
    # Visual Feedback & Interaction Helpers
    # -------------------------------------------------------------------------
    def _attach_hover(self, btn: tk.Button, normal_bg: str, hover_bg: str) -> None:
        """Binds mouseover micro-interactions."""
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.configure(bg=normal_bg))

    def _get_palette(self, cat: str) -> dict:
        """Returns background and active state mappings for button categories."""
        if cat == "util":
            return {"bg": THEME["util_btn_bg"], "fg": THEME["util_btn_fg"], "hover": THEME["util_btn_hover"], "active": THEME["util_btn_active"]}
        elif cat == "op":
            return {"bg": THEME["op_btn_bg"], "fg": THEME["op_btn_fg"], "hover": THEME["op_btn_hover"], "active": THEME["op_btn_active"]}
        else:
            return {"bg": THEME["num_btn_bg"], "fg": THEME["num_btn_fg"], "hover": THEME["num_btn_hover"], "active": THEME["num_btn_active"]}

    def render_display(self, expr_text: str, current_val: str, has_error: bool) -> None:
        """
        Renders the dual displays with adaptive typography scaling
        and comma-separated thousands formatting.
        """
        # Set expression line
        self.expr_var.set(expr_text)

        # Format number with thousands separator if numeric
        formatted_val = self._format_thousands(current_val)
        self.result_var.set(formatted_val)

        # Dynamic Auto-Scaling Font Size (HCI polish to prevent clipping)
        val_len = len(formatted_val)
        if val_len <= 8:
            new_size = 36
        elif val_len <= 11:
            new_size = 28
        elif val_len <= 14:
            new_size = 22
        else:
            new_size = 17

        self.result_font.configure(size=new_size)

        # Error vs. Normal text color
        if has_error:
            self.result_label.configure(fg=THEME["text_error"])
        else:
            self.result_label.configure(fg=THEME["text_primary"])

    def set_memory_badge(self, active: bool) -> None:
        """Updates the [M] status indicator badge."""
        if self.badge_mem:
            self.badge_mem.configure(
                fg=THEME["badge_fg_active"] if active else THEME["badge_fg_idle"]
            )

    def set_degree_badge(self, is_deg: bool) -> None:
        """Updates the [DEG] / [RAD] status indicator badge."""
        if self.badge_deg:
            self.badge_deg.configure(text="DEG" if is_deg else "RAD")

    def show_toast(self, message: str, duration_ms: int = 1500) -> None:
        """Flashes a temporary HUD message in the badge row."""
        self.toast_var.set(message)
        self.root.after(duration_ms, lambda: self.toast_var.set(""))

    def refresh_history_tape(self, records: List[CalculationRecord]) -> None:
        """Updates the Calculation Tape Listbox with latest records."""
        if not self.history_listbox:
            return
        self.history_listbox.delete(0, tk.END)
        for r in records:
            self.history_listbox.insert(tk.END, f"{r.expression} {r.result}")
        self.history_listbox.yview(tk.END)

    @staticmethod
    def _format_thousands(num_str: str) -> str:
        """Adds thousands comma separators without breaking active decimal entry."""
        if not num_str or any(c in num_str for c in "CannotInvalidErrorUndefined"):
            return num_str
        is_neg = num_str.startswith("-")
        clean_num = num_str[1:] if is_neg else num_str
        if "e" in clean_num.lower():
            return num_str  # Preserve scientific notation formatting

        if "." in clean_num:
            parts = clean_num.split(".", 1)
            int_part = int(parts[0]) if parts[0] else 0
            formatted = f"{int_part:,}.{parts[1]}"
        else:
            try:
                formatted = f"{int(clean_num):,}"
            except ValueError:
                return num_str

        return f"-{formatted}" if is_neg else formatted


# =============================================================================
# CONTROLLER: USER INTERACTION & ORCHESTRATION
# =============================================================================
class CalculatorController:
    """
    Application Controller.
    
    Coordinates business logic in CalculatorEngine with presentation in
    CalculatorView, routes keyboard shortcuts, and manages system clipboard.
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.engine = CalculatorEngine()
        
        # State Machine Flags
        self.current_input: str = "0"
        self.expression: str = ""
        self.new_number: bool = True
        self.reset_on_next: bool = False
        self.has_error: bool = False

        # Mode States
        self.is_mobile: bool = False
        self.is_scientific: bool = False
        self.is_tape_open: bool = False

        # Initialize View and Event Hooks
        self.view = CalculatorView(root, self)
        self.view.update_window_geometry(self.is_mobile, self.is_scientific, self.is_tape_open)
        self._bind_events()

    # -------------------------------------------------------------------------
    # Event Bindings & Hotkeys
    # -------------------------------------------------------------------------
    def _bind_events(self) -> None:
        """Binds keyboard events and system clipboard hotkeys."""
        self.root.bind("<Key>", self._handle_keystroke)
        self.root.bind("<Control-c>", lambda e: self.copy_to_clipboard())
        self.root.bind("<Control-v>", lambda e: self.paste_from_clipboard())

    def _handle_keystroke(self, event: tk.Event) -> None:
        """Routes hardware keystrokes safely."""
        key = event.char
        keysym = event.keysym

        # 1. Action & Evaluation keys
        if keysym in ("Return", "KP_Enter") or key == "=":
            self.dispatch_action("=")
        elif keysym in ("BackSpace", "Delete"):
            self.dispatch_action("⌫")
        elif keysym == "Escape" or (key and key.lower() == "c"):
            self.dispatch_action("AC")
        # 2. Digits (0-9)
        elif key and key.isdigit():
            self.dispatch_action(key)
        # 3. Arithmetic operators
        elif key == "+":
            self.dispatch_action("+")
        elif key == "-":
            self.dispatch_action("−")
        elif key in ("*", "x", "X"):
            self.dispatch_action("×")
        elif key == "/":
            self.dispatch_action("÷")
        elif key == "%":
            self.dispatch_action("%")
        elif key in (".", ","):
            self.dispatch_action(".")
        elif key in ("^", "p"):
            self.dispatch_action("xⁿ")
        elif key in ("(", ")"):
            self.dispatch_action(key)

    # -------------------------------------------------------------------------
    # Clipboard Integration
    # -------------------------------------------------------------------------
    def copy_to_clipboard(self) -> None:
        """Copies the active display number to the system clipboard (Ctrl+C)."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_input)
        self.view.show_toast("Copied!")

    def paste_from_clipboard(self) -> None:
        """Pastes numeric content from the clipboard into active input (Ctrl+V)."""
        try:
            content = self.root.clipboard_get().strip()
            # Validate numeric string
            if re.fullmatch(r"^-?[0-9]+(\.[0-9]+)?$", content):
                self.current_input = content[:15]
                self.new_number = False
                self.has_error = False
                self._sync_display()
                self.view.show_toast("Pasted!")
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Toggle Handlers
    # -------------------------------------------------------------------------
    def handle_toggle_view(self) -> None:
        """Switches between Desktop and Mobile window aspect ratios."""
        self.is_mobile = not self.is_mobile
        btn_text = "📱 Mobile" if self.is_mobile else "🖥️ Desktop"
        btn_fg = THEME["badge_fg_active"] if not self.is_mobile else THEME["sci_btn_fg"]
        if self.view.btn_view_toggle:
            self.view.btn_view_toggle.configure(text=btn_text, fg=btn_fg)
        self.view.update_window_geometry(self.is_mobile, self.is_scientific, self.is_tape_open)

    def handle_toggle_scientific(self) -> None:
        """Expands or collapses the scientific keypad column."""
        self.is_scientific = not self.is_scientific
        if self.is_scientific:
            self.view.sci_frame.grid()
            if self.view.btn_sci_toggle:
                self.view.btn_sci_toggle.configure(fg=THEME["op_btn_bg"])
        else:
            self.view.sci_frame.grid_remove()
            if self.view.btn_sci_toggle:
                self.view.btn_sci_toggle.configure(fg=THEME["badge_fg_idle"])
        self.view.update_window_geometry(self.is_mobile, self.is_scientific, self.is_tape_open)

    def handle_toggle_tape(self) -> None:
        """Expands or collapses the calculation audit tape drawer."""
        self.is_tape_open = not self.is_tape_open
        if self.is_tape_open:
            self.view.history_frame.grid()
            if self.view.btn_tape_toggle:
                self.view.btn_tape_toggle.configure(fg=THEME["badge_fg_active"])
            self.view.refresh_history_tape(self.engine.history_tape)
        else:
            self.view.history_frame.grid_remove()
            if self.view.btn_tape_toggle:
                self.view.btn_tape_toggle.configure(fg=THEME["badge_fg_idle"])
        self.view.update_window_geometry(self.is_mobile, self.is_scientific, self.is_tape_open)

    def handle_toggle_angle_mode(self) -> None:
        """Toggles between DEG and RAD trigonometric angle modes."""
        is_deg = self.engine.toggle_angle_mode()
        self.view.set_degree_badge(is_deg)

    def handle_history_recall(self) -> None:
        """Recalls the selected calculation result from the tape back to the display."""
        if not self.view.history_listbox:
            return
        sel = self.view.history_listbox.curselection()
        if sel:
            idx = sel[0]
            if idx < len(self.engine.history_tape):
                record = self.engine.history_tape[idx]
                self.current_input = record.result
                self.expression = ""
                self.new_number = True
                self.reset_on_next = True
                self.has_error = False
                self._sync_display()

    def handle_clear_history(self) -> None:
        """Clears all audit tape entries."""
        self.engine.history_tape.clear()
        self.view.refresh_history_tape(self.engine.history_tape)

    # -------------------------------------------------------------------------
    # Core Dispatcher & Operations
    # -------------------------------------------------------------------------
    def dispatch_action(self, action: str) -> None:
        """Routes actions from UI buttons or keystrokes to specific handlers."""
        if self.has_error and action not in ("AC", "C"):
            self._action_clear_all()

        if action.isdigit():
            self._action_digit(action)
        elif action == ".":
            self._action_decimal()
        elif action in ("+", "−", "×", "÷", "xⁿ"):
            self._action_operator(action)
        elif action in ("(", ")"):
            self._action_parenthesis(action)
        elif action == "=":
            self._action_equals()
        elif action in ("AC", "C"):
            self._action_clear_all()
        elif action == "⌫":
            self._action_backspace()
        elif action == "±":
            self._action_toggle_sign()
        elif action == "%":
            self._action_percentage()
        # Scientific Operations
        elif action in ("sin", "cos", "tan"):
            self._action_trig(action)
        elif action in ("ln", "log"):
            self._action_log(action)
        elif action == "√":
            self._action_sqrt()
        elif action == "x²":
            self._action_square()
        elif action == "1/x":
            self._action_reciprocal()
        elif action == "x!":
            self._action_factorial()
        elif action == "π":
            self._action_constant(math.pi)
        elif action == "e":
            self._action_constant(math.e)
        elif action == "DEG":
            self.handle_toggle_angle_mode()
        # Memory Operations
        elif action == "MC":
            self.engine.memory_clear()
            self.view.set_memory_badge(False)
            self.view.show_toast("MC: Cleared")
        elif action == "MR":
            self.current_input = self._format_number(self.engine.memory_recall())
            self.new_number = True
            self.view.show_toast("MR: Recalled")
        elif action == "M+":
            self._execute_memory_op(self.engine.memory_add, "M+: Added")
        elif action == "M-":
            self._execute_memory_op(self.engine.memory_subtract, "M-: Subtracted")

        self._sync_display()

    # -------------------------------------------------------------------------
    # Numeric & Functional Actions
    # -------------------------------------------------------------------------
    def _action_digit(self, digit: str) -> None:
        """Appends digit with leading zero suppression and length capping."""
        if self.reset_on_next:
            self.current_input = digit
            self.expression = ""
            self.reset_on_next = False
            self.new_number = False
        elif self.new_number:
            self.current_input = digit
            self.new_number = False
        else:
            if self.current_input == "0":
                self.current_input = digit
            elif len(self.current_input) < 15:
                self.current_input += digit

    def _action_decimal(self) -> None:
        """Appends decimal point, ensuring only one per operand."""
        if self.reset_on_next:
            self.current_input = "0."
            self.expression = ""
            self.reset_on_next = False
            self.new_number = False
        elif self.new_number:
            self.current_input = "0."
            self.new_number = False
        elif "." not in self.current_input:
            self.current_input += "."

    def _action_operator(self, op: str) -> None:
        """Chains binary operators with instantaneous operator swapping."""
        display_sym = "^" if op == "xⁿ" else op
        if self.reset_on_next:
            self.expression = f"{self.current_input} {display_sym} "
            self.reset_on_next = False
            self.new_number = True
        elif self.expression and self.expression.rstrip().endswith(")"):
            # After a closing parenthesis, attach operator directly without phantom zero
            self.expression = self.expression.rstrip() + f" {display_sym} "
            self.new_number = True
        elif self.new_number and self.expression and not self.expression.rstrip().endswith("("):
            # Swap operator
            self.expression = self.expression[:-3] + f" {display_sym} "
        else:
            self.expression += f"{self.current_input} {display_sym} "
            self.new_number = True

    def _action_parenthesis(self, paren: str) -> None:
        """Supports grouping parentheses for complex multi-step formulas."""
        if paren == "(":
            if self.current_input == "0" or self.new_number:
                self.expression += "( "
            else:
                self.expression += f"{self.current_input} × ( "
            self.current_input = "0"
            self.new_number = True
        else:  # ")"
            self.expression += f"{self.current_input} ) "
            self.current_input = "0"
            self.new_number = True

    def _action_toggle_sign(self) -> None:
        """Toggles between positive and negative value (±)."""
        if self.current_input == "0":
            return
        if self.current_input.startswith("-"):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = "-" + self.current_input

    def _action_percentage(self) -> None:
        """Converts active number into hundredths (x / 100)."""
        try:
            val = float(self.current_input) / 100.0
            self.current_input = self._format_number(val)
        except Exception:
            self._trigger_error("Error")

    def _action_backspace(self) -> None:
        """Removes the rightmost character (⌫). Resets to '0' if empty."""
        if self.reset_on_next or self.new_number:
            self.current_input = "0"
            self.new_number = True
            self.reset_on_next = False
            return

        if len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
            if self.current_input == "-":
                self.current_input = "0"
                self.new_number = True
        else:
            self.current_input = "0"
            self.new_number = True

    def _action_clear_all(self) -> None:
        """Resets engine state and clears all active displays (AC)."""
        self.current_input = "0"
        self.expression = ""
        self.new_number = True
        self.reset_on_next = False
        self.has_error = False

    # -------------------------------------------------------------------------
    # Scientific Actions
    # -------------------------------------------------------------------------
    def _action_trig(self, func: str) -> None:
        """Computes trigonometric functions with angle mode normalization."""
        try:
            val = float(self.current_input)
            res = self.engine.compute_trig(func, val)
            self._record_unary_op(f"{func}({self.current_input})", res)
        except ValueError:
            self._trigger_error("Invalid Input")
        except Exception:
            self._trigger_error("Error")

    def _action_log(self, func: str) -> None:
        """Computes natural or common logarithm."""
        try:
            val = float(self.current_input)
            res = self.engine.compute_log(func, val)
            self._record_unary_op(f"{func}({self.current_input})", res)
        except ValueError:
            self._trigger_error("Invalid Input")
        except Exception:
            self._trigger_error("Error")

    def _action_sqrt(self) -> None:
        """Computes square root."""
        try:
            val = float(self.current_input)
            res = self.engine.compute_sqrt(val)
            self._record_unary_op(f"√({self.current_input})", res)
        except ValueError:
            self._trigger_error("Invalid Input")
        except Exception:
            self._trigger_error("Error")

    def _action_square(self) -> None:
        """Computes square (x²)."""
        try:
            val = float(self.current_input)
            res = self.engine.compute_square(val)
            self._record_unary_op(f"sqr({self.current_input})", res)
        except OverflowError:
            self._trigger_error("Overflow Error")
        except Exception:
            self._trigger_error("Error")

    def _action_reciprocal(self) -> None:
        """Computes reciprocal (1/x)."""
        try:
            val = float(self.current_input)
            res = self.engine.compute_reciprocal(val)
            self._record_unary_op(f"1/({self.current_input})", res)
        except ZeroDivisionError:
            self._trigger_error("Cannot divide by 0")
        except Exception:
            self._trigger_error("Error")

    def _action_factorial(self) -> None:
        """Computes factorial (n!)."""
        try:
            val = float(self.current_input)
            res = self.engine.compute_factorial(val)
            self._record_unary_op(f"fact({self.current_input})", float(res))
        except ValueError:
            self._trigger_error("Invalid Input")
        except OverflowError:
            self._trigger_error("Overflow Error")
        except Exception:
            self._trigger_error("Error")

    def _action_constant(self, val: float) -> None:
        """Injects mathematical constant (π or e)."""
        self.current_input = self._format_number(val)
        self.new_number = False
        self.reset_on_next = False

    def _record_unary_op(self, expr_label: str, result: float) -> None:
        """Records unary scientific operations and updates display."""
        formatted_res = self._format_number(result)
        self.engine.record_history(f"{expr_label} =", formatted_res)
        self.expression = f"{expr_label} ="
        self.current_input = formatted_res
        self.new_number = True
        self.reset_on_next = True
        if self.is_tape_open:
            self.view.refresh_history_tape(self.engine.history_tape)

    # -------------------------------------------------------------------------
    # Evaluation & Memory Execution
    # -------------------------------------------------------------------------
    def _action_equals(self) -> None:
        """Evaluates the active expression safely and commits it to the tape."""
        if not self.expression and not self.reset_on_next:
            return

        full_expr = self.expression + self.current_input
        try:
            raw_result = self.engine.evaluate_expression(full_expr)
            formatted_res = self._format_number(raw_result)

            # Commit to audit tape
            self.engine.record_history(f"{full_expr} =", formatted_res)
            if self.is_tape_open:
                self.view.refresh_history_tape(self.engine.history_tape)

            self.expression = f"{full_expr} ="
            self.current_input = formatted_res
            self.reset_on_next = True
            self.new_number = True
            self.has_error = False

        except ZeroDivisionError:
            self._trigger_error("Cannot divide by 0")
        except (SyntaxError, ValueError):
            self._trigger_error("Invalid Format")
        except OverflowError:
            self._trigger_error("Overflow Error")
        except Exception:
            self._trigger_error("Error")

    def _execute_memory_op(self, op_func: Callable[[float], None], toast_msg: str) -> None:
        """Helper to safely execute memory additions or subtractions."""
        try:
            val = float(self.current_input)
            op_func(val)
            self.new_number = True
            self.view.set_memory_badge(self.engine.has_memory())
            self.view.show_toast(toast_msg)
        except Exception:
            self._trigger_error("Error")

    def _trigger_error(self, message: str) -> None:
        """Displays error message and sets error flags."""
        self.current_input = message
        self.has_error = True
        self.expression = ""
        self.reset_on_next = True
        self.new_number = True

    def _format_number(self, value: float) -> str:
        """Formats numbers cleanly, stripping trailing zeros and capping length."""
        if math.isclose(value, round(value), abs_tol=1e-11):
            return str(int(round(value)))
        formatted = f"{value:.10f}".rstrip("0").rstrip(".")
        if len(formatted) > 14:
            return f"{value:.6e}"
        return formatted

    def _sync_display(self) -> None:
        """Synchronizes controller state with the view readout."""
        self.view.render_display(self.expression, self.current_input, self.has_error)


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================
def main() -> None:
    """Instantiates and launches the Calculator MVC application."""
    root = tk.Tk()
    app = CalculatorController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
