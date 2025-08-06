import streamlit as st
import pandas as pd
import numpy as np

# Page config and title
st.set_page_config(page_title="SYAI-Rank", layout="centered")
st.title("SYAI-Rank: Empowering Sustainable Decisions through Smart Aggregation")
st.markdown("""
This system uses the **Simplified Yielded Aggregation Index (SYAI)** for Multi-Criteria Decision-Making (MCDM).
Upload your data, set weights and types, and get smart rankings.
""")

# Step 1: Upload or input decision matrix
st.header("Step 1: Input Decision Matrix")
data_source = st.radio("Choose data input method:", ["Upload CSV", "Manual Entry"])

if data_source == "Upload CSV":
    uploaded_file = st.file_uploader("Upload your decision matrix CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])  # remove index column
        st.dataframe(df)
else:
    num_alternatives = st.number_input("Number of Alternatives", min_value=2, max_value=20, value=4)
    num_criteria = st.number_input("Number of Criteria", min_value=2, max_value=10, value=3)
    df = pd.DataFrame(np.zeros((num_alternatives, num_criteria)),
                      columns=[f"C{i+1}" for i in range(num_criteria)],
                      index=[f"A{i+1}" for i in range(num_alternatives)])
    df = st.data_editor(df)

# Step 2: Input criteria weights and types
if df is not None and not df.empty:
    st.header("Step 2: Input Criteria Weights and Types")
    weights = []
    types = []
    ideals = {}

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Criteria Weights")
        for i in range(df.shape[1]):
            weight = st.number_input(f"Weight for {df.columns[i]}", min_value=0.0, max_value=1.0, value=1.0)
            weights.append(weight)
    with col2:
        st.markdown("### Criteria Types")
        for i in range(df.shape[1]):
            ctype = st.selectbox(f"Type for {df.columns[i]}", ["Benefit", "Cost", "Ideal"], key=i)
            types.append(ctype)
            if ctype == "Ideal":
                ideal_val = st.number_input(f"Ideal value for {df.columns[i]}", value=float(df.iloc[:, i].mean()))
                ideals[i] = ideal_val

# Step 3: Compute SYAI Ranking
    st.header("Step 3: Compute SYAI Ranking")
    if st.button("Run SYAI Method"):
        norm_matrix = df.copy()
        try:
            for i, t in enumerate(types):
                if t == "Benefit":
                    norm_matrix.iloc[:, i] = df.iloc[:, i] / df.iloc[:, i].max()
                elif t == "Cost":
                    norm_matrix.iloc[:, i] = df.iloc[:, i].min() / df.iloc[:, i]
                elif t == "Ideal":
                    ideal = ideals[i]
                    norm_matrix.iloc[:, i] = 1 - (abs(df.iloc[:, i] - ideal) / ideal)

            weighted_matrix = norm_matrix * weights
            scores = weighted_matrix.sum(axis=1)
            result_df = pd.DataFrame({
                "Alternative": df.index,
                "SYAI Score": scores,
                "Rank": scores.rank(ascending=False).astype(int)
            }).sort_values(by="SYAI Score", ascending=False)

            st.success("SYAI Ranking Completed")
            st.dataframe(result_df)
        except Exception as e:
            st.error(f"An error occurred during computation: {e}")
