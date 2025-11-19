import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Hypertension Management System",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .risk-low {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .risk-moderate {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    .risk-high {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}

# Sidebar navigation
st.sidebar.title("🏥 Navigation")
page = st.sidebar.radio(
    "Select Section",
    ["Home", "Patient Assessment", "Treatment Options", "Diet Advice", "Exercise Plan", "Reports"]
)

# Helper Functions
def calculate_bmi(weight, height):
    """Calculate BMI from weight (kg) and height (cm)"""
    height_m = height / 100
    return round(weight / (height_m ** 2), 2)

def classify_bp(systolic, diastolic):
    """Classify blood pressure"""
    if systolic < 120 and diastolic < 80:
        return "Normal", "low"
    elif systolic < 130 and diastolic < 80:
        return "Elevated", "moderate"
    elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
        return "Stage 1 Hypertension", "moderate"
    elif systolic >= 140 or diastolic >= 90:
        return "Stage 2 Hypertension", "high"
    elif systolic >= 180 or diastolic >= 120:
        return "Hypertensive Crisis - EMERGENCY", "high"
    return "Unknown", "moderate"

def calculate_risk_score(data):
    """Calculate cardiovascular risk score"""
    score = 0
    
    # Age factor
    if data.get('age', 0) > 65:
        score += 3
    elif data.get('age', 0) > 55:
        score += 2
    elif data.get('age', 0) > 45:
        score += 1
    
    # BMI factor
    bmi = data.get('bmi', 0)
    if bmi >= 30:
        score += 2
    elif bmi >= 25:
        score += 1
    
    # Comorbidities
    if data.get('diabetes'):
        score += 3
    if data.get('cad'):
        score += 3
    if data.get('ckd'):
        score += 2
    if data.get('smoking'):
        score += 2
    
    # BP classification
    bp_class, _ = classify_bp(data.get('systolic', 120), data.get('diastolic', 80))
    if "Crisis" in bp_class:
        score += 5
    elif "Stage 2" in bp_class:
        score += 3
    elif "Stage 1" in bp_class:
        score += 2
    
    return score

def get_risk_category(score):
    """Determine risk category based on score"""
    if score <= 3:
        return "Low Risk", "low"
    elif score <= 7:
        return "Moderate Risk", "moderate"
    elif score <= 12:
        return "High Risk", "high"
    else:
        return "Very High Risk", "high"

# HOME PAGE
if page == "Home":
    st.markdown('<h1 class="main-header">🩺 Hypertension Management System</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📋 **Comprehensive Assessment**\n\nComplete patient evaluation with risk stratification")
    
    with col2:
        st.success("💊 **Treatment Planning**\n\nEvidence-based medication and management strategies")
    
    with col3:
        st.warning("🥗 **Lifestyle Management**\n\nPersonalized diet and exercise recommendations")
    
    st.markdown("---")
    
    st.markdown("### 📊 About This System")
    st.write("""
    This comprehensive hypertension management system helps healthcare providers:
    
    - **Assess** patients using standardized protocols
    - **Identify** modifiable and non-modifiable risk factors
    - **Screen** for secondary hypertension
    - **Plan** appropriate treatment strategies
    - **Provide** personalized lifestyle recommendations
    - **Monitor** patient progress over time
    
    Navigate using the sidebar to begin patient assessment.
    """)
    
    st.markdown("---")
    st.info("⚠️ **Emergency Protocol**: Any patient with BP ≥180/120 mmHg with symptoms requires immediate emergency referral")

# PATIENT ASSESSMENT PAGE
elif page == "Patient Assessment":
    st.markdown('<h1 class="main-header">📋 Patient Assessment</h1>', unsafe_allow_html=True)
    
    tabs = st.tabs(["Demographics & Vitals", "Medical History", "Risk Factors", "Secondary HTN Screening", "Assessment Summary"])
    
    # Tab 1: Demographics & Vitals
    with tabs[0]:
        st.markdown('<div class="section-header">Patient Demographics</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            patient_name = st.text_input("Patient Name", key="patient_name")
            age = st.number_input("Age (years)", min_value=1, max_value=120, value=45, key="age")
            sex = st.selectbox("Sex", ["Male", "Female"], key="sex")
        
        with col2:
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.1, key="weight")
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.1, key="height")
            waist = st.number_input("Waist Circumference (cm)", min_value=50.0, max_value=200.0, value=85.0, step=0.1, key="waist")
        
        # Calculate BMI
        bmi = calculate_bmi(weight, height)
        st.metric("Calculated BMI", f"{bmi} kg/m²")
        
        if bmi < 18.5:
            st.info("Underweight")
        elif 18.5 <= bmi < 25:
            st.success("Normal weight")
        elif 25 <= bmi < 30:
            st.warning("Overweight")
        else:
            st.error("Obese")
        
        st.markdown('<div class="section-header">Vital Signs</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            systolic = st.number_input("Systolic BP (mmHg)", min_value=70, max_value=250, value=130, key="systolic")
        
        with col2:
            diastolic = st.number_input("Diastolic BP (mmHg)", min_value=40, max_value=150, value=85, key="diastolic")
        
        with col3:
            hr = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, value=75, key="hr")
        
        # BP Classification
        bp_class, bp_risk = classify_bp(systolic, diastolic)
        
        if bp_risk == "low":
            st.success(f"**Blood Pressure Classification:** {bp_class}")
        elif bp_risk == "moderate":
            st.warning(f"**Blood Pressure Classification:** {bp_class}")
        else:
            st.error(f"**Blood Pressure Classification:** {bp_class}")
        
        if systolic >= 180 or diastolic >= 120:
            st.error("⚠️ **EMERGENCY**: Patient requires immediate emergency referral!")
        
        duration_htn = st.number_input("Duration of Hypertension (years)", min_value=0, max_value=50, value=0, key="duration_htn")
    
    # Tab 2: Medical History
    with tabs[1]:
        st.markdown('<div class="section-header">Comorbidities</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            diabetes = st.checkbox("Diabetes Mellitus", key="diabetes")
            if diabetes:
                hba1c = st.number_input("HbA1c (%)", min_value=4.0, max_value=15.0, value=6.5, step=0.1, key="hba1c")
            
            cad = st.checkbox("Coronary Artery Disease", key="cad")
            cva = st.checkbox("Cerebrovascular Accident (Stroke)", key="cva")
            ckd = st.checkbox("Chronic Kidney Disease", key="ckd")
            if ckd:
                ckd_stage = st.selectbox("CKD Stage", ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5"], key="ckd_stage")
        
        with col2:
            dyslipidemia = st.checkbox("Dyslipidemia", key="dyslipidemia")
            if dyslipidemia:
                total_chol = st.number_input("Total Cholesterol (mg/dL)", min_value=100, max_value=500, value=200, key="total_chol")
                ldl = st.number_input("LDL (mg/dL)", min_value=50, max_value=300, value=130, key="ldl")
                hdl = st.number_input("HDL (mg/dL)", min_value=20, max_value=100, value=45, key="hdl")
            
            thyroid = st.checkbox("Thyroid Disorder", key="thyroid")
            if thyroid:
                thyroid_type = st.selectbox("Type", ["Hypothyroidism", "Hyperthyroidism"], key="thyroid_type")
            
            lvh = st.checkbox("Left Ventricular Hypertrophy", key="lvh")
        
        st.markdown('<div class="section-header">Family History</div>', unsafe_allow_html=True)
        
        fh_htn = st.checkbox("Family History of Hypertension", key="fh_htn")
        fh_cad = st.checkbox("Family History of CAD", key="fh_cad")
        fh_stroke = st.checkbox("Family History of Stroke", key="fh_stroke")
        fh_kidney = st.checkbox("Family History of Kidney Disease", key="fh_kidney")
    
    # Tab 3: Risk Factors
    with tabs[2]:
        st.markdown('<div class="section-header">Modifiable Risk Factors</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            smoking = st.checkbox("Current Smoker", key="smoking")
            if smoking:
                cigs_per_day = st.number_input("Cigarettes per day", min_value=1, max_value=100, value=10, key="cigs_per_day")
                smoking_years = st.number_input("Years of smoking", min_value=1, max_value=60, value=10, key="smoking_years")
            
            alcohol = st.checkbox("Alcohol Consumption", key="alcohol")
            if alcohol:
                drinks_per_week = st.number_input("Drinks per week", min_value=1, max_value=50, value=5, key="drinks_per_week")
            
            physical_inactivity = st.checkbox("Physical Inactivity (<150 min/week)", key="physical_inactivity")
            high_salt = st.checkbox("High Salt Intake", key="high_salt")
        
        with col2:
            poor_diet = st.checkbox("Poor Diet Quality", key="poor_diet")
            stress = st.checkbox("Chronic Stress", key="stress")
            sleep_deprivation = st.checkbox("Sleep Deprivation (<6 hrs/night)", key="sleep_deprivation")
            sleep_apnea_symptoms = st.checkbox("Sleep Apnea Symptoms", key="sleep_apnea_symptoms")
    
    # Tab 4: Secondary HTN Screening
    with tabs[3]:
        st.markdown('<div class="section-header">Clinical Features Suggesting Secondary Hypertension</div>', unsafe_allow_html=True)
        
        resistant_htn = st.checkbox("Resistant Hypertension (uncontrolled on ≥3 drugs)", key="resistant_htn")
        acute_rise = st.checkbox("Acute Rise in Blood Pressure", key="acute_rise")
        malignant_htn = st.checkbox("Malignant/Accelerated Hypertension", key="malignant_htn")
        early_onset = st.checkbox("Onset before age 30 without risk factors", key="early_onset")
        onset_before_puberty = st.checkbox("Onset before puberty", key="onset_before_puberty")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Renal/Renovascular Clues**")
            abdominal_bruit = st.checkbox("Abdominal Bruit", key="abdominal_bruit")
            asymmetric_kidneys = st.checkbox("Asymmetric Kidney Sizes", key="asymmetric_kidneys")
            elevated_creatinine = st.checkbox("Elevated Creatinine", key="elevated_creatinine")
            abnormal_urinalysis = st.checkbox("Abnormal Urinalysis", key="abnormal_urinalysis")
        
        with col2:
            st.markdown("**Endocrine Clues**")
            hypokalemia = st.checkbox("Hypokalemia (suggests primary aldosteronism)", key="hypokalemia")
            cushings_features = st.checkbox("Cushing's Features", key="cushings_features")
            pheo_triad = st.checkbox("Pheochromocytoma Triad (headache, palpitations, sweating)", key="pheo_triad")
        
        st.markdown("---")
        st.markdown("**Medications That May Cause Hypertension**")
        
        medications = st.multiselect(
            "Select current medications",
            ["Oral Contraceptives", "NSAIDs", "Corticosteroids", "Decongestants", 
             "Anti-cancer Drugs", "Immunosuppressants", "Herbal Supplements"],
            key="medications"
        )
    
    # Tab 5: Assessment Summary
    with tabs[4]:
        st.markdown('<div class="section-header">Assessment Summary</div>', unsafe_allow_html=True)
        
        # Save all data to session state
        if st.button("Generate Assessment Summary", type="primary"):
            st.session_state.patient_data = {
                'patient_name': patient_name,
                'age': age,
                'sex': sex,
                'weight': weight,
                'height': height,
                'waist': waist,
                'bmi': bmi,
                'systolic': systolic,
                'diastolic': diastolic,
                'hr': hr,
                'duration_htn': duration_htn,
                'diabetes': diabetes,
                'cad': cad,
                'cva': cva,
                'ckd': ckd,
                'smoking': smoking,
                'physical_inactivity': physical_inactivity,
                'assessment_date': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
            # Calculate risk score
            risk_score = calculate_risk_score(st.session_state.patient_data)
            risk_category, risk_level = get_risk_category(risk_score)
            
            st.session_state.patient_data['risk_score'] = risk_score
            st.session_state.patient_data['risk_category'] = risk_category
            
            st.success("✅ Assessment completed successfully!")
        
        if st.session_state.patient_data:
            data = st.session_state.patient_data
            
            st.markdown("### Patient Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Name", data.get('patient_name', 'N/A'))
                st.metric("Age", f"{data.get('age', 'N/A')} years")
            
            with col2:
                st.metric("BMI", f"{data.get('bmi', 'N/A')} kg/m²")
                st.metric("Blood Pressure", f"{data.get('systolic', 'N/A')}/{data.get('diastolic', 'N/A')} mmHg")
            
            with col3:
                bp_class, _ = classify_bp(data.get('systolic', 120), data.get('diastolic', 80))
                st.metric("BP Classification", bp_class)
            
            st.markdown("---")
            
            # Risk Assessment
            risk_score = data.get('risk_score', 0)
            risk_category, risk_level = get_risk_category(risk_score)
            
            if risk_level == "low":
                st.markdown(f'<div class="risk-low"><h3>Risk Category: {risk_category}</h3><p>Risk Score: {risk_score}/20+</p></div>', unsafe_allow_html=True)
            elif risk_level == "moderate":
                st.markdown(f'<div class="risk-moderate"><h3>Risk Category: {risk_category}</h3><p>Risk Score: {risk_score}/20+</p></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="risk-high"><h3>Risk Category: {risk_category}</h3><p>Risk Score: {risk_score}/20+</p></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Recommendations
            st.markdown("### Immediate Actions Required")
            
            actions = []
            
            if data.get('systolic', 0) >= 180 or data.get('diastolic', 0) >= 120:
                actions.append("🚨 **EMERGENCY REFERRAL** - Hypertensive crisis")
            
            if risk_category in ["High Risk", "Very High Risk"]:
                actions.append("💊 Start or intensify antihypertensive therapy")
            
            if data.get('bmi', 0) >= 25:
                actions.append("🏃 Weight reduction program")
            
            if data.get('smoking'):
                actions.append("🚭 Smoking cessation counseling")
            
            if data.get('diabetes'):
                actions.append("🩸 Optimize diabetes management")
            
            actions.append("📋 Order basic investigations (CBC, LFT, KFT, Lipid Profile, HbA1c, TSH, ECG, Echo)")
            
            if resistant_htn or early_onset or malignant_htn:
                actions.append("🔬 Screen for secondary hypertension")
            
            for action in actions:
                st.write(action)

# TREATMENT OPTIONS PAGE
elif page == "Treatment Options":
    st.markdown('<h1 class="main-header">💊 Treatment Options</h1>', unsafe_allow_html=True)
    
    if not st.session_state.patient_data:
        st.warning("⚠️ Please complete Patient Assessment first")
    else:
        data = st.session_state.patient_data
        
        tabs = st.tabs(["Medication Selection", "Treatment Goals", "Monitoring Plan"])
        
        with tabs[0]:
            st.markdown('<div class="section-header">Antihypertensive Medication Selection</div>', unsafe_allow_html=True)
            
            st.info("""
            **First-Line Agents for Hypertension:**
            - ACE Inhibitors (ACEi)
            - Angiotensin Receptor Blockers (ARB)
            - Calcium Channel Blockers (CCB)
            - Thiazide/Thiazide-like Diuretics
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Risk Category", risk_category)
                st.metric("Risk Score", f"{risk_score}/20+")
            
            with col2:
                if risk_level == "low":
                    st.success("Low cardiovascular risk")
                elif risk_level == "moderate":
                    st.warning("Moderate cardiovascular risk")
                else:
                    st.error("High cardiovascular risk")
            
            st.markdown("---")
            
            st.markdown("### Comorbidities")
            
            comorbidities = []
            if data.get('diabetes'):
                comorbidities.append("✓ Diabetes Mellitus")
            if data.get('cad'):
                comorbidities.append("✓ Coronary Artery Disease")
            if data.get('cva'):
                comorbidities.append("✓ Cerebrovascular Accident")
            if data.get('ckd'):
                comorbidities.append("✓ Chronic Kidney Disease")
            
            if comorbidities:
                for condition in comorbidities:
                    st.write(condition)
            else:
                st.write("No significant comorbidities reported")
            
            st.markdown("---")
            
            st.markdown("### Risk Factors")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Modifiable Risk Factors:**")
                modifiable = []
                if data.get('smoking'):
                    modifiable.append("• Smoking")
                if data.get('physical_inactivity'):
                    modifiable.append("• Physical inactivity")
                if data.get('bmi', 0) >= 25:
                    modifiable.append(f"• Overweight/Obesity (BMI: {data.get('bmi')})")
  
