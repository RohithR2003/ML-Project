# pages/meal_plan_recommender.py
import streamlit as st
import pandas as pd
import os
import joblib
from utils.recommender import recommend_similar
from utils.tracker_utils import save_plan_log, save_user_log

st.set_page_config(page_title="Meal Plan Recommender - NutriSync", page_icon="🍱", layout="wide")

# load css (page-scoped just in case)
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<div class='card'><h2>🍱 Meal Plan Recommender</h2><p class='small-muted'>Generate personalized meal plans and add them directly to your tracker.</p></div>", unsafe_allow_html=True)

# -------------------- LOAD PROFILE --------------------
profile_path = os.path.join("models", "user_profile.json")
if os.path.exists(profile_path):
    try:
        user = pd.read_json(profile_path, typ="series").to_dict()
    except Exception:
        user = {}
else:
    user = {}

if not user:
    st.warning("⚠️ Please complete your profile first (Profile page).")
    st.stop()

diet_choice = user.get("diet_type", "mediterranean")

# -------------------- LOAD DATASET --------------------
DATA_PATH = os.path.join("Resource", "All_Diets.csv")
MODEL_PATH = os.path.join("models", "calorie_model.pkl")
os.makedirs("models", exist_ok=True)

if not os.path.exists(DATA_PATH):
    st.error(f"Dataset not found at {DATA_PATH}")
    st.stop()

df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()
if "calories_est" not in df.columns:
    df["calories_est"] = 4*df["Protein(g)"] + 4*df["Carbs(g)"] + 9*df["Fat(g)"]

filtered = df[df["Diet_type"].str.lower() == diet_choice.lower()].reset_index(drop=True)
st.write(f"Found **{len(filtered)}** recipes for **{diet_choice}**")

# calorie estimator
with st.expander("🔢 Estimate Calories from Macros (Optional)"):
    p = st.number_input("Protein (g)", value=20.0)
    c = st.number_input("Carbs (g)", value=30.0)
    f = st.number_input("Fat (g)", value=10.0)
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            pred = model.predict([[p,c,f]])[0]
            st.success(f"Predicted Calories: **{pred:.1f} kcal** (model)")
        except Exception:
            pred = 4*p + 4*c + 9*f
            st.info(f"Estimated Calories: **{pred:.1f} kcal** (formula fallback)")
    else:
        pred = 4*p + 4*c + 9*f
        st.info(f"Estimated Calories: **{pred:.1f} kcal** (formula)")

# filtering
st.markdown("### 🎯 Calorie & Cuisine Filters")
target_calories = st.number_input("Target Calories (kcal)", value=float(pred), step=50.0)
tolerance = st.slider("Calorie Tolerance (± kcal)", 50, 500, 100, step=50)
lower, upper = target_calories - tolerance, target_calories + tolerance
filtered_meals = filtered[(filtered["calories_est"] >= lower) & (filtered["calories_est"] <= upper)]

st.success(f"Found **{len(filtered_meals)}** meals between {lower:.0f}–{upper:.0f} kcal")

search = st.text_input("🔍 Search recipes by name")
cuisine_options = ["All"] + sorted(filtered["Cuisine_type"].dropna().unique().tolist())
cuisine = st.selectbox("Filter by Cuisine Type", cuisine_options)

display_df = filtered_meals.copy()
if search:
    display_df = display_df[display_df["Recipe_name"].str.contains(search, case=False, na=False)]
if cuisine != "All":
    display_df = display_df[display_df["Cuisine_type"] == cuisine]

# show recipes with expanders and Add buttons
st.markdown("### 📋 Select meals")
selected_rows = []
cols_per_row = 2
for idx, row in display_df.iterrows():
    with st.expander(f"{row['Recipe_name']} — {row['Cuisine_type']}"):
        left, right = st.columns([4,1])
        with left:
            st.write(f"Protein: **{row['Protein(g)']} g**  •  Carbs: **{row['Carbs(g)']} g**  •  Fat: **{row['Fat(g)']} g**")
            st.write(f"Calories: **{row['calories_est']:.0f} kcal**")
        with right:
            if st.button("➕ Add to today's tracker", key=f"add_{idx}"):
                # Save as today's log (via utils.tracker_utils)
                save_user_log = None
                try:
                    from utils.tracker_utils import save_user_log
                except Exception:
                    save_user_log = None
                if save_user_log:
                    save_user_log(user.get("name","user"), pd.Timestamp.today().strftime("%Y-%m-%d"), row["Recipe_name"], float(row["Protein(g)"]), float(row["Carbs(g)"]), float(row["Fat(g)"]))
                    st.success(f"Added **{row['Recipe_name']}** to tracker.")
                else:
                    # fallback store in session_state meal_plan
                    st.session_state.setdefault("temp_added", [])
                    st.session_state["temp_added"].append(row.to_dict())
                    st.success(f"Added **{row['Recipe_name']}** to temporary plan (session).")

# summary & save selected (if any checked earlier)
st.markdown("---")
st.subheader("Selected Items Summary (session)")

# collect any items in session temp_added and show summary
session_items = st.session_state.get("temp_added", [])
if session_items:
    plan_df = pd.DataFrame(session_items)
    total_protein = plan_df["Protein(g)"].sum()
    total_carbs = plan_df["Carbs(g)"].sum()
    total_fat = plan_df["Fat(g)"].sum()
    total_cal = 4*total_protein + 4*total_carbs + 9*total_fat

    st.metric("Total Calories", f"{total_cal:.0f} kcal")
    st.metric("Protein (g)", f"{total_protein:.1f}")
    st.metric("Carbs (g)", f"{total_carbs:.1f}")
    st.metric("Fat (g)", f"{total_fat:.1f}")

    if st.button("💾 Save session plan to tracker"):
        try:
            save_plan_log(plan_df, user.get("name","user"))
            st.success("Plan saved to tracker via models/user_logs.csv")
            st.session_state["temp_added"] = []
        except Exception as e:
            st.error("Failed to save plan: " + str(e))
else:
    st.info("No session items added yet — use ➕ Add to today's tracker on any recipe.")

# recommended similar (for first selected or search)
if session_items:
    try:
        st.markdown("### 🤖 Recommended Similar Meals")
        first_recipe = session_items[0]["Recipe_name"]
        recs = recommend_similar(first_recipe, topn=5)
        if isinstance(recs, (list, tuple)):
            st.write(recs)
        else:
            st.dataframe(recs)
    except Exception as e:
        st.error("Failed to produce recommendations: " + str(e))
