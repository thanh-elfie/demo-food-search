import os
import streamlit as st
import requests
import logging

logging.basicConfig(level=logging.DEBUG)


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
if "selected_food_data" not in st.session_state:
    st.session_state.selected_food_data = None
if "prompt" not in st.session_state:
    st.session_state.prompt = None
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = None

# RIGHT COLUMN: Prompt Editor
with right_col:
    st.markdown("### 📝 AI Prompt Editor")
    
    # Top buttons
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col4:
        if st.button("Original version"):
            try:
                response = requests.get(f"{BASE_URI}/gen-ai/version-prompt?useCase=FOOD_DATA_IMPORT&version=1")
                if response.status_code == 200:
                    version_prompt_resp = response.json()
                    st.session_state.current_prompt = version_prompt_resp
            except Exception as e:
                st.error(f"Error fetching data: {e}")
    with col3:
        if st.button("Previous"):
            if st.session_state.current_prompt['version'] > 1:
                try:
                    response = requests.get(f"{BASE_URI}/gen-ai/version-prompt?useCase=FOOD_DATA_IMPORT&version={st.session_state.current_prompt['version'] - 1}")
                    if response.status_code == 200:
                        version_prompt_resp = response.json()
                        st.session_state.current_prompt = version_prompt_resp
                except Exception as e:
                    st.error(f"Error fetching data: {e}")
    with col2:
        if st.button("Next"):
            try:
                response = requests.get(f"{BASE_URI}/gen-ai/version-prompt?useCase=FOOD_DATA_IMPORT&version={st.session_state.current_prompt['version'] + 1}")
                if response.status_code == 200:
                    version_prompt_resp = response.json()
                    st.session_state.current_prompt = version_prompt_resp
            except Exception as e:
                st.error(f"Error fetching data: {e}")
                
    with col1:
        if st.button("Save"):
            prompt_content = st.session_state.prompt
            if prompt_content.strip():
                try:
                    response = requests.post(f"{BASE_URI}/gen-ai/update-prompt", json={"prompt": prompt_content, "useCase": "FOOD_DATA_IMPORT"})
                    if response.status_code == 200 or response.status_code == 201:
                        selected_food = st.session_state.selected_food
                        if selected_food:
                            get_food_resp = requests.get(f"{BASE_URI}/food/{selected_food['id']}/ai-nutrition")
                            if get_food_resp.status_code == 200:
                                st.session_state.selected_food_data = get_food_resp.json()
                            else:
                                st.warning("Failed to fetch AI prompt.")
                    else:
                        st.warning(f"Request failed with status {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {e}")
                
                st.session_state.current_prompt = None
                st.success("Updated prompt successfully!")
            else:
                st.warning("Text area is empty.")
    
    if st.session_state.current_prompt:
        st.session_state.prompt = st.text_area(f"Prompt Instructions - Version ({st.session_state.current_prompt['version']})", value=st.session_state.current_prompt['prompt'], height=700)
    else:
        try:
            response = requests.get(f"{BASE_URI}/gen-ai/latest-prompt?useCase=FOOD_DATA_IMPORT")
            if response.status_code == 200:
                resp_data = response.json()
                st.session_state.current_prompt = resp_data
                st.session_state.prompt = st.text_area(f"Prompt Instructions - Version ({resp_data['version']})", value=resp_data['prompt'], height=700)
            else:
                st.warning("Failed to fetch AI prompt.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")


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
    else:
        st.markdown("### Search and enter to see result")

    selected_food = st.session_state.selected_food
    if selected_food:
        get_food_resp = requests.get(f"{BASE_URI}/food/{selected_food['id']}/ai-nutrition")
        if get_food_resp.status_code == 200:
            st.session_state.selected_food_data = get_food_resp.json()
        else:
            st.warning("Failed to fetch AI prompt.")

    selected_food_data = st.session_state.selected_food_data
    if selected_food_data:
        col1, col2 = st.columns([1, 10])
        with col1:
            if selected_food_data['iconUrl']:
                st.image(selected_food_data['iconUrl'], width=45)
        with col2:
            st.markdown(f"### {selected_food_data['name']}: ")
        st.text(f"Generated with prompt Version ({selected_food_data.get('genAIUsecaseId', '')})")
        st.text(f"Original Name (inc country match, if available): {selected_food_data['nameOrigin']}")
        st.text(f"Category: {selected_food['category']}")
        st.text(f"Subcategory: {selected_food['subCategory']}")
        with st.container(height=500):
            display_food_data = selected_food_data
            display_food_data['document'] = None
            display_food_data['genaiId'] = None
            display_food_data['genAIUsecaseId'] = None
            display_food_data['nutritionScore'] = f"{round(selected_food_data['nutritionScore'], 1)}%"
            display_food_data['organicRate'] = f"{round(selected_food_data['organicRate'], 1)}%"
            st.json(selected_food_data)

