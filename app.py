import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SYAI-Rank", layout="wide")
st.title("SYAI-Rank: Empowering Sustainable Decisions through Smart Aggregation")

# Step 1: Upload Dataset
st.header("Step 1: Upload Decision Matrix")
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Remove unnamed column if exists
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])

    # Set index as A1, A2, A3,...
    df.index = [f"A{i}" for i in range(1, len(df)+1)]

    st.subheader("Uploaded Decision Matrix")
    st.dataframe(df)

    # Step 2: Input Weights and Criteria Types
    st.header("Step 2: Input Criteria Weights and Types")
    num_criteria = df.shape[1]

    weights = []
    types = []

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Criteria Weights")
        for col in df.columns:
            w = st.number_input(f"Weight for {col}", min_value=0.0, max_value=1.0, value=1.0 / num_criteria, step=0.01)
            weights.append(w)
    with col2:
        st.subheader("Criteria Types")
        for col in df.columns:
            t = st.selectbox(f"Type for {col}", ["Benefit", "Cost", "Ideal"])
            types.append(t)

    # Normalize weights
    weights = np.array(weights)
    if weights.sum() == 0:
        weights = np.ones(num_criteria) / num_criteria
    else:
        weights = weights / weights.sum()

    # Step 3: SYAI Method Calculation
    st.header("Step 3: Compute SYAI Ranking")

    beta = st.slider("Select β (balance between Ideal and Anti-Ideal)", 0.0, 1.0, 0.5, step=0.01)

    if st.button("Run SYAI Method"):
        matrix = df.to_numpy(dtype=float)
        norm_matrix = np.zeros_like(matrix)

        # Step 3.1: Normalize based on type
        for j in range(num_criteria):
            col = matrix[:, j]
            if types[j] == "Benefit":
                norm_matrix[:, j] = col / col.max()
            elif types[j] == "Cost":
                norm_matrix[:, j] = col.min() / col
            elif types[j] == "Ideal":
                ideal = (col.max() + col.min()) / 2
                norm_matrix[:, j] = 1 - abs(col - ideal) / (col.max() - col.min() + 1e-9)

        # Step 3.2: Weighted Normalized Matrix
        weighted_matrix = norm_matrix * weights

        # Step 3.3: Compute Distances
        D_plus = np.sqrt(((1 - weighted_matrix) ** 2).sum(axis=1))
        D_minus = np.sqrt((weighted_matrix ** 2).sum(axis=1))

        # Step 3.4: Compute Final SYAI Scores with β
        scores = ((1 - beta) * D_minus) / (beta * D_plus + (1 - beta) * D_minus + 1e-9)

        # Step 3.5: Display Results
        results = pd.DataFrame({
            "Alternative": df.index,
            "SYAI Score": scores,
            "Rank": scores.argsort()[::-1].argsort() + 1
        }).sort_values("Rank")

        st.subheader("SYAI Ranking Results")
        st.dataframe(results.set_index("Alternative"))

        st.success("SYAI computation completed successfully.")
