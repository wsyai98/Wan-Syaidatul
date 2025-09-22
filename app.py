import streamlit as st
import pandas as pd
import numpy as np

# =========================
# SYAI-Rank (Reference-Accurate)
# =========================

st.set_page_config(page_title="SYAI-Rank", layout="wide")

st.title("SYAI-Rank: Empowering Sustainable Decisions through Smart Aggregation")

# --- Constants (per reference code) ---
C = 0.01  # normalization floor

st.caption(f"Normalization floor C is fixed at **{C}** (per reference implementation).")

# ========== Step 1: Upload ==========
st.header("Step 1: Upload Decision Matrix")
uploaded_file = st.file_uploader("Upload your decision matrix in CSV format", type=["csv"])

if uploaded_file:
    # Expect first column = Alternative/index
    df = pd.read_csv(uploaded_file, index_col=0)
    df.index.name = "Alternative"
    st.subheader("Decision Matrix")
    st.dataframe(df)

    # Basic derived info
    num_criteria = df.shape[1]
    default_weights = [round(1 / num_criteria, 2)] * num_criteria

    # ========== Step 2: Weights & Types ==========
    st.header("Step 2: Input Criteria Weights and Types")

    # Weights
    st.subheader("Criteria Weights")
    weights = []
    for i, col in enumerate(df.columns):
        w = st.number_input(
            f"Weight for {col}",
            min_value=0.0, max_value=1.0, step=0.01,
            value=default_weights[i], format="%.2f",
            key=f"w_{col}"
        )
        weights.append(w)

    # Normalize weight vector if user wants
    if st.toggle("Normalize weights to sum = 1", value=True):
        total_w = sum(weights)
        if total_w > 0:
            weights = [w / total_w for w in weights]

    # Types + Ideal (Goal) values
    st.subheader("Criteria Types")
    types = []
    ideal_values = {}
    for col in df.columns:
        c_type = st.selectbox(
            f"Type for {col}",
            options=["Benefit", "Cost", "Ideal (Goal)"],
            index=0,
            key=f"type_{col}"
        )
        types.append(c_type)
        if c_type == "Ideal (Goal)":
            default_goal = float(df[col].mean())
            val = st.number_input(
                f"Ideal (Goal) value for {col}",
                value=default_goal,
                key=f"ideal_val_{col}"
            )
            ideal_values[col] = val

    # ========== Step 3: SYAI ==========
    st.header("Step 3: Compute SYAI Ranking")

    # β selector (global, as in the reference code)
    beta = st.slider("Beta (β) — Emphasis on closeness to Ideal vs Anti-Ideal",
                     min_value=0.0, max_value=1.0, value=0.9, step=0.01)

    if st.button("Run SYAI Method"):
        # Ensure numeric
        df_numeric = df.apply(pd.to_numeric, errors="coerce")
        if df_numeric.isna().any().any():
            st.warning("Non-numeric values detected and coerced to NaN. Please verify your data.")
        weights_arr = np.array(weights, dtype=float)

        # --- Step 2 (Reference): Normalize with floor C and range R ---
        normalized_matrix = pd.DataFrame(index=df_numeric.index, columns=df_numeric.columns, dtype=float)

        for j, col in enumerate(df_numeric.columns):
            x = df_numeric[col].astype(float)
            x_min, x_max = x.min(), x.max()
            R = x_max - x_min

            # choose x* per type
            c_type = types[j]
            if c_type == "Benefit":
                x_star = x_max
            elif c_type == "Cost":
                x_star = x_min
            else:  # "Ideal (Goal)"
                x_star = ideal_values.get(col, float(x.mean()))

            if R == 0 or np.isclose(R, 0.0):
                # Degenerate column: all same values → treat as fully satisfied
                normalized = pd.Series(1.0, index=x.index, dtype=float)
            else:
                normalized = C + (1 - C) * (1 - (x - x_star).abs() / R)
                # clip to [C, 1] for safety
                normalized = normalized.clip(lower=C, upper=1.0)

            normalized_matrix[col] = normalized

        st.subheader("Normalized Decision Matrix")
        st.dataframe(normalized_matrix.style.format("{:.4f}"))

        # --- Step 3 (Reference): Weighted normalized matrix ---
        weighted_matrix = normalized_matrix.multiply(weights_arr, axis=1)

        st.subheader("Weighted Normalized Matrix")
        st.dataframe(weighted_matrix.style.format("{:.4f}"))

        # --- Step 4 (Reference): Ideal & Anti-Ideal (column-wise) ---
        ideal_solution = weighted_matrix.max(axis=0)
        anti_ideal_solution = weighted_matrix.min(axis=0)

        st.subheader("Ideal (Best) Values")
        st.write(ideal_solution)

        st.subheader("Anti-Ideal (Worst) Values")
        st.write(anti_ideal_solution)

        # --- Step 5 (Reference): L1 distances & Closeness Score ---
        # D+ = sum |row - ideal| ; D- = sum |row - anti-ideal|
        D_plus = weighted_matrix.apply(lambda row: (row - ideal_solution).abs().sum(), axis=1)
        D_minus = weighted_matrix.apply(lambda row: (row - anti_ideal_solution).abs().sum(), axis=1)

        # Closeness score per reference
        # ((1 - beta) * D-) / (beta * D+ + (1 - beta) * D-)
        denom = beta * D_plus + (1 - beta) * D_minus
        # Avoid divide-by-zero
        denom = denom.replace(0, np.finfo(float).eps)
        closeness_score = ((1 - beta) * D_minus) / denom

        # --- Step 6 (Reference): Rank ---
        result_df = pd.DataFrame({
            "Alternative": weighted_matrix.index,
            "D+": D_plus.values,
            "D-": D_minus.values,
            "Closeness Score": closeness_score.values
        }).set_index("Alternative")

        result_df["Rank"] = result_df["Closeness Score"].rank(ascending=False, method="min").astype(int)
        result_df = result_df.sort_values(by="Closeness Score", ascending=False)

        st.header("Final Ranking (SYAI)")
        st.dataframe(
            result_df.reset_index().style.format({
                "D+": "{:.4f}",
                "D-": "{:.4f}",
                "Closeness Score": "{:.4f}"
            })
        )

        with st.expander("Notes on this implementation"):
            st.markdown(
                "- Normalization strictly follows the reference: **range-based with floor C=0.01** and target **x\\*** per type.\n"
                "- **Distances are L1 (Manhattan)**, matching your reference snippet (not Euclidean).\n"
                "- **β is a single global parameter**, as in the reference code; set with the slider.\n"
                "- For **Ideal (Goal)** criteria, you can input the **target value** per column."
            )
