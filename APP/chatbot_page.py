# chatbot_page.py
import streamlit as st
import pandas as pd
from ollama import chat

def chatbot_page(complete_df=None, filtered_df=None):
    st.markdown("### Chatbot Assistant")
    st.write(
        "Ask about your dataset — e.g. *What's the highest EPI value?* or *Which route has the best potential?*"
    )

    # --- Load the dataset if not provided ---
    if complete_df is None:
        try:
            complete_df = pd.read_csv("./data/oebb_gtfs/stop_times_geo_with_startEnd_calc.csv")
        except FileNotFoundError:
            st.error("Could not load dataset. Please check the file path.")
            return
    
    # If no filtered dataframe provided, use the complete one
    if filtered_df is None:
        filtered_df = complete_df

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

        # --- Compute dataset context for both complete and filtered data ---
        # Complete dataset stats
        if "EPI_segment" in complete_df.columns:
            complete_epi_max = complete_df["EPI_segment"].max()
            complete_epi_mean = complete_df["EPI_segment"].mean()
        else:
            complete_epi_max = complete_epi_mean = None

        complete_route_count = complete_df["trip_id"].nunique() if "trip_id" in complete_df else None

        # Filtered dataset stats
        if "EPI_segment" in filtered_df.columns:
            filtered_epi_max = filtered_df["EPI_segment"].max()
            filtered_epi_mean = filtered_df["EPI_segment"].mean()
            routes_names = filtered_df["trip_id"].unique().tolist() if "trip_id" in filtered_df else None
            Epi_per_route = (filtered_df.groupby("trip_id")["EPI_segment"].mean().to_dict() 
                             if "trip_id" in filtered_df else {})
        else:
            filtered_epi_max = filtered_epi_mean = None

        filtered_route_count = filtered_df["trip_id"].nunique() if "trip_id" in filtered_df else None

        context = (
            #context for complete dataset
            f"COMPLETE DATASET: {len(complete_df):,} rows, {complete_route_count} unique trips. "
            f"Average EPI: {complete_epi_mean:.2f}, Maximum EPI: {complete_epi_max:.2f}. "
            f"CURRENTLY DISPLAYED DATA: {len(filtered_df):,} rows, {filtered_route_count} unique trips. "
            ## Context for filtered data
            f"Average EPI: {filtered_epi_mean:.2f}, Maximum EPI: {filtered_epi_max:.2f}."
            f"Route Names: {', '.join(routes_names) if routes_names else 'N/A'}"
            f" EPI per Route: {Epi_per_route if Epi_per_route else 'N/A'}"
        )

        # --- Generate response using Ollama ---
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = chat(
                        model="llama3.2",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful assistant explaining results from a railway piezoelectric energy analysis. "
                                           "You use the data summary provided to answer clearly and factually. "
                                           "EPI stands for Energy Potential Index. When user asks about current data, refer to the 'CURRENTLY DISPLAYED DATA'. "
                                           "When asked about the full dataset, refer to 'COMPLETE DATASET'.",
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
