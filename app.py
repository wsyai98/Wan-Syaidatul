import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SYAI-Rank", layout="wide")
st.title("SYAI-Rank (C=0.01, L1 distances, equal weights)")

C = 0.01  # normalization floor

# ---------- Core math ----------
def normalize_column(x: pd.Series, ctype: str, goal_val: float | None) -> pd.Series:
    x = x.astype(float)
    R = x.max() - x.min()
    if ctype == "Benefit":
        x_star = x.max()
    elif ctype == "Cost":
        x_star = x.min()
    else:  # Ideal (Goal)
        x_star = float(goal_val) if goal_val is not None else float(x.mean())

    if R == 0 or np.isclose(R, 0.0):
        norm = pd.Series(1.0, index=x.index, dtype=float)
    else:
        norm = C + (1 - C) * (1 - (x - x_star).abs() / R)
        norm = norm.clip(lower=C, upper=1.0)
    return norm

def compute_syai_equal_weights(df: pd.DataFrame,
                               types: list[str],
                               ideals: dict[str, float],
                               beta: float):
    # Ensure numeric
    X = df.apply(pd.to_numeric, errors="coerce")
    if X.isna().any().any():
        st.warning("Non-numeric values were coerced to NaN. Check your data.")

    # 1) Normalize (per column; x* from type)
    N = pd.DataFrame(index=X.index, columns=X.columns, dtype=float)
    for j, col in enumerate(X.columns):
        N[col] = normalize_column(X[col], types[j], ideals.get(col))

    # 2) Equal weights
    m = X.shape[1]
    w = pd.Series([1.0/m] * m, index=X.columns, dtype=float)

    # 3) Weighted matrix
    W = N.mul(w, axis=1)

    # 4) A+ / A- on WEIGHTED matrix
    A_plus = W.max(axis=0)
    A_minus = W.min(axis=0)

    # 5) L1 distances
    D_plus = (W.sub(A_plus, axis=1).abs()).sum(axis=1)
    D_minus = (W.sub(A_minus, axis=1).abs()).sum(axis=1)

    # 6) Closeness
    denom = beta * D_plus + (1 - beta) * D_minus
    denom = denom.replace(0, np.finfo(float).eps)
    closeness = ((1 - beta) * D_minus) / denom

    res = pd.DataFrame({"D+": D_plus, "D-": D_minus, "Closeness Score": closeness})
    res["Rank"] = res["Closeness Score"].rank(ascending=False, method="min").astype(int)
    res = res.sort_values("Closeness Score", ascending=False)

    return res, N, W, A_plus, A_minus

# ---------- Sidebar: sample & test ----------
with st.sidebar:
    st.markdown("### Sample CSV (first column = Alternative)")
    st.download_button(
        "Download sample.csv",
        data=("Alternative,Cost,Quality,Delivery Time,Temperature\n"
              "A1,200,8,4,30\n"
              "A2,250,7,5,60\n"
              "A3,300,9,6,85\n"),
        file_name="sample.csv",
        mime="text/csv",
    )
    st.markdown("---")
    run_test = st.button("Reproduce Paper Example (Test)")

# ---------- Step 1: Data ----------
st.header("Step 1: Upload Decision Matrix")
file = st.file_uploader("Upload CSV (first column must be Alternative)", type=["csv"])

df = None
if run_test:
    # Paper example (locked)
    df = pd.DataFrame({
        "Cost": [200, 250, 300],
        "Quality": [8, 7, 9],
        "Delivery Time": [4, 5, 6],
        "Temperature": [30, 60, 85],
    }, index=["A1", "A2", "A3"])
    df.index.name = "Alternative"
    st.success("Loaded paper example data.")
elif file:
    df = pd.read_csv(file, index_col=0)
    df.index.name = "Alternative"

if df is not None:
    st.subheader("Decision Matrix")
    st.dataframe(df)

if df is not None and not df.empty:
    # ---------- Step 2: Types ----------
    st.header("Step 2: Define Criteria Types")
    types = []
    ideals = {}

    # Default to the paper mapping if we’re in test mode
    default_types = {}
    default_goal = {}
    if run_test:
        default_types = {"Cost": "Cost", "Quality": "Benefit",
                         "Delivery Time": "Cost", "Temperature": "Ideal (Goal)"}
        default_goal = {"Temperature": 60.0}

    for col in df.columns:
        default_idx = 0  # Benefit
        if col in default_types:
            # map to selectbox index
            if default_types[col] == "Cost":
                default_idx = 1
            elif default_types[col] == "Ideal (Goal)":
                default_idx = 2

        ctype = st.selectbox(
            f"Type for {col}",
            ["Benefit", "Cost", "Ideal (Goal)"],
            index=default_idx,
            key=f"type_{col}"
        )
        types.append(ctype)

        if ctype == "Ideal (Goal)":
            val_default = float(default_goal.get(col, df[col].mean()))
            val = st.number_input(
                f"Ideal (Goal) value for {col}",
                value=val_default,
                key=f"goal_{col}"
            )
            ideals[col] = float(val)

    # ---------- Step 3: β ----------
    st.header("Step 3: Compute SYAI")
    beta_default = 0.5 if run_test else 0.5
    beta = st.slider("β (blend of D+ and D-)", 0.0, 1.0, beta_default, 0.01)

    if st.button("Run SYAI"):
        result, N, W, A_plus, A_minus = compute_syai_equal_weights(df, types, ideals, beta)

        st.subheader("Normalized Matrix")
        st.dataframe(N.style.format("{:.6f}"))

        st.subheader("Weighted Matrix (equal weights)")
        st.dataframe(W.style.format("{:.6f}"))

        c1, c2 = st.columns(2)
        with c1:
            st.write("A⁺ (max of weighted)")
            st.write(A_plus)
        with c2:
            st.write("A⁻ (min of weighted)")
            st.write(A_minus)

        st.header("Final Ranking (SYAI)")
        st.dataframe(
            result.reset_index().rename(columns={"index": "Alternative"}).style.format({
                "D+": "{:.6f}",
                "D-": "{:.6f}",
                "Closeness Score": "{:.6f}",
            })
        )

        # --- If we’re in test mode, show expected vs computed
        if run_test:
            st.markdown("### Paper Check (expected vs computed)")
            expected_Dp = pd.Series([0.25875, 0.49500, 0.60750], index=["A1", "A2", "A3"])
            expected_Dm = pd.Series([0.61875, 0.38250, 0.27000], index=["A1", "A2", "A3"])
            expected_C  = pd.Series([0.705128, 0.435897, 0.307692], index=["A1", "A2", "A3"])

            # recompute distances to reference order (A1..A3)
            # pull from result’s underlying values:
            # Better: recompute directly from W, A+/A- in the same order
            Dp = (W.sub(A_plus, axis=1).abs()).sum(axis=1).reindex(expected_Dp.index)
            Dm = (W.sub(A_minus, axis=1).abs()).sum(axis=1).reindex(expected_Dm.index)
            denom = beta * Dp + (1 - beta) * Dm
            denom = denom.replace(0, np.finfo(float).eps)
            Cscore = ((1 - beta) * Dm) / denom

            comp = pd.DataFrame({
                "D+ (expected)": expected_Dp,
                "D+ (computed)": Dp,
                "D- (expected)": expected_Dm,
                "D- (computed)": Dm,
                "Closeness (expected)": expected_C,
                "Closeness (computed)": Cscore
            })
            st.dataframe(comp.style.format("{:.6f}"))

            tol = 1e-6
            ok = (np.allclose(Dp.values, expected_Dp.values, atol=tol) and
                  np.allclose(Dm.values, expected_Dm.values, atol=tol) and
                  np.allclose(Cscore.values, expected_C.values, atol=tol))
            if ok:
                st.success("✅ Matches the paper exactly.")
            else:
                st.error("❌ Does not match the paper. Check types, goal value, and β.")
