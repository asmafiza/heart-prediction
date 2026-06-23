import streamlit as st
import time
from src.predictor import HeartDiseasePredictor

# -- Page Configuration --
st.set_page_config(
    page_title="Heart Disease Risk Predictor",
    page_icon="❤️",
    layout="centered"
)

# Initialize the predictor back-end
@st.cache_resource
def load_predictor():
    return HeartDiseasePredictor()

predictor = load_predictor()

# -- Header Area --
st.title("❤️ Heart Disease Risk Predictor")
st.markdown("Enter clinical parameters to assess cardiovascular risk")
st.write("---")

# -- Form Layout --
with st.form("risk_assessment_form"):
    
    # 1. Demographics Section
    st.subheader("DEMOGRAPHICS")
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.slider("Age (years)", 20, 85, 45)
    with col2:
        bmi = st.slider("BMI", 15.0, 50.0, 26.0, step=0.1)
    with col3:
        sex = st.radio("Sex", ["Male", "Female"])

    # 2. Vitals & Labs Section
    st.subheader("VITALS & LABS")
    col1, col2, col3 = st.columns(3)
    with col1:
        bp = st.slider("Resting BP (mmHg)", 80, 200, 120)
    with col2:
        chol = st.slider("Cholesterol (mg/dL)", 100, 400, 220)
    with col3:
        hr = st.slider("Resting HR (bpm)", 40, 200, 72)

    col1, col2, col3 = st.columns(3)
    with col1:
        maxhr = st.slider("Max HR achieved", 60, 220, 150)
    with col2:
        st_dep = st.slider("ST Depression", 0.0, 6.0, 1.0, step=0.1)
    with col3:
        fbs = st.radio("Fasting Sugar > 120 mg/dL", ["No", "Yes"])

    # 3. Clinical Findings Section
    st.subheader("CLINICAL FINDINGS")
    col1, col2, col3 = st.columns(3)
    with col1:
        cp = st.selectbox("Chest Pain Type", [
            "Typical angina", "Atypical angina", "Non-anginal", "Asymptomatic"
        ])
    with col2:
        ecg = st.selectbox("Resting ECG", [
            "Normal", "ST-T abnormality", "Left ventricular hypertrophy"
        ])
    with col3:
        slope = st.selectbox("ST Slope", ["Upsloping", "Flat", "Downsloping"])

    col1, col2, col3 = st.columns(3)
    with col1:
        exang = st.radio("Exercise Angina", ["No", "Yes"])
    with col2:
        vessels = st.radio("Major Vessels (0–3)", ["0", "1", "2", "3"])
    with col3:
        thal = st.selectbox("Thalassemia", [
            "Normal", "Fixed defect", "Reversible defect"
        ])

    # 4. Lifestyle & History Section
    st.subheader("LIFESTYLE & HISTORY")
    col1, col2, col3 = st.columns(3)
    with col1:
        smoking = st.selectbox("Smoking Status", ["Never", "Former smoker", "Current smoker"])
    with col2:
        diabetes = st.radio("Diabetes", ["No", "Yes"])
    with col3:
        famhist = st.radio("Family History CVD", ["No", "Yes"])

    # Submit Button
    submit_btn = st.form_submit_button("Assess Risk", type="primary")

# -- Handle Prediction Execution --
if submit_btn:
    # Bundle data identically to the original _collect() method
    data = {
        "age": age, "sex": sex, "bmi": bmi, "bp": bp, "chol": chol, "hr": hr,
        "maxhr": maxhr, "st_dep": st_dep, "fbs": fbs, "exang": exang,
        "vessels": int(vessels), "diabetes": diabetes, "famhist": famhist,
        "cp": cp, "ecg": ecg, "slope": slope, "thal": thal, "smoking": smoking,
    }
    
    with st.spinner("Analyzing parameters..."):
        try:
            # Execute backend prediction
            result = predictor.predict(data)
            
            # Extract values
            pct = result["risk_percent"]
            level = result["risk_level"]
            
            # Display Metrics
            st.write("---")
            st.subheader("Assessment Results")
            
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Risk Percentage", f"{pct}%")
            m_col2.metric("Risk Level", level)
            m_col3.metric("Key Risk Factors", len(result.get("factors", [])))
            
            # Summary Summary
            if result.get("summary"):
                st.info(result["summary"])
                
            # Key Factors Display
            if result.get("factors"):
                st.markdown("### Key Risk Factors")
                for f in result["factors"]:
                    st.markdown(f"• **{f['label']}**: {f['impact']}")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# -- Disclaimer --
st.write("---")
st.caption("⚠️ For educational purposes only. Not a substitute for professional medical advice.")
