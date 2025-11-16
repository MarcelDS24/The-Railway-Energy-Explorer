import streamlit as st
from app import main as map_app
from chatbot_page import chatbot_page

st.set_page_config(page_title="REE - Railway Energy Explorer", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Route Visualization", "AI Chat Assistant"])

if page == "Route Visualization":
    map_app()
elif page == "AI Chat Assistant":
    chatbot_page()


