import os
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URI = os.getenv("BASE_URI", "http://localhost:3000")

st.set_page_config(layout="wide")

# Split layout into two columns
left_col, right_col = st.columns([1, 2])

if "selectedFood" not in st.session_state:
    st.session_state.selectedFood = None

with left_col:
    search_term = st.text_input("Search food", placeholder="Type to search...")

    if search_term:
        try:
            response = requests.get(f"{BASE_URI}/food/search?search={search_term}")
            if response.status_code == 200:
                food_matches = response.json()
                st.markdown("### BEST MATCHES")
                with st.container(height=200):
                    for food in food_matches:
                        if st.button(f"{food['name']}\n{food['calories_kcal']} kcal, per 100g"):
                            st.session_state.selectedFood = food

            else:
                st.warning("Failed to fetch food matches.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
    else:
        st.markdown("### Search and enter to see result")

    selectedFood = st.session_state.selectedFood
    if selectedFood:
        st.markdown("----")
        st.markdown(f"### 🥣 {selectedFood['name']}: ")
        st.text(f"Original Name (inc country match, if available): {selectedFood['name_origin']}")
        st.text(f"Category: {selectedFood['category']}")
        st.text(f"Subcategory: {selectedFood['subcategory']}")
        
        st.markdown("**Main unit**\n- Display name\n- Unit1\n- Unit2\n- Display_to_main_conversion")
        st.markdown("**Nutrition facts per 100g:**\n- Calories\n- Protein\n- ... (add others)")

# RIGHT COLUMN: Prompt Editor
with right_col:
    st.markdown("### 📝 AI Prompt Editor")
    
    # Top buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Save")
        
    
    # Text area for full prompt
    prompt_text = """Given the input:
- Original_name
- Category_name
- Subcategory_name
- Food_name
...

Role: You are a professional “Nutrition Data Extractor” ...
    """
    st.text_area("Prompt Instructions", value=prompt_text, height=700)
