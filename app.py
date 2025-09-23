# app.py
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import altair as alt

st.set_page_config(page_title="SYAI-Rank", layout="wide")
st.title("SYAI-Rank (C=0.01, L1 distances, deferred weight normalization)")

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

def compute_syai(df: pd.DataFrame,
                 types: list[str],
                 ideals: dict[str, float],
                 weights: pd.Series,
                 beta: float):
    X = df.apply(pd.to_numeric, errors="coerce")
    if X.isna().any().any():
        st.warning("Non-numeric values were coerced to NaN. Check your data.")

    # 1) normalize
    N = pd.DataFrame(index=X.index, columns=X.columns, dtype=float)
    for j, col in enumerate(X.columns):
        N[col] = normalize_column(X[col], types[j], ideals.get(col))

    # 2) weight
    w = weights.reindex(X.columns).astype(float)
    W = N.mul(w, axis=1)

    # 3) A+ / A-
    A_plus = W.max(axis=0)
    A_minus = W.min(axis=0)

    # 4) L1 distances
    D_plus = (W.sub(A_plus, axis=1).abs()).sum(axis=1)
    D_minus = (W.sub(A_minus, axis=1).abs()).sum(axis=1)

    # 5) closeness
    denom = beta * D_plus + (1 - beta) * D_minus
    denom = denom.replace(0, np.finfo(float).eps)
    closeness = ((1 - beta) * D_minus) / denom

    res = pd.DataFrame({"D+": D_plus, "D-": D_minus, "Closeness Score": closeness})
    res["Rank"] = res["Closeness Score"].rank(ascending=False, method="min").astype(int)
    res = res.sort_values("Closeness Score", ascending=False)

    return res, N, W, A_plus, A_minus, w

def normalize_weights_any(raw_w: pd.Series) -> pd.Series:
    raw_w = raw_w.fillna(0).astype(float)
    total = raw_w.sum()
    if total <= 0:
        st.warning("All custom weights are zero; defaulting to equal weights.")
        return pd.Series([1.0/len(raw_w)]*len(raw_w), index=raw_w.index, dtype=float)
    return raw_w / total

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### Navigation")
    tab = st.radio("Go to:", ["SYAI Ranking", "Comparison with Other Methods"])
    st.markdown("---")
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
    run_test_click = st.button("Reproduce Paper Example (Test)")

# persist test mode
if "run_test" not in st.session_state:
    st.session_state.run_test = False
if run_test_click:
    st.session_state.run_test = True

# ---------- SYAI TAB ----------
if tab == "SYAI Ranking":
    st.header("Step 1: Upload Decision Matrix")
    file = st.file_uploader("Upload CSV (first column must be Alternative)", type=["csv"])

    df = None
    if st.session_state.run_test:
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
        # Step 2: Types
        st.header("Step 2: Define Criteria Types")
        types, ideals = [], {}
        if st.session_state.run_test:
            default_types = {"Cost": "Cost", "Quality": "Benefit",
                             "Delivery Time": "Cost", "Temperature": "Ideal (Goal)"}
            default_goal = {"Temperature": 60.0}
        else:
            default_types, default_goal = {}, {}

        for col in df.columns:
            default_idx = 0
            if col in default_types:
                default_idx = {"Benefit": 0, "Cost": 1, "Ideal (Goal)": 2}[default_types[col]]
            ctype = st.selectbox(f"Type for {col}",
                                 ["Benefit", "Cost", "Ideal (Goal)"],
                                 index=default_idx, key=f"type_{col}")
            types.append(ctype)
            if ctype == "Ideal (Goal)":
                val_default = float(default_goal.get(col, df[col].mean()))
                val = st.number_input(f"Ideal (Goal) value for {col}",
                                      value=val_default, key=f"goal_{col}")
                ideals[col] = float(val)

        # Step 3: Weights
        st.header("Step 3: Set Weights")
        m = df.shape[1]
        if st.session_state.run_test:
            raw_w = pd.Series([1.0/m]*m, index=df.columns, dtype=float)
            st.info("Test mode uses equal weights to match the paper example.")
        else:
            mode = st.radio("Weighting scheme", ["Equal (1/m)", "Custom"], horizontal=True)
            if mode == "Custom":
                cols = st.columns(min(4, m))
                weight_inputs = {}
                for j, col in enumerate(df.columns):
                    with cols[j % len(cols)]:
                        weight_inputs[col] = st.number_input(
                            f"w({col})", min_value=0.0, value=0.0,
                            step=0.001, format="%.6f", key=f"w_{col}"
                        )
                raw_w = pd.Series(weight_inputs, dtype=float)
                st.write("Raw weights entered:")
                st.dataframe(raw_w.to_frame("Raw").T)
            else:
                raw_w = pd.Series([1.0/m]*m, index=df.columns, dtype=float)
                st.caption("Equal weights selected (1/m each).")

        # Step 4: β + Run
        st.header("Step 4: Compute SYAI")
        beta = st.slider("β (blend of D+ and D-)", 0.0, 1.0, 0.5, 0.01)

        if st.button("Run SYAI"):
            w = normalize_weights_any(raw_w)
            result, N, W, A_plus, A_minus, w_used = compute_syai(df, types, ideals, w, beta)

            st.subheader("Normalized weights used (sum=1)")
            st.dataframe(w_used.to_frame("Weight").T.style.format("{:.6f}"))

            st.subheader("Final Ranking (SYAI)")
            st.dataframe(
                result.reset_index().rename(columns={"index": "Alternative"}).style.format({
                    "D+": "{:.6f}", "D-": "{:.6f}", "Closeness Score": "{:.6f}",
                })
            )

            # ---------- Visualizations (Altair) ----------
            vis_df = result.sort_values("Rank").reset_index().rename(columns={"index": "Alternative"})
            vis_df["Alternative"] = vis_df["Alternative"].astype(str)

            st.subheader("Ranking Visualization — Bar")
            bar = (
                alt.Chart(vis_df)
                .mark_bar()
                .encode(
                    x=alt.X("Alternative:N", sort=None, title="Alternative"),
                    y=alt.Y("Closeness Score:Q", title="Closeness Score"),
                    color=alt.Color("Alternative:N", legend=None),
                    tooltip=["Alternative", alt.Tooltip("Closeness Score:Q", format=".4f"), "Rank:Q"],
                )
                .properties(height=360)
            )
            st.altair_chart(bar, use_container_width=True)

            st.subheader("Ranking Visualization — Line")
            line = (
                alt.Chart(vis_df)
                .mark_line(point=True)
                .encode(
                    x=alt.X("Rank:O", title="Rank (1 = best)"),
                    y=alt.Y("Closeness Score:Q", title="Closeness Score"),
                    tooltip=["Alternative", "Rank:Q", alt.Tooltip("Closeness Score:Q", format=".4f")],
                    color=alt.value("#4C78A8"),
                )
                .properties(height=320)
            )
            st.altair_chart(line, use_container_width=True)

# ---------- COMPARISON TAB ----------
if tab == "Comparison with Other Methods":
    st.header("Comparison of SYAI with Other MCDM Methods")
    st.markdown("""
    This section provides a comparison of **SYAI** against TOPSIS, VIKOR, SAW, COBRA,
    WASPAS, and MOORA. Use either **URL** (e.g., raw GitHub) or **upload** the images.
    """)

    st.markdown("#### Option A: Load images from URL (e.g., raw GitHub links)")
    url_scatter = st.text_input("Scatter matrix image URL", placeholder="https://raw.githubusercontent.com/<user>/<repo>/<branch>/scatter_matrix.png")
    url_corr    = st.text_input("Correlation heatmap image URL", placeholder="https://raw.githubusercontent.com/<user>/<repo>/<branch>/corr_matrix.png")

    shown_any = False
    if url_scatter:
        st.image(url_scatter, caption="Scatter Matrix for Method Scores", use_container_width=True)
        shown_any = True
    if url_corr:
        st.image(url_corr, caption="Correlation Heatmap of Method Scores", use_container_width=True)
        shown_any = True

    st.markdown("#### Option B: Or upload the images")
    up_scatter = st.file_uploader("Upload scatter matrix (.png/.jpg)", type=["png", "jpg", "jpeg"], key="up_scatter")
    up_corr    = st.file_uploader("Upload correlation heatmap (.png/.jpg)", type=["png", "jpg", "jpeg"], key="up_corr")

    if up_scatter is not None:
        st.image(up_scatter, caption="Scatter Matrix for Method Scores (uploaded)", use_container_width=True)
        shown_any = True
    if up_corr is not None:
        st.image(up_corr, caption="Correlation Heatmap of Method Scores (uploaded)", use_container_width=True)
        shown_any = True

    if not shown_any:
        # fallback to local files if present
        scatter_path = Path("scatter_matrix.png")
        corr_path = Path("corr_matrix.png")
        if scatter_path.exists():
            st.image(str(scatter_path), caption="Scatter Matrix for Method Scores", use_container_width=True)
            shown_any = True
        if corr_path.exists():
            st.image(str(corr_path), caption="Correlation Heatmap of Method Scores", use_container_width=True)
            shown_any = True
        if not shown_any:
            st.warning("Provide URLs or upload images to display the comparison visuals.")

    st.markdown("""
    **How to read this:**
    - The **scatter matrix** shows pairwise score relationships (each dot = one alternative).
    - The **correlation heatmap** highlights similarity of scores/rankings across methods
      (darker cells = stronger agreement).
    """)
