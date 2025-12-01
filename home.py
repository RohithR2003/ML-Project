# home.py
import streamlit as st
import os
import pandas as pd

st.set_page_config(page_title="NutriSync", page_icon="🍱", layout="wide")

# load css
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# header
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=64)
    else:
        st.markdown("<div class='nutrisync-logo'><svg width='36' height='36' viewBox='0 0 24 24' fill='none' stroke='#3b82f6' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'><path d='M13 10V3L4 14h7v7l9-11h-7z'></path></svg><h1>NutriSync</h1></div>", unsafe_allow_html=True)

with col2:
    st.markdown("<h1 style='text-align:center;color:#2e7d32;margin-bottom:0'>🍱 NutriSync</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;color:#555;margin-top:4px'>A Personalized Diet Planner</h4>", unsafe_allow_html=True)

st.write("---")

# Quick instructions and overview
st.markdown("""
<div class="card">
**How to use**  
1. Go to **Profile** and save your personal details & preferences.  
2. Go to **Meal Plan Recommender** to browse available meals, build your plan and estimate calories.  
3. Use **Tracker** to log what you ate and view charts.
</div>
""", unsafe_allow_html=True)

# dataset snapshot
DATA_PATH = os.path.join("Resource", "All_Diets.csv")
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
    st.markdown("<div class='header-hr'></div>", unsafe_allow_html=True)
    st.subheader("Dataset snapshot")
    st.write(f"Rows: **{len(df)}**  —  Diet types: **{df['Diet_type'].nunique()}**")
    st.dataframe(df.head(6))
else:
    st.warning(f"Dataset not found at `{DATA_PATH}`. Put cleaned CSV there.")

st.write("---")
st.markdown("Project pages : **Profile**, **Meal Plan Recommender**,  **Tracker**.")
