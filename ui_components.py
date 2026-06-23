"""
Reusable Tkinter UI components for the Heart Disease Predictor.
"""

import tkinter as tk
from tkinter import ttk


# ─────────────────────────────────────────────────────────────────
#  SliderField
# ─────────────────────────────────────────────────────────────────
class SliderField(tk.Frame):
    """Label + horizontal slider + live value display."""

    def __init__(self, parent, label: str, min_val, max_val,
                 default, col: int = 0, decimals: int = 0):
        super().__init__(parent, bg="#F8F9FA", padx=8, pady=4)
        self.grid(row=0, column=col, sticky="ew", padx=4)
        parent.columnconfigure(col, weight=1)

        self._decimals = decimals
        self._var = tk.DoubleVar(value=default)

        tk.Label(self, text=label, font=("Helvetica", 10),
                 bg="#F8F9FA", fg="#2C3E50").pack(anchor="w")

        row = tk.Frame(self, bg="#F8F9FA")
        row.pack(fill="x")

        self._slider = ttk.Scale(
            row, from_=min_val, to=max_val,
            variable=self._var, orient="horizontal",
            command=self._on_change
        )
        self._slider.pack(side="left", fill="x", expand=True)

        self._lbl = tk.Label(
            row, text=self._fmt(default),
            font=("Helvetica", 10, "bold"),
            bg="#F8F9FA", fg="#C0392B", width=6
        )
        self._lbl.pack(side="right")

    def _fmt(self, v) -> str:
        return f"{float(v):.{self._decimals}f}"

    def _on_change(self, _=None):
        self._lbl.config(text=self._fmt(self._var.get()))

    def get(self):
        v = self._var.get()
        return round(v, self._decimals) if self._decimals else int(round(v))


# ─────────────────────────────────────────────────────────────────
#  ToggleGroup
# ─────────────────────────────────────────────────────────────────
class ToggleGroup(tk.Frame):
    """Label + a row of mutually exclusive buttons."""

    def __init__(self, parent, label: str, options: list, col: int = 0):
        super().__init__(parent, bg="#F8F9FA", padx=8, pady=4)
        self.grid(row=0, column=col, sticky="ew", padx=4)
        parent.columnconfigure(col, weight=1)

        self._value = options[0]
        self._buttons = {}

        tk.Label(self, text=label, font=("Helvetica", 10),
                 bg="#F8F9FA", fg="#2C3E50").pack(anchor="w")

        btn_row = tk.Frame(self, bg="#F8F9FA")
        btn_row.pack(fill="x")

        for opt in options:
            btn = tk.Button(
                btn_row, text=opt,
                font=("Helvetica", 10),
                relief="flat", cursor="hand2",
                padx=8, pady=4,
                command=lambda o=opt: self._select(o)
            )
            btn.pack(side="left", padx=2)
            self._buttons[opt] = btn

        self._select(options[0])

    def _select(self, value):
        self._value = value
        for opt, btn in self._buttons.items():
            if opt == value:
                btn.config(bg="#C0392B", fg="white")
            else:
                btn.config(bg="#ECF0F1", fg="#2C3E50")

    def get(self) -> str:
        return self._value


# ─────────────────────────────────────────────────────────────────
#  DropdownField
# ─────────────────────────────────────────────────────────────────
class DropdownField(tk.Frame):
    """Label + ttk.Combobox dropdown."""

    def __init__(self, parent, label: str, options: list, col: int = 0):
        super().__init__(parent, bg="#F8F9FA", padx=8, pady=4)
        self.grid(row=0, column=col, sticky="ew", padx=4)
        parent.columnconfigure(col, weight=1)

        tk.Label(self, text=label, font=("Helvetica", 10),
                 bg="#F8F9FA", fg="#2C3E50").pack(anchor="w")

        self._var = tk.StringVar(value=options[0])
        combo = ttk.Combobox(
            self, textvariable=self._var,
            values=options, state="readonly",
            font=("Helvetica", 10)
        )
        combo.pack(fill="x")

    def get(self) -> str:
        return self._var.get()


# ─────────────────────────────────────────────────────────────────
#  RiskMeter  (canvas-drawn gauge)
# ─────────────────────────────────────────────────────────────────
class RiskMeter(tk.Frame):
    """Horizontal coloured bar showing risk percentage."""

    def __init__(self, parent, pct: int, level: str, color: str):
        super().__init__(parent, bg="white",
                         relief="solid", bd=1, padx=12, pady=12)

        header = tk.Frame(self, bg="white")
        header.pack(fill="x")

        tk.Label(header, text=f"{level} Risk",
                 font=("Helvetica", 16, "bold"),
                 bg="white", fg=color).pack(side="left")
        tk.Label(header, text=f"{pct}% estimated probability",
                 font=("Helvetica", 11),
                 bg="white", fg="#7F8C8D").pack(side="right")

        # Bar background
        bar_bg = tk.Canvas(self, height=14, bg="white",
                           highlightthickness=0)
        bar_bg.pack(fill="x", pady=(8, 2))
        bar_bg.update_idletasks()
        w = bar_bg.winfo_width() or 600

        # Gradient background (Low → Very High)
        bar_bg.create_rectangle(0, 2, w, 12, fill="#ECF0F1", outline="")
        fill_w = max(4, int(w * pct / 100))
        bar_bg.create_rectangle(0, 2, fill_w, 12, fill=color, outline="")

        # Scale labels
        scale = tk.Frame(self, bg="white")
        scale.pack(fill="x")
        for lbl in ("Low", "Moderate", "High", "Very High"):
            tk.Label(scale, text=lbl, font=("Helvetica", 8),
                     bg="white", fg="#BDC3C7").pack(side="left", expand=True)


# ─────────────────────────────────────────────────────────────────
#  MetricCard
# ─────────────────────────────────────────────────────────────────
class MetricCard(tk.Frame):
    """Small summary card with a muted label and big value."""

    def __init__(self, parent, label: str, value: str, color: str = "#2C3E50"):
        super().__init__(parent, bg="#F4F6F7",
                         relief="flat", padx=12, pady=10)

        tk.Label(self, text=label.upper(),
                 font=("Helvetica", 9),
                 bg="#F4F6F7", fg="#95A5A6").pack()
        tk.Label(self, text=value,
                 font=("Helvetica", 18, "bold"),
                 bg="#F4F6F7", fg=color).pack()
