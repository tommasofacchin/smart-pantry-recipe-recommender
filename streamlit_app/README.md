# Smart Pantry – Streamlit app

This folder contains the Streamlit frontend for the Smart Pantry Recipe Recommender.

The app lets you choose:
- allergens to avoid
- ingredients you have at home
- maximum cooking time
- preferred cuisines
- number of recipes to return

It then calls the FastAPI backend `/recommend` endpoint and displays the recommended recipes as cards.

---

## Hosted backend

the FastAPI backend is deployed on Render:

```python
API_URL = "https://smart-pantry-recipe-recommender.onrender.com"
```
