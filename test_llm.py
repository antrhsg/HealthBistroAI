# Quick test — run this before building app.py
from prompts import build_analysis_prompt
from llm import get_health_analysis

# Fake patient data to test the full pipeline
sample_data = {
    "height": "5'9\"",
    "weight": "210 lbs",
    "bmi": "31.0",
    "age": "45",
    "sex": "Male",
    "conditions": "Type 2 Diabetes, Hypertension",
    "glucose": "142",
    "hba1c": "7.8",
    "sodium": "138",
    "potassium": "4.1",
    "total_cholesterol": "215",
    "ldl": "145",
    "hdl": "38",
    "triglycerides": "280",
    "hemoglobin": "13.2",
    "vitamin_d": "18",
    "b12": "310"
}

print("Building prompt...")
prompt = build_analysis_prompt(sample_data)

print("Calling LLM... (may take 10-20 seconds)")
result = get_health_analysis(prompt)

print("\n" + "="*60)
print("LLM RESPONSE:")
print("="*60)
if result.startswith("Error"):
    print("❌ Test failed")
else:
    print("✅ Test succeeded")
