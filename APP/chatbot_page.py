# chatbot_page.py
import streamlit as st
import pandas as pd
from ollama import chat

def chatbot_page():
    st.markdown("Chatbot Assistant")
    st.write(
        "Ask about your dataset — e.g. *What’s the highest EPI value?* or *Which route has the best potential?*"
    )

    # --- Load the dataset directly here ---
    try:
        df = pd.read_csv("../data/oebb_gtfs/stop_times_geo_with_startEnd_calc.csv")
    except FileNotFoundError:
        st.error("Could not load dataset. Please check the file path.")
        return

    # --- Keep chat history in session state ---
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- User input box ---
    user_input = st.chat_input("Ask your question about the analysis...")
    if user_input:
        # Save user message
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # --- Compute dataset context ---
        if "EPI_segment" in df.columns:
            epi_max = df["EPI_segment"].max()
            epi_mean = df["EPI_segment"].mean()
        else:
            epi_max = epi_mean = None

        route_count = df["trip_id"].nunique() if "trip_id" in df else None

        context = (
            f"The dataset contains {len(df):,} rows and {route_count} unique trips. "
            f"The average EPI value is {epi_mean:.2f} and the maximum EPI is {epi_max:.2f}."
        )

        # --- Generate response using Ollama ---
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = chat(
                        model="llama3",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful assistant explaining results from a railway piezoelectric energy analysis. "
                                           "You use the data summary provided to answer clearly and factually.",
                            },
                            {"role": "user", "content": f"{context}\n\nUser question: {user_input}"},
                        ],
                    )
                    answer = response["message"]["content"]
                except Exception as e:
                    answer = f"There was an error communicating with the model: {e}"

                st.markdown(answer)

        # Save assistant response
        st.session_state["messages"].append({"role": "assistant", "content": answer})
