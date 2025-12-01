import pandas as pd
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

DATA_PATH = os.path.join("Resource", "All_Diets.csv")
MODEL_PATH = os.path.join("models", "calorie_model.pkl")

def _find_col(columns, keywords):
    """
    Find the first column name that contains any of the keywords (case-insensitive).
    `keywords` may be a list of strings; returns the original column name or None.
    """
    cols = list(columns)
    cols_lower = [c.lower() for c in cols]
    for kw in keywords:
        kw_lower = kw.lower()
        for i, c in enumerate(cols_lower):
            if kw_lower in c:
                return cols[i]
    return None

def load_cleaned(path=None):
    """
    Load dataset and normalize macro columns.
    Accepts common variations like 'Protein(g)', 'protein_g', 'Protein' etc.
    Ensures both 'diet_type' and 'Diet_type' columns exist for compatibility.
    """
    if path is None:
        path = DATA_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    # find macro columns flexibly
    protein_col = _find_col(df.columns, ["protein"])
    carbs_col = _find_col(df.columns, ["carb"])   # matches carb or carbs
    fat_col = _find_col(df.columns, ["fat"])

    # optional other columns
    recipe_col = _find_col(df.columns, ["recipe", "name"])
    diet_col = _find_col(df.columns, ["diet"])
    cuisine_col = _find_col(df.columns, ["cuisine"])

    if not (protein_col and carbs_col and fat_col):
        raise ValueError(
            "Missing macro columns in dataset. "
            f"Available columns: {list(df.columns)}. "
            "Expected columns containing 'protein', 'carb' and 'fat'."
        )

    rename_map = {
        protein_col: "protein",
        carbs_col: "carbs",
        fat_col: "fat"
    }
    if recipe_col:
        rename_map[recipe_col] = "recipe_name"
    if diet_col:
        rename_map[diet_col] = "diet_type"
    if cuisine_col:
        rename_map[cuisine_col] = "cuisine_type"

    df = df.rename(columns=rename_map)

    # coerce macros to numeric and drop rows missing macro values
    for col in ["protein", "carbs", "fat"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["protein", "carbs", "fat"])

    # Ensure both lowercase and capitalized diet columns exist to keep legacy code working
    if "diet_type" in df.columns and "Diet_type" not in df.columns:
        df["Diet_type"] = df["diet_type"]
    if "Diet_type" in df.columns and "diet_type" not in df.columns:
        df["diet_type"] = df["Diet_type"]

    return df

def train_calorie_model(save_path=MODEL_PATH):
    try:
        df = load_cleaned()
    except Exception as e:
        raise RuntimeError("train_calorie_model: failed to load/clean data: " + str(e)) from e

    df["calories_est"] = 4 * df["protein"] + 4 * df["carbs"] + 9 * df["fat"]
    X = df[["protein", "carbs", "fat"]].values
    y = df["calories_est"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # ensure model directory exists
    model_dir = os.path.dirname(save_path)
    if model_dir and not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)

    joblib.dump(model, save_path)
    return model
# filepath: e:\Luminar\ML Project\utils\preprocessing.py
