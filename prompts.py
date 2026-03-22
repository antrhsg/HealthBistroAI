SYSTEM_PROMPT = """You are HealthBistroAI, a clinical nutrition assistant that helps 
patients make evidence-based dietary decisions based on their personal health data.

SAFETY RULES:
- You are NOT a doctor. Do NOT diagnose or recommend medications.
- Provide nutrition guidance only.
- If lab values are critically abnormal, recommend consulting a healthcare professional.
- Use cautious, evidence-based language.

CLINICAL RULES:
- Tie every recommendation directly to a specific lab value or condition.
- If a lab value is missing, state your assumption explicitly.
- Do NOT give generic advice.

CRITICAL LAB WARNINGS — flag with WARNING label if:
- HbA1c > 9% | LDL > 190 mg/dL | Triglycerides > 500 mg/dL
- Sodium < 135 or > 145 mEq/L | Ferritin < 12 or > 300 ng/mL
- TSH < 0.4 or > 4.0 mIU/L | Free T4 < 0.8 or > 1.8 ng/dL
- Calcium < 8.5 or > 10.5 mg/dL | Vitamin D < 20 ng/mL

OUTPUT RULES:
- Use headers and bullet points.
- Be clear and practical, not alarmist.
- Always complete your full response. Never stop mid-output.
"""


def build_analysis_prompt(user_data: dict) -> str:
    return f"""Analyze this patient's health profile and return a structured nutritional assessment.

Every recommendation MUST reference a specific lab value or diagnosis.
If data is missing, state your assumption.

Respond in exactly these five sections:
1. SUMMARY — 2-3 sentences on the most important concerns
2. PRIORITIZE — foods/nutrients to increase, each with a clinical reason
3. REDUCE / AVOID — foods/nutrients to limit, each with a clinical reason
4. LAB FLAGS — abnormal values, what each means nutritionally, WARNING labels where needed
5. CONFIDENCE & ASSUMPTIONS — missing data, assumptions made, confidence level

## Patient Profile

Biometrics: Height {user_data.get('height')} | Weight {user_data.get('weight')} | BMI {user_data.get('bmi')} | Age {user_data.get('age')} | Sex {user_data.get('sex')}
Conditions: {user_data.get('conditions')}

Metabolic: Glucose {user_data.get('glucose')} mg/dL | HbA1c {user_data.get('hba1c')}% | Sodium {user_data.get('sodium')} mEq/L | Potassium {user_data.get('potassium')} mEq/L
Lipids: Total Chol {user_data.get('total_cholesterol')} | LDL {user_data.get('ldl')} | HDL {user_data.get('hdl')} | Triglycerides {user_data.get('triglycerides')} mg/dL
Iron: Serum Iron {user_data.get('serum_iron')} mcg/dL | Ferritin {user_data.get('ferritin')} ng/mL | TIBC {user_data.get('tibc')} mcg/dL
Thyroid: TSH {user_data.get('tsh')} mIU/L | Free T3 {user_data.get('free_t3')} pg/mL | Free T4 {user_data.get('free_t4')} ng/dL
Bone/Vitamins: Calcium {user_data.get('calcium')} mg/dL | Vit D {user_data.get('vitamin_d')} ng/mL | B12 {user_data.get('b12')} pg/mL | Hemoglobin {user_data.get('hemoglobin')} g/dL

Provide your analysis now:"""


def build_meal_suggestions_prompt(meal_type: str, analysis: str, preferences: dict) -> str:
    """
    Generates exactly 3 dish suggestions for the chosen meal type.
    Focused, short, no truncation risk.
    """
    dislikes = preferences.get('dislikes', 'None')
    forbidden = (
        f"FORBIDDEN — do NOT use these ingredients in any dish: {dislikes}"
        if dislikes.lower() not in ("none", "none specified", "")
        else ""
    )

    return f"""Generate exactly 3 {meal_type} dish options for this patient.

Each dish must be clinically tailored to their health profile below.
Keep instructions concise — numbered steps only.

PATIENT HEALTH ANALYSIS:
{analysis}

PATIENT PREFERENCES:
- Cuisines: {preferences.get('cuisines', 'No preference')}
- Skill level: {preferences.get('skill_level', 'Intermediate')}
- Time available: {preferences.get('cook_time', '30-45 minutes')}
- Dietary restrictions: {preferences.get('restrictions', 'None')}
- Servings: {preferences.get('servings', '1-2 people')}
{forbidden}

Use EXACTLY this format for all 3 dishes:

---
**Option 1: [Dish Name]**
- Why this fits your profile: [1-2 sentences referencing specific lab values or conditions]
- Ingredients:
  - [ingredient + quantity]
- Instructions:
  1. [step]
  2. [step]

---
**Option 2: [Dish Name]**
- Why this fits your profile:
- Ingredients:
- Instructions:

---
**Option 3: [Dish Name]**
- Why this fits your profile:
- Ingredients:
- Instructions:

Generate all 3 options now. Do not stop until Option 3 is fully complete."""