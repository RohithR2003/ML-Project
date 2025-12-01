# utils/recommender.py
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = os.path.join("Resource","All_Diets.csv")

def _build_features():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    # use numeric macro features
    feat = df[["Protein(g)","Carbs(g)","Fat(g)"]].fillna(0)
    scaler = StandardScaler()
    return df, scaler.fit_transform(feat)

# recommend recipes similar by macros
def recommend_similar(recipe_name, topn=5):
    df, feats = _build_features()
    # find index of the recipe by name (case insensitive)
    idx_list = df.index[df["Recipe_name"].str.lower() == recipe_name.lower()].tolist()
    if not idx_list:
        return []
    idx = idx_list[0]
    sims = cosine_similarity(feats[idx:idx+1], feats).flatten()
    df["sim_score"] = sims
    # exclude same name
    recs = df[df.index != idx].sort_values("sim_score", ascending=False).head(topn)
    return recs[["Recipe_name","Cuisine_type","Protein(g)","Carbs(g)","Fat(g)","sim_score"]].to_dict(orient="records")
