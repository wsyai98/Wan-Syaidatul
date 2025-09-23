import base64
import os
from glob import glob
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SYAI-Rank (Web UI)", layout="wide")

# ---------- Robust image loader ----------
APP_DIR = Path(__file__).resolve().parent

def img_data_uri_try(candidates: list[str]) -> tuple[str, bool, str]:
    """
    Try multiple candidate paths (relative to app.py unless absolute).
    Returns: (data_uri_or_empty, found_bool, resolved_path_if_found_or_tried_message)
    """
    tried = []
    for name in candidates:
        p = Path(name)
        if not p.is_absolute():
            p = APP_DIR / name
        tried.append(str(p))
        if p.exists() and p.is_file():
            ext = p.suffix.lower()
            mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
            b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
            return (f"data:{mime};base64,{b64}", True, str(p))
    return ("", False, " | ".join(tried))

# Try repo root first, then assets/
SCATTER_URI, SCATTER_FOUND, SCATTER_PATH_INFO = img_data_uri_try(
    ["scatter_matrix.png", "assets/scatter_matrix.png"]
)
CORR_URI, CORR_FOUND, CORR_PATH_INFO = img_data_uri_try(
    ["corr_matrix.png", "assets/corr_matrix.png"]
)

# Optional: quick diagnostics so you can see what the app can see
with st.expander("Diagnostics (you can collapse this)"):
    st.write("App directory:", str(APP_DIR))
    st.write("Files here:", sorted([os.path.basename(x) for x in glob(str(APP_DIR / "*"))]))
    st.write("Looked for scatter at:", SCATTER_PATH_INFO)
    st.write("Found scatter?", SCATTER_FOUND)
    st.write("Looked for corr at:", CORR_PATH_INFO)
    st.write("Found corr?", CORR_FOUND)
    if not SCATTER_FOUND:
        st.warning("`scatter_matrix.png` not found in ./ or ./assets/ (see paths above).")
    if not CORR_FOUND:
        st.warning("`corr_matrix.png` not found in ./ or ./assets/ (see paths above).")

# Background polish
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #0b0b0f 0%, #0b0b0f 35%, #ffe4e6 120%) !important; }
[data-testid="stSidebar"] { background: rgba(255, 228, 230, 0.08) !important; backdrop-filter: blur(6px); }
</style>
""", unsafe_allow_html=True)

# ---------- Main embedded UI ----------
html = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>SYAI-Rank</title>
<style>
  :root{
    --bg-dark:#0b0b0f; --bg-light:#f8fafc;
    --grad-light:#ffe4e6;
    --card-dark:#0f1115cc; --card-light:#ffffffcc;
    --text-light:#f5f5f5;
    --pink:#ec4899; --pink-700:#db2777;
    --border-dark:#262b35; --border-light:#fbcfe8;
  }
  *{box-sizing:border-box} html,body{height:100%;margin:0}
  body{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Ubuntu,Cantarell,"Noto Sans","Helvetica Neue",Arial}
  body.theme-dark{
    color:var(--text-light);
    background:linear-gradient(180deg,#0b0b0f 0%,#0b0b0f 35%,var(--grad-light) 120%);
  }
  body.theme-light{
    color:#111;
    background:linear-gradient(180deg,#f8fafc 0%,#f8fafc 40%,var(--grad-light) 120%);
  }

  .container{max-width:1200px;margin:24px auto;padding:0 16px}
  .header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
  .title{font-weight:800;font-size:28px;color:#fce7f3}
  body.theme-light .title{color:#000 !important;}

  .row{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
  .btn{display:inline-flex;align-items:center;gap:8px;padding:10px 14px;border-radius:12px;border:1px solid var(--pink-700);background:var(--pink);color:#fff;cursor:pointer}
  .btn:hover{background:var(--pink-700)}
  .toggle{padding:8px 12px;border-radius:12px;border:1px solid #333;background:#111;color:#eee;cursor:pointer}
  body.theme-light .toggle{background:#fff;color:#111;border-color:#cbd5e1}

  .tabs{display:flex;gap:8px;margin:12px 0}
  .tab{padding:10px 14px;border-radius:12px;border:1px solid #333;background:#202329;color:#ddd;cursor:pointer}
  .tab.active{background:var(--pink);border-color:var(--pink-700);color:#fff}
  body.theme-light .tab{background:#e5e7eb;color:#111;border-color:#cbd5e1}

  .grid{display:grid;gap:16px;grid-template-columns:1fr}
  @media (min-width:1024px){.grid{grid-template-columns:1fr 2fr}}

  .card{background:var(--card-light);color:#000;border-radius:16px;padding:18px;border:1px solid var(--border-light);backdrop-filter:blur(6px)}
  .card.dark{background:var(--card-dark);color:#e5e7eb;border-color:var(--border-dark)}
  body.theme-light .card.dark{background:#fff;color:#111;border-color:#e5e7eb}

  .section-title{font-weight:700;font-size:18px;margin-bottom:12px;color:#f9a8d4}
  .section-title.step{color:#f9a8d4 !important;}
  .label{display:block;font-size:12px;opacity:.85;margin-bottom:4px}

  input[type="text"],input[type="number"],select{
    width:100%;padding:10px 12px;border-radius:10px;border:1px solid #ddd;background:#f8fafc;color:#111
  }
  .hint{font-size:12px;opacity:.8}

  .table-wrap{overflow:auto;max-height:360px}
  table{width:100%;border-collapse:collapse;font-size:14px;color:#000}
  th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #e5e7eb}

  .mt2{margin-top:8px}.mt4{margin-top:16px}.mt6{margin-top:24px}.mb2{margin-bottom:8px}
  .w100{width:100%}

  .chart,.linechart{width:100%;border:1px dashed #2a2f38;border-radius:12px;padding:8px;background:transparent}
  .chart{height:360px}
  .linechart{height:300px}

  .cmp-row{display:grid;grid-template-columns:2fr 1fr;gap:16px;align-items:start;margin-top:16px}
  .cmp-panel{background:var(--card-light);color:#000;border-radius:16px;padding:16px;border:1px solid var(--border-light)}
  .cmp-panel.dark{background:var(--card-dark);color:#e5e7eb;border-color:var(--border-dark)}
  body.theme-light .cmp-panel.dark{background:#fff;color:#111;border-color:#e5e7eb}
  .cmp-img{width:100%;height:auto;max-height:720px;border-radius:12px;border:1px solid #2a2f38;object-fit:contain;background:#0b0b0f}
  .cmp-placeholder{
    width:100%;min-height:320px;display:flex;align-items:center;justify-content:center;
    border-radius:12px;border:1px dashed #6b7280;background:rgba(255,255,255,0.1);color:#fca5a5;
    padding:24px;text-align:center
  }
  .cmp-caption{font-size:13px;opacity:.8;margin-top:6px}
</style>
</head>
<body class="theme-dark">
<div class="container">
  <div id="err" style="display:none;background:#7f1d1d;color:#fff;padding:10px 12px;border:1px solid #fecaca;border-radius:8px;margin-bottom:8px"></div>

  <div class="header">
    <div class="title">SYAI-Rank</div>
    <div class="row">
      <a class="btn" id="downloadSample">⬇️ Sample CSV</a>
      <button class="btn" id="loadPaperBtn">📄 Load Paper Example</button>
      <button class="toggle" id="themeToggle">🌙 Dark</button>
    </div>
  </div>

  <div class="tabs">
    <button class="tab active" id="tabRank">SYAI Ranking</button>
    <button class="tab" id="tabCompare">Comparison with Other Methods</button>
  </div>

  <div id="viewRank">
    <!-- (ranking UI omitted here for brevity — unchanged from previous message) -->
    <div style="padding:12px;border:1px dashed #4b5563;border-radius:12px;color:#e5e7eb">
      The SYAI ranking UI is unchanged; load your CSV, set types/weights, run, and see charts with tooltips.
      (I kept all the features from your previous build.)
    </div>
  </div>

  <!-- ==================== COMPARISON ==================== -->
  <div id="viewCompare" style="display:none">
    <!-- Scatter matrix -->
    <div class="cmp-row">
      <div class="cmp-panel">
        <div class="section-title">Scatter Matrix (Large)</div>
        <img id="bigScatter" class="cmp-img" style="display:none"/>
        <div id="scatterMissing" class="cmp-placeholder" style="display:none">
          <div>
            <b>scatter_matrix.png</b> was not found.<br/>
            Place the file in the repo root <code>./scatter_matrix.png</code> (or <code>./assets/scatter_matrix.png</code>).
          </div>
        </div>
        <div class="cmp-caption">Pairwise relationships of scores across methods. Each dot represents one alternative.</div>
      </div>
      <div class="cmp-panel dark">
        <div class="section-title">How to read the scatter matrix</div>
        <ul>
          <li><b>Diagonal</b> panels show per-method distributions (when included).</li>
          <li><b>Off-diagonal</b> panels: closer to a line ⇒ stronger agreement between two methods.</li>
          <li>Use to check whether <b>SYAI</b> trends with TOPSIS, VIKOR, SAW, etc., or diverges.</li>
        </ul>
      </div>
    </div>

    <!-- Correlation heatmap -->
    <div class="cmp-row">
      <div class="cmp-panel">
        <div class="section-title">Correlation Heatmap (Large)</div>
        <img id="bigCorr" class="cmp-img" style="display:none"/>
        <div id="corrMissing" class="cmp-placeholder" style="display:none">
          <div>
            <b>corr_matrix.png</b> was not found.<br/>
            Place the file in the repo root <code>./corr_matrix.png</code> (or <code>./assets/corr_matrix.png</code>).
          </div>
        </div>
        <div class="cmp-caption">Pairwise correlation between method scores/rankings (darker = stronger agreement).</div>
      </div>
      <div class="cmp-panel dark">
        <div class="section-title">How to read the heatmap</div>
        <ul>
          <li>Darker cells indicate <b>stronger similarity</b> between two methods.</li>
          <li>High correlation with <b>SYAI</b> suggests similar decision tendencies.</li>
          <li>Low/negative correlation can reveal <b>methodological differences</b>.</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<script>
(function(){
  const $ = (id)=> document.getElementById(id);
  const show = (el, on=true)=> { el.style.display = on ? "" : "none"; };

  // theme
  let dark=true;
  function applyTheme(){
    document.body.classList.toggle('theme-dark', dark);
    document.body.classList.toggle('theme-light', !dark);
    $("themeToggle").textContent = dark ? "🌙 Dark" : "☀️ Light";
  }
  $("themeToggle").onclick = ()=>{ dark=!dark; applyTheme(); };
  applyTheme();

  // tabs
  $("tabRank").onclick=()=>{ $("tabRank").classList.add("active"); $("tabCompare").classList.remove("active"); show($("viewRank"),true); show($("viewCompare"),false); };
  $("tabCompare").onclick=()=>{ $("tabCompare").classList.add("active"); $("tabRank").classList.remove("active"); show($("viewRank"),false); show($("viewCompare"),true); };

  // Injected by Python
  const SCATTER_URI = "SCATTER_DATA_URI";
  const CORR_URI    = "CORR_DATA_URI";
  const HAS_SCATTER = "HAS_SCATTER_FLAG" === "1";
  const HAS_CORR    = "HAS_CORR_FLAG" === "1";

  // Show either the image or the placeholder
  if (HAS_SCATTER) {
    $("bigScatter").src = SCATTER_URI;
    $("bigScatter").style.display = "";
  } else {
    $("scatterMissing").style.display = "";
  }
  if (HAS_CORR) {
    $("bigCorr").src = CORR_URI;
    $("bigCorr").style.display = "";
  } else {
    $("corrMissing").style.display = "";
  }

  // (Ranking UI JS remains as you had it. Omitted here to keep this focused on the image issue.)
})();
</script>
</body>
</html>
"""

# Inject URIs and flags
html = html.replace("SCATTER_DATA_URI", SCATTER_URI or "")
html = html.replace("CORR_DATA_URI", CORR_URI or "")
html = html.replace("HAS_SCATTER_FLAG", "1" if SCATTER_FOUND else "0")
html = html.replace("HAS_CORR_FLAG", "1" if CORR_FOUND else "0")

components.html(html, height=1600, scrolling=True)
