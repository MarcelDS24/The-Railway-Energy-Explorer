import streamlit as st
from app import main as map_app
from chatbot_page import chatbot_page
import joblib
import numpy as np
import pandas as pd

st.set_page_config(page_title="REE - Railway Energy Explorer", layout="wide")

# -----------------------------
# Sidebar navigation
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Route Visualization", "EPI Prediction"])

# -----------------------------
# 1. Route Visualization Page
# -----------------------------
if page == "Route Visualization":
    map_app()

# -----------------------------
# 2. Chatbot Page
# -----------------------------
#elif page == "AI Chat Assistant":
#    chatbot_page()

# -----------------------------
# 3. EPI Prediction Page (NEW)
# -----------------------------
elif page == "EPI Prediction":
    st.title("Predict Energy Potential Index (EPI)")
    st.markdown(
        "Estimate the potential for piezoelectric energy harvesting based on train and route parameters."
    )

    # --- Load trained models ---
    try:
        rf_model = joblib.load("./models/epi_predictor_rf.pkl")
        lr_model = joblib.load("./models/epi_predictor_linear.pkl")
        xgb_model = joblib.load("./models/epi_predictor_xgb.pkl")
    except:
        st.warning("Models not found. Please ensure you've trained and saved them in the `models/` directory.")
        st.stop()

    # --- Input fields for user ---
    col1, col2, col3 = st.columns(3)
    with col1:
        distance = st.number_input("Distance (km)", min_value=1.0, value=50.0, step=1.0)
    with col2:
        avg_speed = st.number_input("Average Speed (km/h)", min_value=10.0, value=80.0, step=5.0)
    with col3:
        train_weight = st.number_input("Train Weight (tons)", min_value=50.0, value=400.0, step=10.0)

    col4, col5 = st.columns(2)
    with col4:
        weekly_total = st.number_input("Weekly Trips (frequency)", min_value=1, value=100, step=5)
    with col5:
        model_choice = st.selectbox(
            "Choose Model for Prediction",
            ["Random Forest", "Linear Regression", "XGBoost"]
        )

    # --- Predict Button ---
    if st.button("Predict EPI"):
        # Use the exact column names used during training
        input_data = pd.DataFrame([{
            "distance": distance,
            "speed": avg_speed,
            "estimated_weight_t": train_weight,
            "weekly_total": weekly_total
        }])

        # Select model
        if model_choice == "Random Forest":
            model = rf_model
        elif model_choice == "Linear Regression":
            model = lr_model
        else:
            model = xgb_model

        # Prediction
        epi_pred = model.predict(input_data)[0]
        st.success(f"Predicted Energy Potential Index (EPI): **{epi_pred:.3f}**")

        # Simple interpretation
        if epi_pred < 5:
            st.info("Low potential — light routes or infrequent trains.")
        elif epi_pred < 20:
            st.info("Moderate potential — may be worth monitoring or small pilot installation.")
        else:
            st.success("High potential — strong candidate for piezoelectric installation!")

 # --- Info box ---
with st.expander("About the Prediction Model"):
    st.markdown(
        """
        The **EPI (Energy Potential Index)** model estimates the relative potential for 
        piezoelectric energy generation using:
        - **Distance (km)**: longer routes yield more vibration opportunities  
        - **Average Speed (km/h)**: higher speeds increase kinetic energy  
        - **Train Weight (tons)**: heavier trains induce more mechanical stress  
        - **Weekly Trips**: reflects frequency and energy capture potential  

        ### Models available:
        - **Random Forest** — high accuracy, robust for non-linear relations  
        - **Linear Regression** — interpretable, simple baseline  
        - **XGBoost** — powerful gradient-boosted ensemble  

        ###  Model Performance Comparison:
        | Model | R² Score | MAE |
        |:--|:--:|:--:|
        | Linear Regression | **0.5719** | 1.6606 |
        | Random Forest | **0.9993** | 0.0078 |
        | XGBoost | **0.9962** | 0.1479 |

        The **Random Forest** model achieved the best overall performance, with near-perfect R² and the lowest Mean Absolute Error (MAE).  
        It was therefore selected as the default model for EPI prediction in this application.
        """
    )
