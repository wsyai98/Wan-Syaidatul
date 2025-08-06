import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SYAI-Rank", layout="wide")

st.title("SYAI-Rank: Empowering Sustainable Decisions through Smart Aggregation")

st.markdown("### Step 1: Upload Decision Matrix (CSV)")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.index = [f"A{i+1}" for i in range(len(df))]
    st.write("### Decision Matrix")
    st.dataframe(df)

    num_criteria = df.shape[1]
    criteria_weights = []
    criteria_types = []

    st.markdown("### Step 2: Input Criteria Weights and Types")
    cols1, cols2 = st.columns(2)

    with cols1:
        st.subheader("Criteria Weights")
        for col in df.columns:
            weight = st.number_input(f"Weight for {col}", min_value=0.0, max_value=1.0, step=0.01, value=round(1/num_criteria, 2))
            criteria_weights.append(weight)

    with cols2:
        st.subheader("Criteria Types")
        for col in df.columns:
            ctype = st.selectbox(f"Type for {col}", ["Benefit", "Cost", "Ideal"])
            criteria_types.append(ctype)

    if st.button("Run SYAI Method"):
        matrix = df.to_numpy(dtype=float)
        weights = np.array(criteria_weights)
        types = criteria_types
        norm_matrix = np.zeros_like(matrix)

        # Step 3.1: Normalize based on type
        ideal_values = {}
        for j in range(num_criteria):
            col = matrix[:, j]
            if types[j] == "Benefit":
                norm_matrix[:, j] = col / col.max()
            elif types[j] == "Cost":
                norm_matrix[:, j] = col.min() / col
            elif types[j] == "Ideal":
                ideal = (col.max() + col.min()) / 2
                ideal_values[df.columns[j]] = round(ideal, 4)
                norm_matrix[:, j] = 1 - abs(col - ideal) / (col.max() - col.min() + 1e-9)

        st.markdown("### Normalized Matrix")
        st.dataframe(pd.DataFrame(norm_matrix, index=df.index, columns=df.columns))

        # Optional: Show computed ideal values
        if ideal_values:
            st.subheader("Computed Ideal Target Values")
            st.write(pd.DataFrame.from_dict(ideal_values, orient='index', columns=['Ideal Value']))

        # Step 3.2: Weighted Normalized Matrix
        weighted_matrix = norm_matrix * weights

        st.markdown("### Step 3: Compute SYAI Ranking")

        beta = st.slider("Select β (balance between ideal and anti-ideal)", 0.0, 1.0, 0.5, step=0.01)

        # Step 3.3: Compute Distances
        D_plus = np.sqrt(((1 - weighted_matrix) ** 2).sum(axis=1))
        D_minus = np.sqrt((weighted_matrix ** 2).sum(axis=1))

        # Step 3.4: Compute SYAI Scores
        scores = ((1 - beta) * D_minus) / (beta * D_plus + (1 - beta) * D_minus + 1e-9)

        # Step 3.5: Ranking
        results = pd.DataFrame({
            'Alternative': df.index,
            'SYAI Score': scores,
            'Rank': scores.argsort()[::-1].argsort() + 1
        }).sort_values(by='SYAI Score', ascending=False).reset_index(drop=True)

        st.success("✅ SYAI Method Applied Successfully!")
        st.write("### Final Ranking")
        st.dataframe(results)
