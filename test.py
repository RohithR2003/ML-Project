import pandas as pd

# Load your original dataset
df = pd.read_csv("Resources/Diet_plan/All_Diets.csv")

# Drop unnecessary columns
df = df.drop(columns=["Extraction_day", "Extraction_time"], errors="ignore")

# Rename columns for consistency
df.columns = ["diet_type", "recipe_name", "cuisine_type", "protein", "carbs", "fat"]

# Remove rows with missing values in important columns
df = df.dropna(subset=["diet_type", "recipe_name", "protein", "carbs", "fat"])

# Calculate total estimated calories
df["calories_estimated"] = (4 * df["protein"] + 4 * df["carbs"] + 9 * df["fat"]).round(2)

# Save cleaned dataset
df.to_csv("Resources/Diet_plan/All_Diets.csv", index=False)

print("✅ Cleaned dataset with calorie estimation saved as 'Clean_Diets.csv'")
print(df.head())
