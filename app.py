import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SYAI-Rank", layout="wide")

st.title("SYAI-Rank: Empowering Sustainable Decisions through Smart Aggregation")

st.header("Step 1: Upload Decision Matrix")
uploaded_file = st.file_uploader("Upload your decision matrix in CSV format", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, index_col=0)
    st.subheader("Decision Matrix")
    st.dataframe(df)

    num_criteria = df.shape[1]
    default_weights = [round(1 / num_criteria, 2)] * num_criteria
    default_types = ["Benefit"] * num_criteria

    st.header("Step 2: Input Criteria Weights and Types")

    st.subheader("Criteria Weights")
    weights = []
    for i, col in enumerate(df.columns):
        w = st.number_input(f"Weight for {col}", min_value=0.0, max_value=1.0, step=0.01, value=default_weights[i], format="%.2f")
        weights.append(w)

    st.subheader("Criteria Types")
    types = []
    ideal_values = {}
    for col in df.columns:
        c_type = st.selectbox(f"Type for {col}", options=["Benefit", "Cost", "Ideal"], index=0, key=f"type_{col}")
        types.append(c_type)
        if c_type == "Ideal":
            val = st.number_input(f"Enter Ideal Value for {col}", value=float(df[col].mean()), key=f"ideal_val_{col}")
            ideal_values[col] = val

    st.header("Step 3: Compute SYAI Ranking")
    beta = st.slider("Beta (β) - Ideal vs Anti-Ideal Impact", 0.0, 1.0, 0.5, 0.01)

    if st.button("Run SYAI Method"):
        df_numeric = df.copy()
        weights = np.array(weights)
        norm_matrix = df_numeric.copy()

        # Normalize
        for i, col in enumerate(df.columns):
            if types[i] == "Benefit":
                norm_matrix[col] = df_numeric[col] / df_numeric[col].max()
            elif types[i] == "Cost":
                norm_matrix[col] = df_numeric[col].min() / df_numeric[col]
            elif types[i] == "Ideal":
                ideal_val = ideal_values.get(col, df_numeric[col].mean())
                norm_matrix[col] = 1 - abs(df_numeric[col] - ideal_val) / ideal_val

        st.subheader("Normalized Decision Matrix")
        st.dataframe(norm_matrix.style.format("{:.4f}"))

        # Weighted normalized matrix
        weighted_matrix = norm_matrix * weights

        # Compute ideal and anti-ideal values
        ideal = weighted_matrix.max()
        anti_ideal = weighted_matrix.min()

        st.subheader("Ideal (Best) Values")
        st.write(ideal)

        st.subheader("Anti-Ideal (Worst) Values")
        st.write(anti_ideal)

        D_plus = np.sqrt(((weighted_matrix - ideal) ** 2).sum(axis=1))
        D_minus = np.sqrt(((weighted_matrix - anti_ideal) ** 2).sum(axis=1))

        # SYAI Score
        scores = ((1 - beta) * D_minus) / (beta * D_plus + (1 - beta) * D_minus)
        df_result = pd.DataFrame({
            "Alternative": df.index,
            "D+": D_plus,
            "D-": D_minus,
            "SYAI Score": scores
        })

        df_result["Rank"] = df_result["SYAI Score"].rank(ascending=False).astype(int)
        df_result = df_result.sort_values(by="SYAI Score", ascending=False)

        st.header("Final Ranking")
        st.dataframe(df_result.reset_index(drop=True).style.format({
            "D+": "{:.4f}",
            "D-": "{:.4f}",
            "SYAI Score": "{:.4f}"
        }))
