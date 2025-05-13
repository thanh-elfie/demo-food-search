import os
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URI = os.getenv("BASE_URI", "")

st.set_page_config(layout="wide")

# Split layout into two columns
left_col, right_col = st.columns([1, 2])

if "current_search" not in st.session_state:
    st.session_state.current_search = ""
if "food_matches" not in st.session_state:
    st.session_state.food_matches = []
if "selected_food" not in st.session_state:
    st.session_state.selected_food = None
if "fetching_food_detail" not in st.session_state:
    st.session_state.fetching_food_detail = False
if "prompt" not in st.session_state:
    st.session_state.prompt = None
if "reloading_food_detail" not in st.session_state:
    st.session_state.reloading_food_detail = False

with left_col:
    search_term = st.text_input("Search food", placeholder="Type to search...")

    if search_term and st.session_state.current_search != search_term:
        st.session_state.current_search = search_term
        try:
            response = requests.get(f"{BASE_URI}/food/search?search={search_term}")
            if response.status_code == 200:
                st.session_state.food_matches = response.json()
            else:
                st.warning("Failed to fetch food matches.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")

    if search_term:
        st.markdown("### BEST MATCHES")
        with st.container(height=200):
            for i, food in enumerate(st.session_state.food_matches):
                if st.button(f"{food['name']} - {food['calories_kcal']} kcal, per 100g", key=f"name_btn_{i}"):
                    st.session_state.selected_food = food
                    st.session_state.fetching_food_detail = True
    else:
        st.markdown("### Search and enter to see result")

    selected_food = st.session_state.selected_food
    if selected_food and st.session_state.fetching_food_detail:
        get_food_resp = requests.get(f"{BASE_URI}/food/{selected_food['id']}/ai-nutrition")
        if get_food_resp.status_code == 200:
            food_data = get_food_resp.json()
            st.markdown("----")
            st.markdown(f"### 🥣 {selected_food['name']}: ")
            st.text(f"Original Name (inc country match, if available): {selected_food['name_origin']}")
            st.text(f"Category: {selected_food['category']}")
            st.text(f"Subcategory: {selected_food['subcategory']}")
            with st.container(height=500):
                st.json(food_data)
            st.session_state.fetching_food_detail = False
        else:
            st.warning("Failed to fetch AI prompt.")

# RIGHT COLUMN: Prompt Editor
with right_col:
    st.markdown("### 📝 AI Prompt Editor")
    
    # Top buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Save"):
            prompt_content = st.session_state.prompt
            if prompt_content.strip():
                try:
                    response = requests.post(f"{BASE_URI}/gen-ai/update-prompt", json={"prompt": prompt_content, "useCase": "FOOD_DATA_IMPORT"})
                    if response.status_code == 200 or response.status_code == 201:
                        st.success("Updated prompt successfully!")
                        st.session_state.fetching_food_detail = True
                    else:
                        st.warning(f"Request failed with status {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Text area is empty.")
            

        
    try:
        response = requests.get(f"{BASE_URI}/gen-ai/latest-prompt?useCase=FOOD_DATA_IMPORT")
        if response.status_code == 200:
            respData = response.json()
            st.session_state.prompt = st.text_area("Prompt Instructions", value=respData['prompt'], height=700)

        else:
            st.warning("Failed to fetch AI prompt.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    
