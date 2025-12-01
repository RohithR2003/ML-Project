# pages/tracker.py
import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

# attempt to import utils functions if available
try:
    from utils.tracker_utils import load_logs, save_user_log
except Exception:
    load_logs = None
    save_user_log = None

st.set_page_config(page_title="Daily Tracker - NutriSync", page_icon="📊", layout="wide")

# load css
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<div class='card'><h2>📊 Daily Tracker & Progress</h2><p class='small-muted'>Log meals and view progress charts.</p></div>", unsafe_allow_html=True)

# ensure profile present
profile_path = os.path.join("models", "user_profile.json")
if os.path.exists(profile_path):
    try:
        user = pd.read_json(profile_path, typ="series").to_dict()
    except Exception:
        user = {}
else:
    user = {}

if not user:
    st.warning("⚠️ Please create a profile first (Profile page).")
    st.stop()

st.subheader(f"Hello {user.get('name','User')}, track your meals and view progress")

# form to add log
with st.form("log_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        log_date = st.date_input("Date", value=date.today())
        recipe = st.text_input("Recipe name")
    with col2:
        prot = st.number_input("Protein (g)", 0.0)
        carbs = st.number_input("Carbs (g)", 0.0)
        fat = st.number_input("Fat (g)", 0.0)
    submitted = st.form_submit_button("Add log")
    if submitted:
        if save_user_log:
            save_user_log(user.get("name","user"), log_date.isoformat(), recipe, prot, carbs, fat)
            st.success("Saved log entry.")
        else:
            # fallback store to local file: models/user_logs.csv
            os.makedirs("models", exist_ok=True)
            logs_path = os.path.join("models","user_logs.csv")
            df_new = pd.DataFrame([{
                "user": user.get("name","user"),
                "date": log_date.isoformat(),
                "recipe": recipe,
                "protein": prot,
                "carbs": carbs,
                "fat": fat
            }])
            if os.path.exists(logs_path):
                df_old = pd.read_csv(logs_path)
                df_old = pd.concat([df_old, df_new], ignore_index=True)
                df_old.to_csv(logs_path, index=False)
            else:
                df_new.to_csv(logs_path, index=False)
            st.success("Saved log entry (local fallback).")

# load logs
if load_logs:
    logs = load_logs()
else:
    logs_path = os.path.join("models","user_logs.csv")
    if os.path.exists(logs_path):
        logs = pd.read_csv(logs_path)
    else:
        logs = pd.DataFrame(columns=["user","date","recipe","protein","carbs","fat"])

if logs.empty:
    st.info("No logs yet. Add entries above or save a plan from Meal Plan page.")
else:
    df_user = logs[logs["user"]==user.get("name","user")]
    if df_user.empty:
        st.info("No logs for this user yet.")
    else:
        st.markdown("### 📋 Logs")
        st.dataframe(df_user.sort_values("date", ascending=False).reset_index(drop=True))
        df_user["date"] = pd.to_datetime(df_user["date"])
        daily = df_user.groupby(df_user["date"].dt.date).agg({"protein":"sum","carbs":"sum","fat":"sum"}).reset_index()
        daily["calories"] = daily["protein"]*4 + daily["carbs"]*4 + daily["fat"]*9

        st.markdown("### 📈 Daily Calories")
        fig = px.line(daily, x="date", y="calories", title="Calories over time", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🧩 Macros per day")
        fig2 = px.bar(daily, x="date", y=["protein","carbs","fat"], title="Macros by day")
        st.plotly_chart(fig2, use_container_width=True)

        avg_cals = daily["calories"].mean()
        col1, col2, col3 = st.columns(3)
        col1.metric("Average Daily Calories", f"{avg_cals:.0f} kcal")
        col2.metric("Average Protein", f"{daily['protein'].mean():.1f} g")
        col3.metric("Average Carbs", f"{daily['carbs'].mean():.1f} g")

st.success("Keep tracking daily to monitor your progress!")
