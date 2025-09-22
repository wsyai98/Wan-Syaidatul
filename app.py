import streamlit as st
import pandas as pd
import numpy as np

# -------------------------------
# SYAI-Rank — Simplified Version
# -------------------------------

st.set_page_config(page_title="SYAI-Rank", layout="wide")
st.title("SYAI-Rank: Smart Aggregation for Ranking Alternatives")

# Constants
C = 0.01  # normalization floor

st.caption(f"Normalization uses range-based formula with C = {C}. Equal weights are applied automatically.")

# ===== Utilities =====
def normalize_column(x: pd.Series, ctype: str, goal_val: float | None) -> pd.Series:
    """Range-based normalization with floor C, using target x* per criterion type."""
    x = x.astype(float)
    R = x.max() - x.min()

    if ctype == "Benefit":
        x_star = x.max()
    elif ctype == "Cost":
        x_star = x.min()
    else:  # "Ideal (Goal)"
        x_star = float(goal_val) if goal_val is not None else float(x.mean())

    if R == 0 or np.isclose(R, 0.0):
        norm = pd.Series(1.0, index=x.index, dtype=float)
    else:
        norm = C + (1 - C) * (1 - (x - x_star).abs() / R)
        norm = norm.clip(lower=C, upper=1.0)
    return norm

def compute_syai(df: pd.DataFrame,
                 types: list[str],
                 ideals: dict[str, float],
                 beta: float) -> pd.DataFrame:
    """Compute SYAI results with equal weights."""
    df_numeric = df.apply(pd.to_numeric, errors="coerce")

    # Normalize
    normalized = pd.DataFrame(index=df_numeric.index, columns=df_numeric.columns, dtype=float)
    for j, col in enumerate(df_numeric.columns):
        normalized[col] = normalize_column(df_numeric[col], types[j], ideals.get(col))

    # Equal weights
    num_criteria = df_numeric.shape[1]
    w = pd.Series([1/num_criteria]*num_criteria, index=df_numeric.columns, dtype=float)
    weighted = normalized.mul(w, axis=1)

    # Ideal / Anti-ideal
    ideal = weighted.max(axis=0)
    anti_ideal = weighted.min(axis=0)

    # Distances (L1)
    D_plus = (weighted.sub(ideal, axis=1).abs()).sum(axis=1)
    D_minus = (weighted.sub(anti_ideal, axis=1).abs()).sum(axis=1)

    # Closeness score
    denom = beta * D_plus + (1 - beta) * D_minus
    denom = denom.replace(0, np.finfo(float).eps)
    closeness = ((1 - beta) * D_minus) / denom

    # Results
    result = pd.DataFrame({
        "D+": D_plus,
        "D-": D_minus,
        "Closeness Score": closeness
    })
    result["Rank"] = result["Closeness Score"].rank(ascending=False, method="min").astype(int)
    result = result.sort_values("Closeness Score", ascending=False)
    return result, normalized, weighted, ideal, anti_ideal

# ===== Sidebar: Example CSV =====
with st.sidebar:
    st.markdown("### Example CSV")
    st.download_button(
        label="Download sample.csv",
        data=(
            "Alternative,Cost,Quality,Delivery Time,Temperature\n"
            "A1,200,8,4,30\n"
            "A2,250,7,5,60\n"
            "A3,300,9,6,85\n"
        ),
        file_name="sample.csv",
        mime="text/csv"
    )
    st.info("Upload CSV with first column = Alternative.")

# ===== Step 1: Upload =====
st.header("Step 1: Upload Decision Matrix")
uploaded = st.file_uploader("Upload CSV (first column = Alternative).", type=["csv"])

df = None
if uploaded:
    df = pd.read_csv(uploaded, index_col=0)
    df.index.name = "Alternative"
    st.subheader("Decision Matrix")
    st.dataframe(df)

# Optional: quick demo button
if st.button("Load Example Data"):
    df = pd.DataFrame({
        "Cost": [200, 250, 300],
        "Quality": [8, 7, 9],
        "Delivery Time": [4, 5, 6],
        "Temperature": [30, 60, 85]
    }, index=["A1", "A2", "A3"])
    st.subheader("Decision Matrix (Example)")
    st.dataframe(df)

if df is not None and not df.empty:
    # ===== Step 2: Types & Goals =====
    st.header("Step 2: Define Criteria Types")
    types = []
    goal_values = {}
    for col in df.columns:
        ctype = st.selectbox(
            f"Type for {col}",
            options=["Benefit", "Cost", "Ideal (Goal)"],
            index=0,
            key=f"type_{col}"
        )
        types.append(ctype)
        if ctype == "Ideal (Goal)":
            val = st.number_input(
                f"Ideal (Goal) value for {col}",
                value=float(df[col].mean()),
                key=f"goal_{col}"
            )
            goal_values[col] = val

    # ===== Step 3: β =====
    st.header("Step 3: Compute SYAI")
    beta = st.slider("β (blend of D+ and D- in closeness score)", 0.0, 1.0, 0.5, 0.01)

    if st.button("Run SYAI"):
        result, norm, weighted, ideal, anti = compute_syai(df, types, goal_values, beta)

        st.subheader("Normalized Decision Matrix")
        st.dataframe(norm.style.format("{:.4f}"))

        st.subheader("Weighted Normalized Matrix (equal weights)")
        st.dataframe(weighted.style.format("{:.4f}"))

        st.subheader("Yielded Ideal (A⁺) and Anti-Ideal (A⁻)")
        c1, c2 = st.columns(2)
        with c1:
            st.write("A⁺:")
            st.write(ideal)
        with c2:
            st.write("A⁻:")
            st.write(anti)

        st.header("Final Ranking (SYAI)")
        st.dataframe(
            result.reset_index().rename(columns={"index": "Alternative"}).style.format({
                "D+": "{:.6f}",
                "D-": "{:.6f}",
                "Closeness Score": "{:.6f}"
            })
        )
