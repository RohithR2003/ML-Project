# pages/profile.py
import streamlit as st
import json
import os

st.set_page_config(page_title="Profile - NutriSync", page_icon="👤", layout="wide")

# load css
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<div class='card'><h2>👤 Profile & Preferences</h2><p class='small-muted'>Set your personal details and goals — NutriSync will use these to tailor recommendations.</p></div>", unsafe_allow_html=True)

PROFILE_PATH = os.path.join("models", "user_profile.json")
profile = {}
if os.path.exists(PROFILE_PATH):
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            profile = json.load(f)
    except Exception:
        profile = {}

st.markdown("### 🧾 Personal Information")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name", value=profile.get("name", ""))
    age = st.number_input("Age", 10, 100, value=profile.get("age", 25))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                          index=0 if not profile.get("gender") else ["Male", "Female", "Other"].index(profile.get("gender", "Male")))
    height = st.number_input("Height (cm)", 100, 250, value=profile.get("height", 170))
with col2:
    weight = st.number_input("Weight (kg)", 30.0, 300.0, value=profile.get("weight", 70.0))
    activity = st.selectbox("Activity Level", ["Sedentary", "Light", "Moderate", "Very Active"],
                            index=0 if not profile.get("activity") else ["Sedentary", "Light", "Moderate", "Very Active"].index(profile.get("activity", "Moderate")))
    goal = st.selectbox("Goal", ["Maintain", "Weight Loss", "Weight Gain"],
                        index=0 if not profile.get("goal") else ["Maintain", "Weight Loss", "Weight Gain"].index(profile.get("goal", "Maintain")))
    diet_type = st.selectbox("Preferred Diet Type", ["mediterranean", "dash", "vegan", "keto", "paleo"],
                             index=0 if not profile.get("diet_type") else ["mediterranean", "dash", "vegan", "keto", "paleo"].index(profile.get("diet_type", "mediterranean")))

if st.button("💾 Save Profile"):
    profile = {
        "name": name,
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "activity": activity,
        "goal": goal,
        "diet_type": diet_type
    }
    os.makedirs("models", exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    st.success("✅ Profile saved successfully!")
    st.session_state["user_info"] = profile

# summary block
if "user_info" in st.session_state or profile:
    ui = st.session_state.get("user_info", profile)
    st.markdown("---")
    st.subheader("📊 Summary & Calorie Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"👤 **Name:** {ui.get('name','-')}")
        st.write(f"🎂 **Age:** {ui.get('age','-')}  •  **Gender:** {ui.get('gender','-')}")
        st.write(f"📏 **Height:** {ui.get('height','-')} cm  •  **Weight:** {ui.get('weight','-')} kg")
        st.write(f"🏃 **Activity:** {ui.get('activity','-')}")
        st.write(f"🎯 **Goal:** {ui.get('goal','-')}")
        st.write(f"🥗 **Diet Preference:** {ui.get('diet_type','-')}")
    with col2:
        bmi = ui.get('weight',70) / ((ui.get('height',170)/100)**2)
        st.metric("BMI", f"{bmi:.1f}")
        if ui.get('gender','male').lower()=="male":
            bmr = 10*ui.get('weight',70) + 6.25*ui.get('height',170) - 5*ui.get('age',25) + 5
        else:
            bmr = 10*ui.get('weight',70) + 6.25*ui.get('height',170) - 5*ui.get('age',25) - 161
        activity_map = {"Sedentary":1.2,"Light":1.375,"Moderate":1.55,"Very Active":1.725}
        tdee = bmr * activity_map.get(ui.get('activity','Moderate'), 1.55)
        if ui.get('goal')=="Weight Loss":
            target_cal = tdee * 0.85
        elif ui.get('goal')=="Weight Gain":
            target_cal = tdee * 1.1
        else:
            target_cal = tdee
        st.metric("TDEE (Daily Need)", f"{tdee:.0f} kcal")
        st.metric("Target Calories", f"{target_cal:.0f} kcal")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.info("💡 These calorie values are used to recommend suitable meal plans.")
