"""
Heart Disease Risk Prediction - Main GUI Application
Author: Your Name
GitHub: https://github.com/yourusername/heart-disease-predictor
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from src.predictor import HeartDiseasePredictor
from src.ui_components import (
    SliderField, ToggleGroup, DropdownField, MetricCard, RiskMeter
)


class HeartDiseasePredictorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Heart Disease Risk Predictor")
        self.geometry("900x750")
        self.resizable(True, True)
        self.configure(bg="#F8F9FA")

        self.predictor = HeartDiseasePredictor()
        self._build_ui()

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────────
        header = tk.Frame(self, bg="#C0392B", pady=16)
        header.pack(fill="x")

        tk.Label(
            header,
            text="❤  Heart Disease Risk Predictor",
            font=("Helvetica", 20, "bold"),
            bg="#C0392B", fg="white"
        ).pack()
        tk.Label(
            header,
            text="Enter clinical parameters to assess cardiovascular risk",
            font=("Helvetica", 11),
            bg="#C0392B", fg="#FADBD8"
        ).pack()

        # ── Scrollable canvas ────────────────────────────────────────
        outer = tk.Frame(self, bg="#F8F9FA")
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg="#F8F9FA", highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.scroll_frame = tk.Frame(canvas, bg="#F8F9FA")
        canvas_window = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)

        self.scroll_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._build_form(self.scroll_frame)

    def _build_form(self, parent):
        pad = {"padx": 24, "pady": 6}

        # ── Demographics ─────────────────────────────────────────────
        self._section(parent, "Demographics")
        demo = tk.Frame(parent, bg="#F8F9FA")
        demo.pack(fill="x", **pad)

        self.age    = SliderField(demo, "Age (years)", 20, 85, 45, col=0)
        self.bmi    = SliderField(demo, "BMI", 15.0, 50.0, 26.0, col=1, decimals=1)
        self.sex    = ToggleGroup(demo, "Sex", ["Male", "Female"], col=2)

        # ── Vitals & Labs ────────────────────────────────────────────
        self._section(parent, "Vitals & Labs")
        vitals = tk.Frame(parent, bg="#F8F9FA")
        vitals.pack(fill="x", **pad)

        self.bp     = SliderField(vitals, "Resting BP (mmHg)", 80, 200, 120, col=0)
        self.chol   = SliderField(vitals, "Cholesterol (mg/dL)", 100, 400, 220, col=1)
        self.hr     = SliderField(vitals, "Resting HR (bpm)", 40, 200, 72, col=2)

        vitals2 = tk.Frame(parent, bg="#F8F9FA")
        vitals2.pack(fill="x", **pad)

        self.maxhr  = SliderField(vitals2, "Max HR achieved", 60, 220, 150, col=0)
        self.st_dep = SliderField(vitals2, "ST Depression", 0.0, 6.0, 1.0, col=1, decimals=1)
        self.fbs    = ToggleGroup(vitals2, "Fasting Sugar >120", ["No", "Yes"], col=2)

        # ── Clinical Findings ────────────────────────────────────────
        self._section(parent, "Clinical Findings")
        clin = tk.Frame(parent, bg="#F8F9FA")
        clin.pack(fill="x", **pad)

        self.cp     = DropdownField(clin, "Chest Pain Type",
                                    ["Typical angina", "Atypical angina",
                                     "Non-anginal", "Asymptomatic"], col=0)
        self.ecg    = DropdownField(clin, "Resting ECG",
                                    ["Normal", "ST-T abnormality",
                                     "Left ventricular hypertrophy"], col=1)
        self.slope  = DropdownField(clin, "ST Slope",
                                    ["Upsloping", "Flat", "Downsloping"], col=2)

        clin2 = tk.Frame(parent, bg="#F8F9FA")
        clin2.pack(fill="x", **pad)

        self.exang   = ToggleGroup(clin2, "Exercise Angina", ["No", "Yes"], col=0)
        self.vessels = ToggleGroup(clin2, "Major Vessels (0–3)",
                                   ["0", "1", "2", "3"], col=1)
        self.thal    = DropdownField(clin2, "Thalassemia",
                                     ["Normal", "Fixed defect",
                                      "Reversible defect"], col=2)

        # ── Lifestyle & History ──────────────────────────────────────
        self._section(parent, "Lifestyle & History")
        life = tk.Frame(parent, bg="#F8F9FA")
        life.pack(fill="x", **pad)

        self.smoking  = DropdownField(life, "Smoking Status",
                                      ["Never", "Former smoker",
                                       "Current smoker"], col=0)
        self.diabetes = ToggleGroup(life, "Diabetes", ["No", "Yes"], col=1)
        self.famhist  = ToggleGroup(life, "Family History CVD", ["No", "Yes"], col=2)

        # ── Predict Button ───────────────────────────────────────────
        btn_frame = tk.Frame(parent, bg="#F8F9FA", pady=16)
        btn_frame.pack(fill="x", padx=24)

        self.predict_btn = tk.Button(
            btn_frame,
            text="  Assess Risk",
            font=("Helvetica", 14, "bold"),
            bg="#C0392B", fg="white",
            activebackground="#A93226",
            relief="flat", cursor="hand2",
            padx=32, pady=12,
            command=self._run_prediction
        )
        self.predict_btn.pack(side="left")

        self.status_lbl = tk.Label(
            btn_frame, text="", font=("Helvetica", 11),
            bg="#F8F9FA", fg="#7F8C8D"
        )
        self.status_lbl.pack(side="left", padx=16)

        # ── Result Panel ─────────────────────────────────────────────
        self.result_frame = tk.Frame(parent, bg="#F8F9FA")
        self.result_frame.pack(fill="x", padx=24, pady=(0, 24))

    # ----------------------------------------------------------------
    def _section(self, parent, title):
        f = tk.Frame(parent, bg="#F8F9FA")
        f.pack(fill="x", padx=24, pady=(14, 2))
        tk.Label(
            f, text=title.upper(),
            font=("Helvetica", 9, "bold"),
            bg="#F8F9FA", fg="#95A5A6"
        ).pack(side="left")
        ttk.Separator(f, orient="horizontal").pack(side="left", fill="x", expand=True, padx=8)

    def _collect(self):
        return {
            "age":      self.age.get(),
            "sex":      self.sex.get(),
            "bmi":      self.bmi.get(),
            "bp":       self.bp.get(),
            "chol":     self.chol.get(),
            "hr":       self.hr.get(),
            "maxhr":    self.maxhr.get(),
            "st_dep":   self.st_dep.get(),
            "fbs":      self.fbs.get(),
            "exang":    self.exang.get(),
            "vessels":  int(self.vessels.get()),
            "diabetes": self.diabetes.get(),
            "famhist":  self.famhist.get(),
            "cp":       self.cp.get(),
            "ecg":      self.ecg.get(),
            "slope":    self.slope.get(),
            "thal":     self.thal.get(),
            "smoking":  self.smoking.get(),
        }

    def _run_prediction(self):
        self.predict_btn.config(state="disabled", text="  Assessing…")
        self.status_lbl.config(text="Analyzing parameters…")

        data = self._collect()

        def worker():
            try:
                result = self.predictor.predict(data)
                self.after(0, lambda: self._show_result(result))
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("Error", str(exc)))
            finally:
                self.after(0, self._reset_btn)

        threading.Thread(target=worker, daemon=True).start()

    def _reset_btn(self):
        self.predict_btn.config(state="normal", text="  Assess Risk")
        self.status_lbl.config(text="")

    def _show_result(self, result):
        for w in self.result_frame.winfo_children():
            w.destroy()

        pct   = result["risk_percent"]
        level = result["risk_level"]
        color = {"Low": "#27AE60", "Moderate": "#F39C12",
                 "High": "#E67E22", "Very High": "#C0392B"}.get(level, "#C0392B")

        # Risk meter
        RiskMeter(self.result_frame, pct, level, color).pack(fill="x", pady=(0, 12))

        # Metric cards
        card_row = tk.Frame(self.result_frame, bg="#F8F9FA")
        card_row.pack(fill="x", pady=(0, 12))

        metrics = [
            ("Risk %",   f"{pct}%",        color),
            ("Level",    level,             color),
            ("Factors",  str(len(result.get("factors", []))), "#2C3E50"),
        ]
        for i, (lbl, val, col) in enumerate(metrics):
            MetricCard(card_row, lbl, val, col).grid(row=0, column=i, padx=6, sticky="ew")
            card_row.columnconfigure(i, weight=1)

        # Summary
        if result.get("summary"):
            tk.Label(
                self.result_frame,
                text=result["summary"],
                font=("Helvetica", 11),
                bg="#FDFEFE",
                fg="#2C3E50",
                wraplength=820,
                justify="left",
                relief="flat",
                bd=0,
                padx=12, pady=10
            ).pack(fill="x", pady=(0, 10))

        # Factors list
        if result.get("factors"):
            tk.Label(
                self.result_frame,
                text="Key Risk Factors",
                font=("Helvetica", 10, "bold"),
                bg="#F8F9FA", fg="#7F8C8D"
            ).pack(anchor="w")

            impact_colors = {
                "Protective":      "#27AE60",
                "Mild risk":       "#F39C12",
                "Moderate risk":   "#E67E22",
                "High risk":       "#C0392B",
            }
            for f in result["factors"]:
                row = tk.Frame(self.result_frame, bg="white",
                               relief="flat", bd=0, pady=6, padx=10)
                row.pack(fill="x", pady=2)

                icol = impact_colors.get(f["impact"], "#7F8C8D")
                dot = tk.Canvas(row, width=10, height=10, bg="white",
                                highlightthickness=0)
                dot.create_oval(1, 1, 9, 9, fill=icol, outline="")
                dot.pack(side="left", padx=(0, 8))

                tk.Label(row, text=f["label"], font=("Helvetica", 11),
                         bg="white", fg="#2C3E50").pack(side="left")
                tk.Label(row, text=f["impact"], font=("Helvetica", 10, "bold"),
                         bg="white", fg=icol).pack(side="right")

        # Disclaimer
        tk.Label(
            self.result_frame,
            text="⚠  For educational purposes only. Not a substitute for professional medical advice.",
            font=("Helvetica", 9),
            bg="#FDECEA", fg="#C0392B",
            pady=8, padx=10,
            wraplength=820
        ).pack(fill="x", pady=(12, 0))


if __name__ == "__main__":
    app = HeartDiseasePredictorApp()
    app.mainloop()
