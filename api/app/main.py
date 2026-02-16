from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path

import pandas as pd
import numpy as np
import joblib
import traceback


app = FastAPI(title="Smart Pantry Recipe Recommender API")

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"

df = None
model = None

class RecommendRequest(BaseModel):
    allergens_to_avoid: list[str] = []
    ingredients_available: list[str] = []
    max_time: int = 60
    cuisines: list[str] = []
    top_k: int = 5

def has_forbidden_allergen(recipe_allergens, forbidden):
    return any(a in recipe_allergens for a in forbidden)

def ingredient_overlap(recipe_ingredients, user_ingredients):
    return len(set(recipe_ingredients) & set(user_ingredients))

@app.on_event("startup")
def load_artifacts():
    global df, model
    df = pd.read_parquet(ARTIFACTS_DIR / "recipes.parquet")
    print("columns:", df.columns.tolist()) 
    model = joblib.load(ARTIFACTS_DIR / "recipe_rating_model.joblib")

@app.post("/recommend")
def recommend(req: RecommendRequest):
    try:
        candidates = df.copy()

        candidates = candidates[candidates["minutes"] <= req.max_time]
        print("after minutes", req.max_time, ":", len(candidates))


        if req.cuisines:
            candidates = candidates[candidates["cuisine"].isin(req.cuisines)]
            print("after cuisines", req.cuisines, ":", len(candidates))

        if req.allergens_to_avoid:
            candidates = candidates[
                ~candidates["allergens"].apply(
                    lambda lst: has_forbidden_allergen(lst, req.allergens_to_avoid)
                )
            ]
            

        if req.ingredients_available:
            if "ingredients" not in candidates.columns:
                raise ValueError("Column 'ingredients' not found in dataframe")
            candidates["ingredient_overlap"] = candidates["ingredients"].apply(
                lambda lst: ingredient_overlap(lst, req.ingredients_available)
            )
        else:
            candidates["ingredient_overlap"] = 0


        if candidates.empty:
            return {"recipes": []}

        if "log_n_reviews" not in candidates.columns:
            candidates["log_n_reviews"] = np.log1p(candidates["n_reviews"])

        feature_cols_num = ["minutes", "n_ingredients", "n_steps", "calories", "log_n_reviews"]
        feature_cols_cat = ["cuisine"]
        X = candidates[feature_cols_num + feature_cols_cat]

        candidates["predicted_rating"] = model.predict(X)

        candidates = candidates.sort_values(
            ["predicted_rating", "ingredient_overlap", "n_reviews"],
            ascending=[False, False, False],
        )

        top = candidates.head(req.top_k)

        return {
            "recipes": [
                {
                    "recipe_id": int(row["recipe_id"]),
                    "name": row["name"],
                    "cuisine": row["cuisine"],
                    "minutes": int(row["minutes"]),
                    "avg_rating": float(row["avg_rating"]),
                    "predicted_rating": float(row["predicted_rating"]),
                    "n_reviews": int(row["n_reviews"]),
                    "ingredient_overlap": int(row["ingredient_overlap"]),
                }
                for _, row in top.iterrows()
            ]
        }

    except Exception as e:
        print("ERRORE NELL'ENDPOINT /recommend:", e)
        traceback.print_exc()

        raise HTTPException(status_code=500, detail=str(e))

