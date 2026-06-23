"""
Heart Disease Risk Predictor
Uses rule-based scoring + optional ML model (sklearn).
"""

import json
import os


class HeartDiseasePredictor:
    """
    Rule-based cardiovascular risk scorer based on established
    clinical guidelines (Framingham, ACC/AHA).

    Optionally loads a trained sklearn model from models/model.pkl
    if it exists; otherwise falls back to the rule engine.
    """

    def __init__(self):
        self.model = None
        self._try_load_model()

    # ------------------------------------------------------------------ #
    #  Model loading (optional)
    # ------------------------------------------------------------------ #
    def _try_load_model(self):
        model_path = os.path.join(
            os.path.dirname(__file__), "..", "models", "model.pkl"
        )
        if os.path.exists(model_path):
            try:
                import pickle
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                print("[Predictor] Loaded sklearn model from models/model.pkl")
            except Exception as e:
                print(f"[Predictor] Could not load model: {e}")

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #
    def predict(self, data: dict) -> dict:
        """
        Parameters
        ----------
        data : dict  — collected from GUI (see app.py _collect())

        Returns
        -------
        dict with keys:
            risk_percent  int  0-100
            risk_level    str  Low | Moderate | High | Very High
            factors       list[{label, impact}]
            summary       str
        """
        if self.model is not None:
            return self._ml_predict(data)
        return self._rule_predict(data)

    # ------------------------------------------------------------------ #
    #  Rule-based engine
    # ------------------------------------------------------------------ #
    def _rule_predict(self, d: dict) -> dict:
        score = 0
        factors = []

        # — Age —
        age = d["age"]
        if age >= 65:
            score += 20; factors.append({"label": "Age ≥ 65", "impact": "High risk"})
        elif age >= 55:
            score += 12; factors.append({"label": "Age 55–64", "impact": "Moderate risk"})
        elif age >= 45:
            score += 6;  factors.append({"label": "Age 45–54", "impact": "Mild risk"})

        # — Sex —
        if d["sex"] == "Male":
            score += 6; factors.append({"label": "Male sex", "impact": "Mild risk"})

        # — BMI —
        bmi = d["bmi"]
        if bmi >= 35:
            score += 10; factors.append({"label": f"BMI {bmi:.1f} (obese)", "impact": "High risk"})
        elif bmi >= 30:
            score += 6;  factors.append({"label": f"BMI {bmi:.1f} (overweight)", "impact": "Moderate risk"})
        elif bmi < 18.5:
            score += 3;  factors.append({"label": f"BMI {bmi:.1f} (underweight)", "impact": "Mild risk"})

        # — Blood pressure —
        bp = d["bp"]
        if bp >= 180:
            score += 18; factors.append({"label": f"BP {bp} mmHg (stage 2 HTN)", "impact": "High risk"})
        elif bp >= 140:
            score += 12; factors.append({"label": f"BP {bp} mmHg (stage 1 HTN)", "impact": "Moderate risk"})
        elif bp >= 120:
            score += 4;  factors.append({"label": f"BP {bp} mmHg (elevated)", "impact": "Mild risk"})
        else:
            factors.append({"label": f"BP {bp} mmHg (normal)", "impact": "Protective"})

        # — Cholesterol —
        chol = d["chol"]
        if chol >= 280:
            score += 14; factors.append({"label": f"Cholesterol {chol} mg/dL", "impact": "High risk"})
        elif chol >= 240:
            score += 8;  factors.append({"label": f"Cholesterol {chol} mg/dL", "impact": "Moderate risk"})
        elif chol >= 200:
            score += 3;  factors.append({"label": f"Cholesterol {chol} mg/dL", "impact": "Mild risk"})
        else:
            factors.append({"label": f"Cholesterol {chol} mg/dL", "impact": "Protective"})

        # — Fasting blood sugar —
        if d["fbs"] == "Yes":
            score += 8; factors.append({"label": "Fasting sugar > 120 mg/dL", "impact": "Moderate risk"})

        # — Smoking —
        smoking = d["smoking"]
        if smoking == "Current smoker":
            score += 14; factors.append({"label": "Current smoker", "impact": "High risk"})
        elif smoking == "Former smoker":
            score += 5;  factors.append({"label": "Former smoker", "impact": "Mild risk"})
        else:
            factors.append({"label": "Non-smoker", "impact": "Protective"})

        # — Diabetes —
        if d["diabetes"] == "Yes":
            score += 10; factors.append({"label": "Diabetes", "impact": "Moderate risk"})

        # — Family history —
        if d["famhist"] == "Yes":
            score += 8; factors.append({"label": "Family history of CVD", "impact": "Moderate risk"})

        # — Chest pain type —
        cp_map = {
            "Asymptomatic":   (14, "High risk"),
            "Non-anginal":    (6,  "Moderate risk"),
            "Atypical angina":(3,  "Mild risk"),
            "Typical angina": (0,  "Protective"),
        }
        cp_score, cp_impact = cp_map.get(d["cp"], (0, "Protective"))
        score += cp_score
        factors.append({"label": f"Chest pain: {d['cp']}", "impact": cp_impact})

        # — Max HR (lower = worse for age) —
        expected_max = 220 - age
        hr_ratio = d["maxhr"] / expected_max
        if hr_ratio < 0.65:
            score += 10; factors.append({"label": "Low max HR achieved", "impact": "High risk"})
        elif hr_ratio > 0.85:
            factors.append({"label": "Good max HR achieved", "impact": "Protective"})

        # — Exercise angina —
        if d["exang"] == "Yes":
            score += 10; factors.append({"label": "Exercise-induced angina", "impact": "High risk"})

        # — ST depression —
        st = d["st_dep"]
        if st >= 3:
            score += 12; factors.append({"label": f"ST depression {st:.1f}", "impact": "High risk"})
        elif st >= 1.5:
            score += 6;  factors.append({"label": f"ST depression {st:.1f}", "impact": "Moderate risk"})

        # — ST slope —
        slope_map = {"Downsloping": 10, "Flat": 5, "Upsloping": 0}
        score += slope_map.get(d["slope"], 0)

        # — Major vessels —
        vessels = d["vessels"]
        if vessels >= 3:
            score += 16; factors.append({"label": f"{vessels} major vessels affected", "impact": "High risk"})
        elif vessels == 2:
            score += 10; factors.append({"label": f"{vessels} major vessels affected", "impact": "Moderate risk"})
        elif vessels == 1:
            score += 5;  factors.append({"label": f"{vessels} major vessel affected", "impact": "Mild risk"})
        else:
            factors.append({"label": "No major vessels affected", "impact": "Protective"})

        # — Thalassemia —
        thal_map = {
            "Reversible defect": (12, "High risk"),
            "Fixed defect":      (6,  "Moderate risk"),
            "Normal":            (0,  "Protective"),
        }
        t_score, t_impact = thal_map.get(d["thal"], (0, "Protective"))
        score += t_score
        factors.append({"label": f"Thalassemia: {d['thal']}", "impact": t_impact})

        # — ECG —
        ecg_map = {
            "Left ventricular hypertrophy": (8, "Moderate risk"),
            "ST-T abnormality":             (4, "Mild risk"),
            "Normal":                        (0, "Protective"),
        }
        e_score, e_impact = ecg_map.get(d["ecg"], (0, "Protective"))
        score += e_score
        factors.append({"label": f"ECG: {d['ecg']}", "impact": e_impact})

        # ── Normalise to 0-100 ──────────────────────────────────────
        max_possible = 200
        risk_pct = min(100, int((score / max_possible) * 100))

        # ── Risk level ──────────────────────────────────────────────
        if risk_pct < 20:
            level = "Low"
        elif risk_pct < 45:
            level = "Moderate"
        elif risk_pct < 70:
            level = "High"
        else:
            level = "Very High"

        # ── Top factors (keep most impactful, max 6) ────────────────
        impact_order = {"High risk": 0, "Moderate risk": 1, "Mild risk": 2, "Protective": 3}
        top_factors = sorted(factors, key=lambda f: impact_order.get(f["impact"], 9))[:6]

        # ── Summary ─────────────────────────────────────────────────
        summary = self._generate_summary(d, risk_pct, level, top_factors)

        return {
            "risk_percent": risk_pct,
            "risk_level":   level,
            "factors":      top_factors,
            "summary":      summary,
        }

    # ------------------------------------------------------------------ #
    #  ML prediction (sklearn)
    # ------------------------------------------------------------------ #
    def _ml_predict(self, d: dict) -> dict:
        features = self._encode_features(d)
        prob = self.model.predict_proba([features])[0][1]
        risk_pct = int(prob * 100)

        if risk_pct < 20:   level = "Low"
        elif risk_pct < 45: level = "Moderate"
        elif risk_pct < 70: level = "High"
        else:               level = "Very High"

        # Fall back to rule engine for factor explanation
        rule_result = self._rule_predict(d)
        return {
            "risk_percent": risk_pct,
            "risk_level":   level,
            "factors":      rule_result["factors"],
            "summary":      self._generate_summary(d, risk_pct, level, rule_result["factors"]),
        }

    def _encode_features(self, d: dict) -> list:
        """Encode GUI values into a flat numeric feature vector."""
        return [
            d["age"],
            1 if d["sex"] == "Male" else 0,
            d["bmi"],
            d["bp"],
            d["chol"],
            d["hr"],
            d["maxhr"],
            d["st_dep"],
            1 if d["fbs"] == "Yes" else 0,
            1 if d["exang"] == "Yes" else 0,
            d["vessels"],
            1 if d["diabetes"] == "Yes" else 0,
            1 if d["famhist"] == "Yes" else 0,
            ["Typical angina","Atypical angina","Non-anginal","Asymptomatic"].index(d["cp"]),
            ["Normal","ST-T abnormality","Left ventricular hypertrophy"].index(d["ecg"]),
            ["Upsloping","Flat","Downsloping"].index(d["slope"]),
            ["Normal","Fixed defect","Reversible defect"].index(d["thal"]),
            ["Never","Former smoker","Current smoker"].index(d["smoking"]),
        ]

    # ------------------------------------------------------------------ #
    #  Summary text
    # ------------------------------------------------------------------ #
    def _generate_summary(self, d, pct, level, factors):
        top_risk = [f["label"] for f in factors if f["impact"] in ("High risk", "Moderate risk")]
        protective = [f["label"] for f in factors if f["impact"] == "Protective"]

        parts = [f"This {d['age']}-year-old {d['sex'].lower()} has an estimated {pct}% "
                 f"cardiovascular risk, classified as {level}."]

        if top_risk:
            parts.append(f"Key contributing factors include: {', '.join(top_risk[:3])}.")
        if protective:
            parts.append(f"Protective factors: {', '.join(protective[:2])}.")

        return " ".join(parts)
