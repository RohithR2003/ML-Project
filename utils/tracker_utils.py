# utils/tracker_utils.py
import pandas as pd
import os
from datetime import datetime

LOG_PATH = os.path.join("models","user_logs.csv")
os.makedirs("models", exist_ok=True)

def save_user_log(user, date_str, recipe, protein, carbs, fat):
    df_row = pd.DataFrame([{
        "user": user,
        "date": date_str,
        "recipe": recipe,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "saved_at": datetime.now().isoformat()
    }])
    if os.path.exists(LOG_PATH):
        df_row.to_csv(LOG_PATH, mode="a", header=False, index=False)
    else:
        df_row.to_csv(LOG_PATH, index=False)

def load_logs():
    if not os.path.exists(LOG_PATH):
        return None
    df = pd.read_csv(LOG_PATH)
    return df

def save_plan_log(df_recipes, user_name="user"):
    # df_recipes is a DataFrame of selected recipes; convert and append today rows
    rows = []
    for _, r in df_recipes.iterrows():
        rows.append({
            "user": user_name,
            "date": datetime.now().date().isoformat(),
            "recipe": r.get("Recipe_name", ""),
            "protein": r.get("Protein(g)", 0),
            "carbs": r.get("Carbs(g)", 0),
            "fat": r.get("Fat(g)", 0),
            "saved_at": datetime.now().isoformat()
        })
    df = pd.DataFrame(rows)
    if os.path.exists(LOG_PATH):
        df.to_csv(LOG_PATH, mode="a", header=False, index=False)
    else:
        df.to_csv(LOG_PATH, index=False)
