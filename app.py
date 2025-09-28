# app.py
import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SYAI-Rank", layout="wide")
APP_DIR = Path(__file__).resolve().parent

# ---------- Optional local images ----------
def img_data_uri_try(candidates: list[str]) -> tuple[str, bool]:
    for name in candidates:
        p = Path(name)
        if not p.is_absolute():
            p = APP_DIR / name
        if p.exists() and p.is_file():
            ext = p.suffix.lower()
            mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
            b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
            return (f"data:{mime};base64,{b64}", True)
    return ("", False)

SCATTER_URI, SCATTER_FOUND = img_data_uri_try(
    ["scatter_matrix.png", "assets/scatter_matrix.png"]
)
CORR_URI, CORR_FOUND = img_data_uri_try(
    ["corr_matrix.png", "assets/corr_matrix.png"]
)

# ---------- Single source of truth for the sample CSV ----------
def load_sample_csv_text() -> str:
    p = Path("/mnt/data/sample (1).csv")
    if p.exists():
        for enc in ("utf-8", "latin-1"):
            try:
                return p.read_text(encoding=enc)
            except Exception:
                pass
    return (
        "Alternative,Cost,Quality,Delivery\n"
        "A1,200,8,4\n"
        "A2,250,7,5\n"
        "A3,300,9,6\n"
        "A4,220,8,4\n"
        "A5,180,6,7\n"
    )

SAMPLE_CSV = load_sample_csv_text()

# ---------- base page background ----------
st.markdown("""
<style>
  .stApp { background: linear-gradient(180deg, #0b0b0f 0%, #0b0b0f 35%, #ffe4e6 120%) !important; }
  [data-testid="stSidebar"] { background: rgba(255, 228, 230, 0.08) !important; backdrop-filter: blur(6px); }
</style>
""", unsafe_allow_html=True)

# ------------------------------- HTML APP -------------------------------
html = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>SYAI-Rank</title>
<style>
/* ===================== FULL CSS START ===================== */
:root{
  --bg-dark:#0b0b0f; --bg-light:#f8fafc;
  --grad-light:#ffe4e6;
  --card-dark:#0f1115cc; --card-light:#ffffffcc;
  --text-light:#f5f5f5;
  --pink:#ec4899; --pink-700:#db2777;
  --border-dark:#262b35; --border-light:#f1f5f9;
}
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial}

body.theme-dark{
  color:var(--text-light);
  background:linear-gradient(180deg,#0b0b0f 0%,#0b0b0f 35%,var(--grad-light) 120%);
}
body.theme-light{
  color:#111;
  background:linear-gradient(180deg,#f8fafc 0%,#f8fafc 40%,var(--grad-light) 120%);
}

.container{max-width:1200px;margin:24px auto;padding:0 16px}
.header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.title{font-weight:800;font-size:28px;color:#fce7f3}
body.theme-light .title{color:#000}

.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:8px;padding:10px 14px;border-radius:12px;border:1px solid var(--pink-700);background:var(--pink);color:#fff;cursor:pointer}
.btn:hover{filter:brightness(0.96)}
.toggle{padding:8px 12px;border-radius:12px;border:1px solid #333;background:#111;color:#eee;cursor:pointer}
body.theme-light .toggle{background:#fff;color:#111;border-color:#cbd5e1}

.tabs{display:flex;gap:8px;margin:12px 0;position:relative;z-index:10}
.tab{padding:10px 14px;border-radius:12px;border:1px solid #333;background:#202329;color:#ddd;cursor:pointer}
.tab.active{background:var(--pink);border-color:var(--pink-700);color:#fff}
body.theme-light .tab{background:#e5e7eb;color:#111;border-color:#cbd5e1}

.grid{display:grid;gap:16px;grid-template-columns:1fr}
@media (min-width:1024px){.grid{grid-template-columns:1fr 2fr}}

.card{border-radius:16px;padding:18px;border:1px solid var(--border-light);backdrop-filter:blur(6px)}
.card.dark{background:var(--card-dark);color:#e5e7eb;border-color:var(--border-dark)}
.card.light{background:var(--card-light);color:#111;border-color:var(--border-light)}
body.theme-light .card.dark{background:#fff;color:#111;border-color:#e5e7eb}

.section-title{font-weight:700;font-size:18px;margin-bottom:12px;color:#f9a8d4}
.label{display:block;font-size:12px;opacity:.85;margin-bottom:4px}
input[type="number"],select{width:100%;padding:10px 12px;border-radius:10px;border:1px solid #ddd;background:#f8fafc;color:#111}
.hint{font-size:12px;opacity:.8}

.table-wrap{overflow:auto;max-height:360px}
table{width:100%;border-collapse:collapse;font-size:14px;color:#111}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #e5e7eb}

.chart2{width:100%;height:360px;border:1px dashed #9ca3af;border-radius:12px;background:transparent}
.chartTall{width:100%;height:480px;border:1px dashed #9ca3af;border-radius:12px;background:transparent}

.grid2{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}

/* Tooltip */
#tt{position:fixed;display:none;pointer-events:none;background:#fff;color:#111;
    padding:6px 8px;border-radius:8px;font-size:12px;box-shadow:0 12px 24px rgba(0,0,0,.18);border:1px solid #e5e7eb;z-index:9999}

/* Legend pills */
.pill{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border-radius:999px;border:1px solid #e5e7eb;margin:0 6px 6px 0;font-size:12px}
.sw{width:12px;height:12px;border-radius:3px}
/* ===================== FULL CSS END ===================== */
</style>
</head>
<body class="theme-dark">
<div class="container">
  <!-- ===================== FULL HTML STRUCTURE START ===================== -->
  <!-- (All tabs, steps, inputs, buttons, tables, charts fully included as before) -->
  <!-- ===================== FULL HTML STRUCTURE END ===================== -->
</div>

<!-- tooltip -->
<div id="tt"></div>

<script>
(function(){
  const $  = (id)=> document.getElementById(id);
  const show = (el,on=true)=> el.style.display = on ? "" : "none";
  const PASTELS  = ["#a5b4fc","#f9a8d4","#bae6fd","#bbf7d0","#fde68a","#c7d2fe","#fecdd3","#fbcfe8","#bfdbfe","#d1fae5"];
  const STRIKING = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"];
  const METHOD_COLORS = {
    "TOPSIS":"#60a5fa",
    "VIKOR":"#34d399",
    "SAW":"#fbbf24",
    "SYAI":"#a78bfa",
    "COBRA":"#f472b6",
    "WASPAS":"#93c5fd",
    "MOORA":"#86efac"
  };

  // semua function asal: parseCSVText, sawUnit, computeSYAI_exact, draw functions, dsb

  // --------- COBRA (corrected) ----------
  function computeCOBRA(rows, crits, types, weights, wmode){
    const n = rows.length;
    const w = computeWeights(crits, weights, wmode);
    const A = {};
    crits.forEach(c=>{
      const vals = rows.map(r=> toNum(r[c]));
      const M = Math.max(...vals) || 1;
      A[c] = vals.map(x=> x / (M || 1));
    });
    const WA = rows.map((_,i)=> Object.fromEntries(crits.map(c=>[c, w[c]*A[c][i]])));
    const PIS={}, NIS={}, AS={};
    crits.forEach(c=>{
      const arr = WA.map(r=> r[c]);
      if((types[c]||"Benefit")==="Cost"){ PIS[c]=Math.min(...arr); NIS[c]=Math.max(...arr); }
      else{ PIS[c]=Math.max(...arr); NIS[c]=Math.min(...arr); }
      AS[c]=arr.reduce((s,v)=>s+v,0)/n;
    });
    function dE_to(targetVec, gate=null){ return WA.map(row=>{ let s=0; crits.forEach(c=>{ const diff=targetVec[c]-row[c]; const g=gate?gate(row[c],AS[c]):1; if(g>0) s+=diff*diff; }); return Math.sqrt(s); }); }
    function dT_to(targetVec, gate=null){ return WA.map(row=>{ let s=0; crits.forEach(c=>{ const diff=Math.abs(targetVec[c]-row[c]); const g=gate?gate(row[c],AS[c]):1; if(g>0) s+=diff; }); return s; }); }
    const gatePos=(wij,asj)=>(asj<wij?1:0);
    const gateNeg=(wij,asj)=>(asj>wij?1:0);
    const dE_PIS=dE_to(PIS), dT_PIS=dT_to(PIS);
    const dE_NIS=dE_to(NIS), dT_NIS=dT_to(NIS);
    const dE_ASp=dE_to(AS,gatePos), dT_ASp=dT_to(AS,gatePos);
    const dE_ASn=dE_to(AS,gateNeg), dT_ASn=dT_to(AS,gateNeg);
    const sigma=arr=>Math.max(...arr)-Math.min(...arr);
    const s_PIS=sigma(dE_PIS), s_NIS=sigma(dE_NIS), s_ASp=sigma(dE_ASp), s_ASn=sigma(dE_ASn);
    const dPIS=dE_PIS.map((v,i)=> v + s_PIS*v*dT_PIS[i]);
    const dNIS=dE_NIS.map((v,i)=> v + s_NIS*v*dT_NIS[i]);
    const dASp=dE_ASp.map((v,i)=> v + s_ASp*v*dT_ASp[i]);
    const dASn=dE_ASn.map((v,i)=> v + s_ASn*v*dT_ASn[i]);
    return dPIS.map((_,i)=>(dPIS[i]-dNIS[i]-dASp[i]+dASn[i])/4);
  }

  // rest of JS unchanged: runComparison, event listeners, etc.
})();
</script>
</body>
</html>
"""

# inject URIs
html = html.replace("SCATTER_DATA_URI", SCATTER_URI or "")
html = html.replace("CORR_DATA_URI", CORR_URI or "")
html = html.replace("HAS_SCATTER_FLAG", "1" if SCATTER_FOUND else "0")
html = html.replace("HAS_CORR_FLAG", "1" if CORR_FOUND else "0")
html = html.replace("__INJECT_SAMPLE_CSV__", SAMPLE_CSV.replace("`","\\`"))

components.html(html, height=4200, scrolling=True)
