# streamlit_app/app.py
import streamlit as st
import requests

API_URL = "https://smart-pantry-recipe-recommender.onrender.com"

st.set_page_config(page_title="Smart Pantry",)

st.title("Smart Pantry – Recipe Recommender")


# --- User inputs ---

st.subheader("Inputs")

allergens = st.multiselect(
    "Allergens to avoid",
    ["milk", "eggs", "nuts", "soy", "gluten"]
)

ingredients_text = st.text_input(
    "Ingredients available (comma separated)",
    "tomato, pasta, garlic"
)

max_time = st.slider("Maximum cooking time (minutes)", 5, 1440, 40)

cuisines = st.multiselect(
    "Preferred cuisines",
    ["american", "european", "asian", "pacific", "african",
     "greek", "french", "german", "scandinavian", "spanish",
     "latin_american", "middle_eastern", "indian", "mexican", "chinese"]
)

top_k = st.slider("Number of recipes", 1, 10, 5)

if st.button("Find recipes"):
    ingredients_available = [
        x.strip() for x in ingredients_text.split(",") if x.strip()
    ]

    body = {
        "allergens_to_avoid": allergens,
        "ingredients_available": ingredients_available,
        "max_time": max_time,
        "cuisines": cuisines,
        "top_k": top_k
    }

    try:
        resp = requests.post(f"{API_URL}/recommend", json=body, timeout=15)
    except requests.exceptions.ReadTimeout:
        st.warning("The backend is waking up (free hosting). Please try again in a few seconds.")
        st.stop()
    except Exception as e:
        st.error(f"Request failed: {e}")
    else:
        if resp.status_code != 200:
            st.error(f"API error {resp.status_code}: {resp.text}")
        else:
            data = resp.json()
            recipes = data.get("recipes", [])

            st.subheader("Recommendations")

            if not recipes:
                st.warning("No recipes found for these constraints.")
            else:
                for r in recipes:
                    card = st.container(border=True)
                    with card:
                        st.markdown(f"### {r['name']}")

                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"Cuisine: **{r['cuisine']}**")
                        with col2:
                            st.write(f"Time: **{r['minutes']} min**")
                        with col3:
                            st.write(f"Reviews: **{r['n_reviews']}**")

                        st.write(f"Average rating: {r['avg_rating']:.2f}")

