import streamlit as st
import pandas as pd
import numpy as np

# -------------------------------
# SYAI-Rank — Reference-Accurate
# -------------------------------

st.set_page_config(page_title="SYAI-Rank", layout="wide")
st.title("SYAI-Rank: Empowering Sustainable Decisions through Smart Aggregation")

# Constants (fixed by method)
C = 0.01  # normalization floor per reference
st.caption(f"Normalization uses range-based formula with C = {C}.")

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
                 weights: list[float],
                 beta: float) -> tuple[pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """Return (result_df, D_plus, D_minus, closeness)."""
    # Ensure numeric & aligned
    df_numeric = df.apply(pd.to_numeric, errors="coerce")
    if df_numeric.isna().any().any():
        st.warning("Non-numeric values were coerced to NaN. Please verify your data.")

    # --- Normalization ---
    normalized = pd.DataFrame(index=df_numeric.index, columns=df_numeric.columns, dtype=float)
    for j, col in enumerate(df_numeric.columns):
        ctype = types[j]
        goal_val = ideals.get(col)
        normalized[col] = normalize_column(df_numeric[col], ctype, goal_val)

    # --- Weights (as labeled Series for safe alignment) ---
    w = pd.Series(weights, index=df_numeric.columns, dtype=float)
    weighted = normalized.mul(w, axis=1)

    # --- Ideal / Anti-ideal on WEIGHTED matrix ---
    ideal = weighted.max(axis=0)
    anti_ideal = weighted.min(axis=0)

    # --- Distances (L1 / Manhattan) ---
    D_plus = (weighted.sub(ideal, axis=1).abs()).sum(axis=1)
    D_minus = (weighted.sub(anti_ideal, axis=1).abs()).sum(axis=1)

    # --- Closeness score ---
    denom = beta * D_plus + (1 - beta) * D_minus
    denom = denom.replace(0, np.finfo(float).eps)
    closeness = ((1 - beta) * D_minus) / denom

    # --- Results ---
    result = pd.DataFrame({
        "D+": D_plus,
        "D-": D_minus,
        "Closeness Score": closeness
    })
    result["Rank"] = result["Closeness Score"].rank(ascending=False, method="min").astype(int)
    result = result.sort_values("Closeness Score", ascending=False)
    return result, D_plus, D_minus, closeness

# ===== Sidebar: sample file =====
with st.sidebar:
    st.markdown("### Example CSV")
    st.markdown("Download a ready-to-run example for quick testing.")
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
    st.info("Tip: After upload, set types to Cost/Benefit/Cost/Ideal and goal=60, β=0.5 to reproduce the paper’s numbers.")

# ===== Step 1: Upload =====
st.header("Step 1: Upload Decision Matrix")
uploaded = st.file_uploader("Upload CSV (first column can be 'Alternative' for index).", type=["csv"])

df = None
if uploaded:
    df = pd.read_csv(uploaded)
    # If user provided an Alternative column, make it the index
    if "Alternative" in df.columns:
        df = df.set_index("Alternative")
    else:
        # Otherwise, keep numeric columns and auto index
        pass
    st.subheader("Decision Matrix")
    st.dataframe(df)

# Optional: quick demo button (loads the example without uploading)
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
    # ===== Step 2: Weights & Types =====
    st.header("Step 2: Criteria Weights and Types")

    num_criteria = df.shape[1]
    default_w = np.repeat(1/num_criteria, num_criteria)

    st.subheader("Weights")
    weights = []
    for i, col in enumerate(df.columns):
        w = st.number_input(
            f"Weight for {col}",
            min_value=0.0, max_value=1.0, step=0.01,
            value=float(np.round(default_w[i], 2)),
            key=f"w_{col}", format="%.2f"
        )
        weights.append(w)

    if st.toggle("Normalize weights to sum = 1", value=True):
        total = sum(weights)
        if total > 0:
            weights = [w/total for w in weights]

    st.subheader("Types & (optional) Ideal/Goal values")
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

    # ===== Step 3: β and Run =====
    st.header("Step 3: Compute SYAI")
    beta = st.slider("β (blend of D+ and D- in closeness score)", 0.0, 1.0, 0.5, 0.01)

    if st.button("Run SYAI"):
        result, Dp, Dm, close = compute_syai(df, types, goal_values, weights, beta)

        # Recompute the intermediate tables for display:
        # (We repeat small parts to show normalized/weighted/ideal explicitly.)
        # Normalized:
        normalized_show = pd.DataFrame(index=df.index, columns=df.columns, dtype=float)
        for j, col in enumerate(df.columns):
            normalized_show[col] = normalize_column(df[col], types[j], goal_values.get(col))

        # Weighted:
        w_series = pd.Series(weights, index=df.columns, dtype=float)
        weighted_show = normalized_show.mul(w_series, axis=1)

        ideal_show = weighted_show.max(axis=0)
        anti_show = weighted_show.min(axis=0)

        st.subheader("Normalized Decision Matrix")
        st.dataframe(normalized_show.style.format("{:.4f}"))

        st.subheader("Weighted Normalized Matrix")
        st.dataframe(weighted_show.style.format("{:.4f}"))

        st.subheader("Yielded Ideal (A⁺) and Anti-Ideal (A⁻)")
        c1, c2 = st.columns(2)
        with c1:
            st.write("A⁺ (column-wise max of weighted):")
            st.write(ideal_show)
        with c2:
            st.write("A⁻ (column-wise min of weighted):")
            st.write(anti_show)

        st.subheader("Distances to A⁺ and A⁻ (L1 / Manhattan)")
        dist_df = pd.DataFrame({"D+": Dp, "D-": Dm})
        st.dataframe(dist_df.style.format("{:.6f}"))

        st.header("Final Ranking (SYAI)")
        st.dataframe(
            result.reset_index().rename(columns={"index": "Alternative"}).style.format({
                "D+": "{:.6f}",
                "D-": "{:.6f}",
                "Closeness Score": "{:.6f}"
            })
        )

        with st.expander("Notes"):
            st.markdown(
                "- **Normalization**: $C + (1-C)\\left(1-\\frac{|x-x^*|}{R}\\right)$ with $C=0.01$, "
                "$R=$ column range, and $x^*$ from type (max/min/goal).\n"
                "- **Weights** multiply the normalized matrix **before** computing A⁺/A⁻.\n"
                "- **Distances** are L1 (sum of absolute differences), matching the reference.\n"
                "- **Closeness**: $\\dfrac{(1-\\beta)D^-}{\\beta D^+ + (1-\\beta)D^-}$.\n"
                "- Use the example to reproduce published numbers (A⁺, A⁻, D⁺, D⁻, closeness)."
            )
