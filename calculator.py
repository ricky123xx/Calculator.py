"""
OIBSIP Advanced Calculator
===========================
A modern, professional calculator application with glassmorphism UI.
Built with Python Tkinter for OIBSIP Python Programming Internship.

Developer: Antariksh Dilkhush Sawarbandhe
Project: OIBSIP Python Programming Internship
"""

import tkinter as tk
from tkinter import font as tkfont
import math
import re


# ─────────────────────────────────────────────
#  COLOR PALETTE  —  Neon Glassmorphism Theme
# ─────────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_root":        "#0a0a14",    # Deep space black
    "bg_card":        "#0f0f1e",    # Card dark
    "bg_display":     "#07071a",    # Display deep blue-black
    "bg_btn_digit":   "#131328",    # Digit button base
    "bg_btn_op":      "#0d1a2e",    # Operator button base
    "bg_btn_accent":  "#0d0d1f",    # Special function base

    # Neon accents
    "neon_blue":      "#00b4ff",    # Primary neon blue
    "neon_cyan":      "#00ffe5",    # Cyan highlight
    "neon_purple":    "#9d4edd",    # Purple accent
    "neon_pink":      "#ff2d78",    # Equals / clear pink-red
    "neon_green":     "#39ff14",    # Optional positive accent

    # Text
    "text_primary":   "#e8f0fe",    # Bright display text
    "text_secondary": "#6b7fa8",    # Dim labels
    "text_op":        "#00ffe5",    # Operator text
    "text_accent":    "#9d4edd",    # Special fn text

    # Borders / glows
    "border_display": "#1a3a6b",    # Display border
    "border_card":    "#1a1a3e",    # Card border
    "glow_blue":      "#003f7f",    # Glow behind display
}

# ─────────────────────────────────────────────
#  FONT SIZES
# ─────────────────────────────────────────────
FONT_DISPLAY_EXPR   = ("Consolas", 14)
FONT_DISPLAY_RESULT = ("Consolas", 36, "bold")
FONT_BUTTON_LARGE   = ("Segoe UI", 18, "bold")
FONT_BUTTON_SMALL   = ("Segoe UI", 14, "bold")
FONT_TITLE          = ("Segoe UI", 15, "bold")
FONT_SUBTITLE       = ("Segoe UI", 9)
FONT_FOOTER         = ("Segoe UI", 8)
FONT_ICON           = ("Segoe UI", 28)


# ══════════════════════════════════════════════
#  CALCULATOR LOGIC
# ══════════════════════════════════════════════
class CalculatorLogic:
    """
    Pure logic layer — no UI dependencies.
    Handles expression building, evaluation, and error states.
    """

    def __init__(self):
        self.expression = ""          # The raw expression string shown on display
        self.result_text = "0"        # Last computed result (string)
        self.just_evaluated = False   # Flag: last action was '='
        self.error = False            # Flag: current state is an error

    # ── Input handlers ──────────────────────────────────────

    def append(self, value: str) -> None:
        """Append a character or token to the expression."""
        if self.error:
            self.clear()

        # After evaluation, start a fresh expression unless continuing with an operator
        if self.just_evaluated:
            if value in "+-×÷^%":
                # Continue from result
                self.expression = self.result_text + value
            else:
                # Start fresh
                self.expression = value
            self.just_evaluated = False
            return

        self.expression += value

    def backspace(self) -> None:
        """Remove last character from expression."""
        if self.error:
            self.clear()
            return
        if self.just_evaluated:
            self.expression = ""
            self.result_text = "0"
            self.just_evaluated = False
            return
        self.expression = self.expression[:-1]

    def clear(self) -> None:
        """Reset calculator to initial state."""
        self.expression = ""
        self.result_text = "0"
        self.just_evaluated = False
        self.error = False

    def evaluate(self) -> None:
        """
        Evaluate the current expression.
        Performs substitutions for display symbols before eval().
        Catches division-by-zero and other math errors.
        """
        if not self.expression.strip():
            return

        try:
            # Replace display symbols with Python equivalents
            expr = self.expression
            expr = expr.replace("×", "*")
            expr = expr.replace("÷", "/")
            expr = expr.replace("^", "**")
            expr = expr.replace("√", "math.sqrt")

            # Guard: only allow safe characters
            if re.search(r"[^0-9+\-*/().%\s\w]", expr):
                raise ValueError("Invalid characters in expression.")

            result = eval(expr, {"__builtins__": {}, "math": math})

            # Format: strip unnecessary decimals
            if isinstance(result, float):
                if result.is_integer():
                    result_str = str(int(result))
                else:
                    result_str = f"{result:.10g}"
            else:
                result_str = str(result)

            self.result_text = result_str
            self.just_evaluated = True
            self.error = False

        except ZeroDivisionError:
            self.result_text = "Division by Zero"
            self.expression = ""
            self.error = True
            self.just_evaluated = False

        except (SyntaxError, NameError, TypeError):
            self.result_text = "Syntax Error"
            self.expression = ""
            self.error = True
            self.just_evaluated = False

        except ValueError as e:
            self.result_text = "Invalid Input"
            self.expression = ""
            self.error = True
            self.just_evaluated = False

        except Exception:
            self.result_text = "Error"
            self.expression = ""
            self.error = True
            self.just_evaluated = False

    def sqrt(self) -> None:
        """Insert square-root function token."""
        if self.error:
            self.clear()
        if self.just_evaluated:
            # Wrap current result in sqrt
            self.expression = f"√({self.result_text})"
            self.just_evaluated = False
        else:
            self.expression += "√("

    def percentage(self) -> None:
        """Convert last number in expression to its percentage."""
        if self.error:
            self.clear()
            return
        if self.expression:
            self.expression += "%"

    def toggle_parens(self) -> None:
        """
        Smart parenthesis: insert '(' or ')' based on context.
        Counts unclosed parens to decide which to insert.
        """
        if self.error:
            self.clear()
            return
        open_count = self.expression.count("(")
        close_count = self.expression.count(")")
        if open_count == close_count or not self.expression:
            self.expression += "("
        else:
            self.expression += ")"


# ══════════════════════════════════════════════
#  ANIMATED BUTTON WIDGET
# ══════════════════════════════════════════════
class NeonButton(tk.Canvas):
    """
    Custom canvas-based button with:
    - Rounded rectangle shape
    - Neon border glow
    - Press animation (scale-down + color flash)
    - Hover highlight
    """

    def __init__(self, parent, text, command,
                 bg_color, fg_color, border_color,
                 width=78, height=58, font=FONT_BUTTON_LARGE, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=COLORS["bg_card"], highlightthickness=0, **kwargs)

        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.border_color = border_color
        self.btn_width = width
        self.btn_height = height
        self.btn_font = font
        self.is_pressed = False

        self._draw_button(pressed=False, hovered=False)

        # ── Bind events ──────────────────────
        self.bind("<ButtonPress-1>",   self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>",           self._on_enter)
        self.bind("<Leave>",           self._on_leave)

    # ── Drawing ───────────────────────────────

    def _draw_button(self, pressed=False, hovered=False):
        """Re-draw button in the given visual state."""
        self.delete("all")
        w, h = self.btn_width, self.btn_height
        r = 14   # corner radius

        # State adjustments
        if pressed:
            bg   = self._darken(self.bg_color, 0.6)
            bord = self.fg_color
            y_off = 1                   # slight push-down
        elif hovered:
            bg   = self._lighten(self.bg_color, 1.35)
            bord = self.fg_color
            y_off = 0
        else:
            bg   = self.bg_color
            bord = self.border_color
            y_off = 0

        # Outer glow shadow (subtle)
        if not pressed:
            self._rounded_rect(2, 2, w-2, h-2, r, fill="", outline=self._alpha_hex(bord, 0.18))

        # Main button body
        self._rounded_rect(3, 3+y_off, w-3, h-3+y_off, r, fill=bg, outline=bord)

        # Label
        self.create_text(
            w // 2, h // 2 + y_off,
            text=self.text,
            fill=self.fg_color,
            font=self.btn_font,
        )

    def _rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Draw a rounded rectangle on the canvas."""
        pts = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1,
        ]
        return self.create_polygon(pts, smooth=True, **kwargs)

    # ── Color helpers ─────────────────────────

    @staticmethod
    def _hex_to_rgb(hex_color: str):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def _rgb_to_hex(r, g, b) -> str:
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

    def _darken(self, hex_color: str, factor: float) -> str:
        r, g, b = self._hex_to_rgb(hex_color)
        return self._rgb_to_hex(r*factor, g*factor, b*factor)

    def _lighten(self, hex_color: str, factor: float) -> str:
        r, g, b = self._hex_to_rgb(hex_color)
        return self._rgb_to_hex(min(255, r*factor), min(255, g*factor), min(255, b*factor))

    def _alpha_hex(self, hex_color: str, alpha: float) -> str:
        """Blend hex color with background at given alpha."""
        fg = self._hex_to_rgb(hex_color)
        bg = self._hex_to_rgb(COLORS["bg_card"])
        blended = tuple(int(bg[i] + (fg[i] - bg[i]) * alpha) for i in range(3))
        return self._rgb_to_hex(*blended)

    # ── Event handlers ────────────────────────

    def _on_press(self, _event):
        self.is_pressed = True
        self._draw_button(pressed=True)
        self.after(120, self._on_release_anim)

    def _on_release_anim(self):
        if self.is_pressed:
            self.is_pressed = False
            self._draw_button(pressed=False)
            self.command()

    def _on_release(self, _event):
        pass

    def _on_enter(self, _event):
        if not self.is_pressed:
            self._draw_button(hovered=True)

    def _on_leave(self, _event):
        if not self.is_pressed:
            self._draw_button(pressed=False, hovered=False)


# ══════════════════════════════════════════════
#  MAIN APPLICATION WINDOW
# ══════════════════════════════════════════════
class AdvancedCalculatorApp:
    """
    Top-level UI class.
    Builds the window, header, display panel, and button grid.
    Connects UI events to CalculatorLogic.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.logic = CalculatorLogic()

        self._configure_window()
        self._build_header()
        self._build_display()
        self._build_button_grid()
        self._build_footer()
        self._bind_keyboard()

        # Initial render
        self._refresh_display()

    # ── Window setup ─────────────────────────

    def _configure_window(self):
        self.root.title("OIBSIP Advanced Calculator")
        self.root.configure(bg=COLORS["bg_root"])
        self.root.resizable(False, False)

        # Center on screen
        w, h = 420, 720
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Thin card border via outer frame
        outer = tk.Frame(self.root, bg=COLORS["border_card"], padx=1, pady=1)
        outer.pack(fill="both", expand=True, padx=10, pady=10)

        self.main_frame = tk.Frame(outer, bg=COLORS["bg_card"])
        self.main_frame.pack(fill="both", expand=True)

    # ── Header ───────────────────────────────

    def _build_header(self):
        header = tk.Frame(self.main_frame, bg=COLORS["bg_card"], pady=10)
        header.pack(fill="x", padx=18)

        # Icon (unicode calculator symbol on a neon circle)
        icon_canvas = tk.Canvas(header, width=52, height=52,
                                bg=COLORS["bg_card"], highlightthickness=0)
        icon_canvas.pack(pady=(4, 2))
        icon_canvas.create_oval(2, 2, 50, 50,
                                fill=COLORS["bg_display"],
                                outline=COLORS["neon_blue"], width=2)
        icon_canvas.create_text(26, 27, text="⌨",
                                fill=COLORS["neon_cyan"], font=("Segoe UI", 22))

        tk.Label(header, text="OIBSIP Advanced Calculator",
                 bg=COLORS["bg_card"], fg=COLORS["neon_blue"],
                 font=FONT_TITLE).pack()

        tk.Label(header, text="Python Programming Internship Project",
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                 font=FONT_SUBTITLE).pack()

        # Thin separator line
        sep = tk.Canvas(self.main_frame, height=1, bg=COLORS["bg_card"],
                        highlightthickness=0)
        sep.pack(fill="x", padx=18, pady=(4, 0))
        sep.create_line(0, 0, 420, 0, fill=COLORS["border_display"])

    # ── Display panel ─────────────────────────

    def _build_display(self):
        disp_outer = tk.Frame(self.main_frame,
                              bg=COLORS["neon_blue"],   # glow border
                              padx=1, pady=1)
        disp_outer.pack(fill="x", padx=18, pady=12)

        disp_inner = tk.Frame(disp_outer, bg=COLORS["bg_display"], padx=16, pady=12)
        disp_inner.pack(fill="both")

        # Expression label (small, top-right)
        self.expr_var = tk.StringVar(value="")
        self.expr_label = tk.Label(
            disp_inner,
            textvariable=self.expr_var,
            bg=COLORS["bg_display"],
            fg=COLORS["text_secondary"],
            font=FONT_DISPLAY_EXPR,
            anchor="e",
            justify="right",
        )
        self.expr_label.pack(fill="x")

        # Result label (large, main)
        self.result_var = tk.StringVar(value="0")
        self.result_label = tk.Label(
            disp_inner,
            textvariable=self.result_var,
            bg=COLORS["bg_display"],
            fg=COLORS["text_primary"],
            font=FONT_DISPLAY_RESULT,
            anchor="e",
            justify="right",
        )
        self.result_label.pack(fill="x", pady=(4, 0))

    # ── Button grid ───────────────────────────

    def _build_button_grid(self):
        """
        Grid layout restructured to standard 4 columns × 5 rows.
        Eliminates the off-screen cutoff and creates perfectly proportional columns.
        """
        grid_frame = tk.Frame(self.main_frame, bg=COLORS["bg_card"])
        grid_frame.pack(padx=14, pady=4)

        # Updated to a strict 4-column sequence
        buttons = [
            # Row 0 — Functions
            ("C",   self._cmd_clear,      COLORS["bg_btn_accent"], COLORS["neon_pink"],    COLORS["neon_pink"]),
            ("(",   self._cmd_paren,      COLORS["bg_btn_accent"], COLORS["neon_purple"],  COLORS["neon_purple"]),
            (")",   self._cmd_paren,      COLORS["bg_btn_accent"], COLORS["neon_purple"],  COLORS["neon_purple"]),
            ("⌫",  self._cmd_backspace,  COLORS["bg_btn_accent"], COLORS["neon_cyan"],    COLORS["neon_cyan"]),

            # Row 1 — Operations / Modifiers
            ("√",   self._cmd_sqrt,       COLORS["bg_btn_accent"], COLORS["neon_purple"],  COLORS["neon_purple"]),
            ("^",   lambda: self._cmd_op("^"), COLORS["bg_btn_op"], COLORS["neon_cyan"], COLORS["neon_cyan"]),
            ("%",   self._cmd_percent,    COLORS["bg_btn_accent"], COLORS["neon_cyan"],    COLORS["neon_cyan"]),
            ("÷",   lambda: self._cmd_op("÷"), COLORS["bg_btn_op"], COLORS["neon_cyan"], COLORS["neon_cyan"]),

            # Row 2 — Digits 7-9
            ("7",   lambda: self._cmd_digit("7"), COLORS["bg_btn_digit"], COLORS["text_primary"], COLORS["border_card"]),
            ("8",   lambda: self._cmd_digit("8"), COLORS["bg_btn_digit"], COLORS["text_primary"], COLORS["border_card"]),
            ("9",   lambda: self._cmd_digit("9"), COLORS["bg_btn_digit"], COLORS["text_primary"], COLORS["border_card"]),
            ("×",   lambda: self._cmd_op("×"), COLORS["bg_btn_op"], COLORS["neon_cyan"], COLORS["neon_cyan"]),

            # Row 3 — Digits 4-6
            ("4",   lambda: self._cmd_digit("4"), COLORS["bg_btn_digit"], COLORS["text_primary"], COLORS["border_card"]),
            ("5",   lambda: self._cmd_digit("5"), COLORS["bg_btn_digit"], COLORS["text_primary"], COLORS["border_card"]),
            ("6",   lambda: self._cmd_digit("6"), COLORS["bg_btn_digit"], COLORS["text_primary"], COLORS["border_card"]),
            ("-",   lambda: self._cmd_op("-"), COLORS["bg_btn_op"], COLORS["neon_cyan"], COLORS["neon_cyan"]),

            # Row 4 — Digits 1-3
            ("1",   lambda: self._cmd_digit("1"), COLORS["bg_btn_digit"], COLORS["text_primary"], COLORS["border_card"]),
            ("2",   lambda: self._cmd_digit("2"), COLORS["bg_btn_digit"], COLORS["text_primary"], COLORS["border_card"]),
            ("3",   lambda: self._cmd_digit("3"), COLORS["bg_btn_digit"], COLORS["text_primary"], COLORS["border_card"]),
            ("+",   lambda: self._cmd_op("+"), COLORS["bg_btn_op"], COLORS["neon_cyan"], COLORS["neon_cyan"]),
        ]

        row = 0
        col = 0
        PAD = 4

        for (label, cmd, bg, fg, bord) in buttons:
            btn = NeonButton(
                grid_frame, text=label, command=cmd,
                bg_color=bg, fg_color=fg, border_color=bord,
                width=78,
                height=58,
            )
            btn.grid(row=row, column=col, padx=PAD, pady=PAD, sticky="nsew")
            col += 1
            if col >= 4:  # Break rows every 4 columns instead of 5
                col = 0
                row += 1

        # ── Bottom row: 0 (wide, spans 2 columns) + . + = ─────
        bottom = tk.Frame(grid_frame, bg=COLORS["bg_card"])
        bottom.grid(row=row, column=0, columnspan=4, padx=0, pady=PAD, sticky="ew")

        zero_btn = NeonButton(
            bottom, text="0",
            command=lambda: self._cmd_digit("0"),
            bg_color=COLORS["bg_btn_digit"],
            fg_color=COLORS["text_primary"],
            border_color=COLORS["border_card"],
            width=170, height=58,  # Spans across two columns perfectly
        )
        zero_btn.pack(side="left", padx=PAD)

        dot_btn = NeonButton(
            bottom, text=".",
            command=lambda: self._cmd_digit("."),
            bg_color=COLORS["bg_btn_digit"],
            fg_color=COLORS["text_primary"],
            border_color=COLORS["border_card"],
            width=78, height=58,
        )
        dot_btn.pack(side="left", padx=PAD)

        eq_btn = NeonButton(
            bottom, text="=",
            command=self._cmd_equals,
            bg_color="#1a0030",
            fg_color=COLORS["neon_purple"],
            border_color=COLORS["neon_purple"],
            width=78, height=58,
        )
        eq_btn.pack(side="left", padx=PAD)

    # ── Footer ────────────────────────────────

    def _build_footer(self):
        sep = tk.Canvas(self.main_frame, height=1,
                        bg=COLORS["bg_card"], highlightthickness=0)
        sep.pack(fill="x", padx=18, pady=(6, 0))
        sep.create_line(0, 0, 420, 0, fill=COLORS["border_display"])

        tk.Label(
            self.main_frame,
            text="Developed by Antariksh Dilkhush Sawarbandhe",
            bg=COLORS["bg_card"],
            fg=COLORS["text_secondary"],
            font=FONT_FOOTER,
        ).pack(pady=(4, 10))

    # ── Command handlers ─────────────────────

    def _cmd_digit(self, digit: str):
        self.logic.append(digit)
        self._refresh_display()

    def _cmd_op(self, op: str):
        self.logic.append(op)
        self._refresh_display()

    def _cmd_clear(self):
        self.logic.clear()
        self._refresh_display()

    def _cmd_backspace(self):
        self.logic.backspace()
        self._refresh_display()

    def _cmd_equals(self):
        self.logic.evaluate()
        self._refresh_display()

    def _cmd_sqrt(self):
        self.logic.sqrt()
        self._refresh_display()

    def _cmd_percent(self):
        self.logic.percentage()
        self._refresh_display()

    def _cmd_paren(self):
        self.logic.toggle_parens()
        self._refresh_display()

    # ── Display refresh ───────────────────────

    def _refresh_display(self):
        """Push current logic state to the UI labels."""
        expr = self.logic.expression or ""
        self.expr_var.set(expr if len(expr) <= 30 else "…" + expr[-29:])

        result = self.logic.result_text
        if self.logic.error:
            self.result_label.config(
                fg=COLORS["neon_pink"],
                font=("Consolas", 20, "bold"),
            )
        else:
            if len(result) > 12:
                self.result_label.config(
                    fg=COLORS["text_primary"],
                    font=("Consolas", 22, "bold"),
                )
            else:
                self.result_label.config(
                    fg=COLORS["text_primary"],
                    font=FONT_DISPLAY_RESULT,
                )

        self.result_var.set(result)

    # ── Keyboard bindings ─────────────────────

    def _bind_keyboard(self):
        """Map keyboard keys to calculator actions."""
        bindings = {
            "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
            "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
            ".": ".",
            "+": "+", "-": "-", "*": "×", "/": "÷",
            "percent": "%", "^": "^",
            "parenleft": "(", "parenright": ")",
        }

        for key, value in bindings.items():
            self.root.bind(f"<KeyPress-{key}>",
                           lambda e, v=value: self._cmd_digit(v))

        self.root.bind("<Return>",    lambda e: self._cmd_equals())
        self.root.bind("<KP_Enter>",  lambda e: self._cmd_equals())
        self.root.bind("<BackSpace>", lambda e: self._cmd_backspace())
        self.root.bind("<Escape>",    lambda e: self._cmd_clear())


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════
def main():
    root = tk.Tk()
    app = AdvancedCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()