# Smart Pantry Recipe Recommender API

Backend API for the **Smart Pantry Recipe Recommender**, built with FastAPI and a scikit-learn regression model trained on the Food.com recipes dataset.  
Given user constraints (time, allergens, cuisines, etc.), it returns the top‑k most suitable recipes.

***

## Features

- Loads a pre‑trained **rating prediction model** (`recipe_rating_model.joblib`).
- Uses a cleaned recipes dataset (`recipes.parquet`) with:
  - recipe metadata (name, cuisine, minutes, reviews, ratings),
  - engineered features (e.g. `n_ingredients`, `n_steps`, `calories`, `n_reviews`).
- Exposes a single recommendation endpoint:

```http
POST /recommend
```

- Returns the top‑k recipes sorted by the model **predicted rating**, number of reviews, and (in the future) ingredient overlap.

***

## Project structure

```text
api/
  app/
    main.py                    # FastAPI application
  artifacts/
    recipes.parquet            # cleaned dataset used by the model
    recipe_rating_model.joblib # trained model 
  requirements.txt
```

***

## Installation (local)

From inside `api/`:

```bash
# install dependencies
pip install -r requirements.txt
```

Make sure you have:

- `recipes.parquet` in `api/artifacts/`
- `recipe_rating_model.joblib` in `api/artifacts/`

***

## Run

From `api/`:

```bash
uvicorn app.main:app --reload
```

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

***

## API

### POST `/recommend`

JSON request:

```json
{
  "allergens_to_avoid": ["milk", "nuts"],
  "ingredients_available": ["tomato", "pasta", "garlic"],
  "max_time": 40,
  "cuisines": ["italian", "american"],
  "top_k": 5
}
```

Fields:

- `allergens_to_avoid` (list of strings, optional)  
  Allergens that must be excluded (e.g. `"milk"`, `"eggs"`, `"nuts"`).

- `ingredients_available` (list of strings, optional)  
  Ingredients currently available in the pantry.  
  In the current backend implementation they are accepted but not yet used in the ranking (placeholder for future extensions).

- `max_time` (int, optional, default 60)  
  Maximum cooking time in minutes.

- `cuisines` (list of strings, optional)  
  Preferred cuisines (e.g. `"italian"`, `"american"`).  
  If empty, the cuisine filter is not applied.

- `top_k` (int, optional, default 5)  
  Number of recipes to return.

Example response:

```json
{
  "recipes": [
    {
      "recipe_id": 241943,
      "name": "chicago dog salad",
      "cuisine": "american",
      "minutes": 15,
      "avg_rating": 5.0,
      "predicted_rating": 4.93,
      "n_reviews": 5,
      "ingredient_overlap": 0
    }
  ]
}
```

If no recipe satisfies the constraints, the response is:

```json
{
  "recipes": []
}
```

***

## Model & data details

- The model is a scikit‑learn regressor (pipeline with preprocessing + model) trained to predict the **average rating** of a recipe from:
  - `minutes`
  - `n_ingredients`
  - `n_steps`
  - `calories`
  - `n_reviews` / `log_n_reviews`
  - `cuisine` (one‑hot encoded)

- The `recipes.parquet` dataset contains the minimal set of columns required to reproduce the features used in production.
