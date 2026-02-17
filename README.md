# Smart Pantry Recipe Recommender

Smart Pantry is an end‑to‑end recipe recommendation system.  
It suggests recipes based on what the user can (and wants to) cook:

- user constraints: time, allergens, preferred cuisines and available ingredients)
- model: scikit‑learn regressor trained on the Food.com recipes dataset
- backend: FastAPI REST API
- frontend: Streamlit web app

The project is split into:

- data & modeling (Kaggle notebooks)
- serving (FastAPI API)
- user interface (Streamlit app)

---

## Tech stack

- Python (data, model, API, frontend)
- Pandas, NumPy (data prep)
- scikit‑learn (model training & inference)
- FastAPI, uvicorn (backend)
- Render (FastAPI backend hosting)
- AWS S3 (dataset + modello)
- Streamlit (UI)
  
---

## Repository structure

```text
smart-pantry-recipe-recommender/
  api/               # FastAPI backend (model serving)
  streamlit_app/     # Streamlit frontend (calls the API)
  notebooks/
    01_data_preparation.ipynb   # data cleaning & feature engineering
    02_model_training.ipynb     # model training
```

- [`api/`](api/): Smart Pantry Recipe Recommender API (FastAPI)  
- [`streamlit_app/`](streamlit_app/): Streamlit frontend that calls the API  
- `notebooks/01_data_preparation.ipynb`: dataset preparation, cleaning, feature engineering  
- `notebooks/02_model_training.ipynb`: model selection, training, evaluation, model export  

Each subfolder has its own README with more details.

---

## End‑to‑end pipeline

1. **Data preparation (Notebook 01)**  
   - Load Food.com recipes and interactions.  
   - Clean and merge data, compute:
     - `n_ingredients`, `n_steps`
     - `avg_rating`, `n_reviews`
     - `calories`, `cuisine`, `allergens`  
   - Save the cleaned dataset as `recipes.parquet`.

2. **Model training (Notebook 02)**  
   - Define features for rating prediction:
     - numeric: `minutes`, `n_ingredients`, `n_steps`, `calories`, `log_n_reviews`
     - categorical: `cuisine`  
   - Train a scikit‑learn regression pipeline to predict the average rating of a recipe.  
   - Export the trained model as `recipe_rating_model.joblib`.

3. **Backend API (`api/`)**  
   - On startup, load:
     - `recipes.parquet` (cleaned dataset)
     - `recipe_rating_model.joblib` (trained model)  
   - Expose a `POST /recommend` endpoint that:
     - filters recipes based on user constraints (`max_time`, `allergens_to_avoid`, `cuisines`)
     - builds the feature matrix
     - gets predictions from the model
     - returns the top‑k recipes sorted by predicted rating and number of reviews  
   - See [`api/README.md`](api/README.md) for details.

4. **Frontend (`streamlit_app/`)**  
   - Web UI where the user selects:
     - allergens to avoid
     - available ingredients
     - maximum time
     - preferred cuisines
     - number of recipes to return  
   - The app sends a JSON request to `/recommend` and displays the recipes returned by the API.  
   - See [`streamlit_app/README.md`](streamlit_app/README.md) for details.

---

## Local setup

### 1. Backend API (FastAPI)

From `api/`:

```bash
python -m venv .venv
.\\.venv\\Scripts\\activate      # Windows
# source .venv/bin/activate      # Linux / macOS

pip install -r requirements.txt
```

The API expects two artifacts:

- `api/artifacts/recipes.parquet` – cleaned dataset  
- `api/artifacts/recipe_rating_model.joblib` – trained model

Then run:

```bash
cd api
uvicorn app.main:app --reload
```

Useful endpoints:

- Docs: `http://127.0.0.1:8000/docs`  
- OpenAPI: `http://127.0.0.1:8000/openapi.json`

Example `POST /recommend` body:

```json
{
  "allergens_to_avoid": ["milk", "nuts"],
  "ingredients_available": ["tomato", "pasta", "garlic"],
  "max_time": 40,
  "cuisines": ["american"],
  "top_k": 5
}
```

---

### 2. Streamlit frontend

From `streamlit_app/`:

```bash
pip install -r requirements.txt
streamlit run app.py
```

By default the app points to a local API:

```python
API_URL = "http://127.0.0.1:8000"
```

---

## Deployment (Render + S3)

In production the stack looks like this:

- FastAPI backend running on **Render** as a web service  
- Dataset and model stored on **AWS S3**, loaded at API startup  
- Streamlit app (local or hosted) calling the public API URL

The FastAPI app in `api/` is deployed to Render with a public URL, for example:

```text
https://smart-pantry-recipe-recommender.onrender.com
```

At startup the service downloads:

- `recipes.parquet` from S3  
- `recipes.smart_pantry_model` from S3

and keeps them in memory for serving recommendations.

The Streamlit app just switches `API_URL` to that public endpoint, e.g.:

```python
API_URL = "https://smart-pantry-recipe-recommender.onrender.com"
```
