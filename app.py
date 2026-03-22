import streamlit as st
from prompts import build_analysis_prompt, build_meal_suggestions_prompt
from llm import get_health_analysis, get_meal_suggestions

st.set_page_config(
    page_title="HealthBistroAI",
    page_icon="🥗",
    layout="wide"
)

st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        h1 { color: #2C7A4B; }
        h2 { color: #2C7A4B; border-bottom: 1px solid #e0e0e0; padding-bottom: 0.3rem; }
        h3 { color: #444444; }
    </style>
""", unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────────

st.title("HealthBistroAI")
st.markdown("**A clinical nutrition assistant.** Enter your health data to receive personalized dish recommendations.")
st.warning("This tool provides nutritional guidance only and is not a substitute for medical advice. Always consult your healthcare provider before making significant dietary changes.")
st.divider()

# ── SESSION STATE ──────────────────────────────────────────────────────────────

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "show_recipe_form" not in st.session_state:
    st.session_state.show_recipe_form = False
if "meal_suggestions" not in st.session_state:
    st.session_state.meal_suggestions = None

# ── MISSING DATA INSTRUCTIONS ──────────────────────────────────────────────────

with st.expander("Don't have all your lab values? Read this first."):
    st.markdown("""
**You do not need every lab value to use this app.** Leave any field at 0 and it will be marked as unavailable.

**How to get your lab results:**
- Ask your doctor's office — you are legally entitled to your records
- Check your patient portal (MyChart, Epic, etc.) — results usually post within 24-48 hours
- Labs from the past 1-2 years are still useful context

**Which labs matter most:**
| Panel | Most important if you have... |
|---|---|
| HbA1c / Fasting Glucose | Diabetes or pre-diabetes |
| Lipid panel | Heart disease or high cholesterol |
| Ferritin / Hemoglobin | Fatigue, anemia, or heavy periods |
| TSH | Thyroid disease or unexplained weight changes |
| Vitamin D / Calcium | Osteoporosis or limited sun exposure |
| Vitamin B12 | Vegetarian/vegan diet or nerve symptoms |

**No labs at all?** Just fill in biometrics and conditions — the app still works.
    """)

st.divider()

# ── STAGE 1: HEALTH INTAKE FORM ────────────────────────────────────────────────

st.header("Step 1 — Your Health Profile")

# Biometrics outside the form so BMI recalculates live
st.subheader("Biometrics")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    age = st.number_input("Age", min_value=18, max_value=100, value=40, key="age")
with col2:
    sex = st.selectbox("Sex", ["Male", "Female", "Prefer not to say"], key="sex")
with col3:
    height_ft = st.number_input("Height (ft)", min_value=4, max_value=7, value=5, key="hft")
with col4:
    height_in = st.number_input("Height (in)", min_value=0, max_value=11, value=7, key="hin")
with col5:
    weight = st.number_input("Weight (lbs)", min_value=80, max_value=500, value=170, key="weight")

total_inches = (height_ft * 12) + height_in
bmi = round((weight / (total_inches ** 2)) * 703, 1) if total_inches > 0 else 0
bmi_category = (
    "Underweight" if bmi < 18.5 else
    "Normal weight" if bmi < 25 else
    "Overweight" if bmi < 30 else "Obese"
)
st.info(f"Calculated BMI: **{bmi}** ({bmi_category})")

with st.form("health_form"):

    conditions = st.text_area(
        "Current Health Conditions",
        placeholder="e.g. Type 2 Diabetes, Hypertension, Hypothyroidism, Osteoporosis",
        height=80
    )

    st.markdown("---")
    st.subheader("Lab Results")
    st.caption("Enter 0 for any value you don't have — it will be marked as unavailable.")

    st.markdown("**Metabolic Panel**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        glucose = st.number_input("Fasting Glucose (mg/dL)", min_value=0, max_value=600, value=0)
    with col2:
        hba1c = st.number_input("HbA1c (%)", min_value=0.0, max_value=15.0, value=0.0, step=0.1)
    with col3:
        sodium = st.number_input("Sodium (mEq/L)", min_value=0, max_value=160, value=0)
    with col4:
        potassium = st.number_input("Potassium (mEq/L)", min_value=0.0, max_value=8.0, value=0.0, step=0.1)

    st.markdown("**Lipid Panel**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_cholesterol = st.number_input("Total Cholesterol (mg/dL)", min_value=0, max_value=600, value=0)
    with col2:
        ldl = st.number_input("LDL (mg/dL)", min_value=0, max_value=400, value=0)
    with col3:
        hdl = st.number_input("HDL (mg/dL)", min_value=0, max_value=150, value=0)
    with col4:
        triglycerides = st.number_input("Triglycerides (mg/dL)", min_value=0, max_value=2000, value=0)

    st.markdown("**Iron Panel**")
    col1, col2, col3 = st.columns(3)
    with col1:
        serum_iron = st.number_input("Serum Iron (mcg/dL)", min_value=0, max_value=300, value=0)
    with col2:
        ferritin = st.number_input("Ferritin (ng/mL)", min_value=0, max_value=2000, value=0)
    with col3:
        tibc = st.number_input("TIBC (mcg/dL)", min_value=0, max_value=600, value=0)

    st.markdown("**Thyroid Panel**")
    col1, col2, col3 = st.columns(3)
    with col1:
        tsh = st.number_input("TSH (mIU/L)", min_value=0.0, max_value=20.0, value=0.0, step=0.01)
    with col2:
        free_t3 = st.number_input("Free T3 (pg/mL)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
    with col3:
        free_t4 = st.number_input("Free T4 (ng/dL)", min_value=0.0, max_value=5.0, value=0.0, step=0.01)

    st.markdown("**Bone & Vitamin Panel**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        calcium = st.number_input("Calcium (mg/dL)", min_value=0.0, max_value=15.0, value=0.0, step=0.1)
    with col2:
        vitamin_d = st.number_input("Vitamin D (ng/mL)", min_value=0, max_value=150, value=0)
    with col3:
        b12 = st.number_input("Vitamin B12 (pg/mL)", min_value=0, max_value=2000, value=0)
    with col4:
        hemoglobin = st.number_input("Hemoglobin (g/dL)", min_value=0.0, max_value=20.0, value=0.0, step=0.1)

    analyze_clicked = st.form_submit_button("Analyze My Health Profile", use_container_width=True)

# ── RUN ANALYSIS ───────────────────────────────────────────────────────────────

if analyze_clicked:
    def val(v):
        return "Not provided" if v == 0 or v == 0.0 else str(v)

    user_data = {
        "age": str(age), "sex": sex,
        "height": f"{height_ft}'{height_in}\"",
        "weight": f"{weight} lbs", "bmi": str(bmi),
        "conditions": conditions.strip() or "None reported",
        "glucose": val(glucose), "hba1c": val(hba1c),
        "sodium": val(sodium), "potassium": val(potassium),
        "total_cholesterol": val(total_cholesterol), "ldl": val(ldl),
        "hdl": val(hdl), "triglycerides": val(triglycerides),
        "serum_iron": val(serum_iron), "ferritin": val(ferritin), "tibc": val(tibc),
        "tsh": val(tsh), "free_t3": val(free_t3), "free_t4": val(free_t4),
        "calcium": val(calcium), "vitamin_d": val(vitamin_d),
        "b12": val(b12), "hemoglobin": val(hemoglobin),
    }

    with st.spinner("Analyzing your health profile... (15-25 seconds)"):
        result = get_health_analysis(build_analysis_prompt(user_data))

    st.session_state.analysis_result = result
    st.session_state.show_recipe_form = True
    st.session_state.meal_suggestions = None

# ── DISPLAY ANALYSIS ───────────────────────────────────────────────────────────

if st.session_state.analysis_result:
    st.divider()
    st.header("Step 2 — Your Nutritional Analysis")
    st.markdown(st.session_state.analysis_result)

# ── STAGE 2: MEAL SUGGESTION FORM ─────────────────────────────────────────────

if st.session_state.show_recipe_form:
    st.divider()
    st.header("Step 3 — Get Dish Suggestions")
    st.caption("Choose a meal type and your preferences. We'll generate 3 tailored dish options for you.")

    with st.form("preference_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            meal_type = st.selectbox(
                "What meal are you planning?",
                ["Breakfast", "Lunch", "Dinner"]
            )
        with col2:
            skill_level = st.selectbox(
                "Cooking skill level",
                ["Beginner (simple recipes, minimal techniques)",
                 "Intermediate (comfortable with most methods)",
                 "Advanced (happy to try complex dishes)"]
            )
        with col3:
            cook_time = st.selectbox(
                "Time available",
                ["Under 20 minutes", "20-30 minutes",
                 "30-45 minutes", "Up to 1 hour", "No time limit"]
            )

        col1, col2 = st.columns(2)
        with col1:
            cuisines = st.multiselect(
                "Cuisine preferences",
                [
                    "American", "Mexican", "Italian", "French",
                    "Vietnamese", "Chinese", "Korean", "Japanese",
                    "Thai", "Indian", "Mediterranean", "Middle Eastern",
                    "German", "No preference"
                ],
                default=["No preference"]
            )
            other_cuisine = st.text_input(
                "Other cuisines not listed above",
                placeholder="e.g. Peruvian, Ethiopian, Greek"
            )
        with col2:
            restrictions = st.multiselect(
                "Dietary restrictions",
                ["None", "Vegetarian", "Vegan", "Gluten-free",
                 "Dairy-free", "Nut-free", "Halal", "Kosher"],
                default=["None"]
            )
            dislikes = st.text_input(
                "Ingredients to avoid",
                placeholder="e.g. salmon, liver, spicy food"
            )
            servings = st.selectbox(
                "Servings",
                ["Just me (1 serving)", "2 people", "3-4 people"]
            )

        suggest_clicked = st.form_submit_button(
            "Get 3 Dish Suggestions", use_container_width=True
        )

    if suggest_clicked:
        all_cuisines = cuisines.copy()
        if other_cuisine.strip():
            all_cuisines.append(other_cuisine.strip())

        preferences = {
            "skill_level":  skill_level,
            "cook_time":    cook_time,
            "cuisines":     ", ".join(all_cuisines),
            "restrictions": ", ".join(restrictions),
            "servings":     servings,
            "dislikes":     dislikes.strip() or "None"
        }

        prompt = build_meal_suggestions_prompt(
            meal_type,
            st.session_state.analysis_result,
            preferences
        )

        with st.spinner(f"Generating 3 {meal_type} options... (15-25 seconds)"):
            suggestions = get_meal_suggestions(prompt)

        st.session_state.meal_suggestions = (meal_type, suggestions)

# ── DISPLAY SUGGESTIONS ────────────────────────────────────────────────────────

if st.session_state.meal_suggestions:
    meal_type, suggestions = st.session_state.meal_suggestions
    st.divider()
    st.header(f"Your {meal_type} Options")
    st.markdown(suggestions)
    st.divider()
    st.caption("Want different options? Change your preferences above and click Generate again.")
    st.caption("Always review significant dietary changes with your doctor or a registered dietitian.")