# app.py
import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SYAI-Rank", layout="wide")
APP_DIR = Path(__file__).resolve().parent

# ---------- Optional local images (kept) ----------
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
    # Fallback tiny demo
    return (
        "Alternative,Cost,Quality,Delivery\n"
        "A1,200,8,4\n"
        "A2,250,7,5\n"
        "A3,300,9,6\n"
        "A4,220,8,4\n"
        "A5,180,6,7\n"
    )

SAMPLE_CSV = load_sample_csv_text()

# ---------- base page background (kept) ----------
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
</style>
</head>
<body class="theme-dark">
<div class="container">
  <div class="header">
    <div class="title">SYAI-Rank</div>
    <div class="row">
      <a class="btn" id="downloadSample">⬇️ Download Sample</a>
      <button class="btn" id="loadSample">📄 Load Sample (Both Tabs)</button>
      <button class="toggle" id="themeToggle">🌙 Dark</button>
    </div>
  </div>

  <div class="tabs">
    <button type="button" class="tab active" id="tabSYAI">SYAI Method</button>
    <button type="button" class="tab" id="tabCompare">Comparison (TOPSIS, VIKOR, SAW, SYAI, COBRA, WASPAS, MOORA)</button>
  </div>

  <!-- ================= TAB 1: SYAI ONLY ================= -->
  <div id="viewSYAI">
    <div class="grid">
      <div>
        <div class="card dark">
          <div class="section-title">Step 1: Upload CSV</div>
          <label for="csv1" class="btn">📤 Choose CSV</label>
          <input id="csv1" type="file" accept=".csv" style="display:none"/>
          <p class="hint mt2">First column is <b>Alternative</b>. Others are criteria.</p>
        </div>

        <div id="t1" class="card dark" style="display:none">
          <div class="section-title">Step 2: Criteria Types</div>
          <div id="types1" class="grid2"></div>
        </div>

        <div id="w1" class="card dark" style="display:none">
          <div class="section-title">Step 3: Weights</div>
          <div class="row mb2" style="gap:16px">
            <label><input type="radio" name="wmode1" id="w1eq" checked> Equal (1/m)</label>
            <label><input type="radio" name="wmode1" id="w1c"> Custom (raw; normalized)</label>
          </div>
          <div id="wg1" class="grid2" style="display:none"></div>
        </div>

        <div id="b1" class="card dark" style="display:none">
          <div class="section-title">Step 4: β (blend of D⁺ and D⁻)</div>
          <input id="beta1" type="range" min="0" max="1" step="0.01" value="0.5" style="width:100%"/>
          <div class="hint mt2">β = <b id="beta1v">0.50</b></div>
          <button type="button" class="btn mt4" id="runSYAI">Run SYAI</button>
        </div>
      </div>

      <div>
        <div id="m1" class="card light" style="display:none">
          <div class="section-title">Decision Matrix (all rows)</div>
          <div class="table-wrap"><table id="tblm1"></table></div>
        </div>
        <div id="r1" class="card light" style="display:none">
          <div class="section-title">SYAI Results</div>
          <div class="table-wrap"><table id="tblr1"></table></div>
          <div class="mt6">
            <div class="hint mb2">Bar Chart (Closeness) — pastel bars, axes black (value on hover)</div>
            <div class="chart2"><svg id="bar1" width="100%" height="100%"></svg></div>
          </div>
          <div class="mt6">
            <div class="hint mb2">Line Chart (Rank vs Closeness)</div>
            <div class="chart2"><svg id="line1" width="100%" height="100%"></svg></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ================= TAB 2: COMPARISON ================= -->
  <div id="viewCompare" style="display:none">
    <div class="grid">
      <div>
        <div class="card dark">
          <div class="section-title">Step A: Upload CSV</div>
          <label for="csv2" class="btn">📤 Choose CSV</label>
          <input id="csv2" type="file" accept=".csv" style="display:none"/>
          <p class="hint mt2">First column is <b>Alternative</b>.</p>
        </div>

        <div id="t2" class="card dark" style="display:none">
          <div class="section-title">Step B: Criteria Types</div>
          <div id="types2" class="grid2"></div>
        </div>

        <div id="w2" class="card dark" style="display:none">
          <div class="section-title">Step C: Weights</div>
          <div class="row mb2" style="gap:16px">
            <label><input type="radio" name="wmode2" id="w2eq" checked> Equal (1/m)</label>
            <label><input type="radio" name="wmode2" id="w2c"> Custom (raw; normalized)</label>
          </div>
          <div id="wg2" class="grid2" style="display:none"></div>
        </div>

        <div class="card dark">
          <div class="section-title">Step D: Run</div>
          <button type="button" class="btn" id="runCmp">▶️ Run Comparison</button>
        </div>
      </div>

      <div>
        <div id="m2" class="card light" style="display:none">
          <div class="section-title">Decision Matrix (all rows)</div>
          <div class="table-wrap"><table id="tblm2"></table></div>
        </div>

        <div id="rcmp" class="card light" style="display:none">
          <div class="section-title">Scores & Ranks</div>
          <div class="table-wrap"><table id="mmc_table"></table></div>

          <div class="mt6">
            <div class="hint mb2">Grouped Bar — <b>method-colored</b> (axes black, hover values)</div>
            <div class="chart2"><svg id="mmc_bar" width="100%" height="100%"></svg></div>
            <div id="legend" class="mt2"></div>
          </div>

          <div class="mt6">
            <div class="hint">Scatter (striking color per alternative, Pearson line)</div>
            <div class="row" style="gap:12px;align-items:center">
              <div class="hint">X:</div>
              <select id="mmc_x"><option>SYAI</option><option>TOPSIS</option><option>VIKOR</option><option>SAW</option><option>COBRA</option><option>WASPAS</option><option>MOORA</option></select>
              <div class="hint">Y:</div>
              <select id="mmc_y"><option>TOPSIS</option><option>SYAI</option><option>VIKOR</option><option>SAW</option><option>COBRA</option><option>WASPAS</option><option>MOORA</option></select>
            </div>
            <div class="chart2"><svg id="mmc_sc" width="100%" height="100%"></svg></div>
          </div>

          <div class="mt6">
            <div class="hint mb2">Correlation Heatmap — <b>Spearman</b> (hot pink palette; legend on right; value on hover)</div>
            <div class="chartTall"><svg id="mmc_heat" width="100%" height="100%"></svg></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- tooltip -->
<div id="tt"></div>

<script>
(function(){
  const $  = (id)=> document.getElementById(id);
  const show = (el,on=true)=> el.style.display = on ? "" : "none";
  const PASTELS  = ["#a5b4fc","#f9a8d4","#bae6fd","#bbf7d0","#fde68a","#c7d2fe","#fecdd3","#fbcfe8","#bfdbfe","#d1fae5"]; // bars & dots
  const STRIKING = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"]; // scatter only

  // Fixed colors per METHOD (legend + bars)
  const METHOD_COLORS = {
    "TOPSIS":"#60a5fa",
    "VIKOR":"#34d399",
    "SAW":"#fbbf24",
    "SYAI":"#a78bfa",
    "COBRA":"#f472b6",
    "WASPAS":"#93c5fd",
    "MOORA":"#86efac"
  };

  // ---------- theme ----------
  let dark=true;
  function applyTheme(){
    document.body.classList.toggle('theme-dark', dark);
    document.body.classList.toggle('theme-light', !dark);
    $("themeToggle").textContent = dark ? "🌙 Dark" : "☀️ Light";
  }
  $("themeToggle").onclick = ()=>{ dark=!dark; applyTheme(); };
  applyTheme();

  // ---------- injected by Python ----------
  const SCATTER_URI = "SCATTER_DATA_URI";
  const CORR_URI    = "CORR_DATA_URI";
  const HAS_SCATTER = "HAS_SCATTER_FLAG" === "1";
  const HAS_CORR    = "HAS_CORR_FLAG" === "1";
  const SAMPLE_TEXT = `__INJECT_SAMPLE_CSV__`;  // single source for load + download

  // unify sample for both: the very same bytes for link & load
  $("downloadSample").href = "data:text/csv;charset=utf-8,"+encodeURIComponent(SAMPLE_TEXT);
  $("downloadSample").download = "sample.csv";
  $("loadSample").onclick = ()=>{ initSYAI(SAMPLE_TEXT); initCmp(SAMPLE_TEXT); };

  // ---------- tabs ----------
  function activateSYAI(e){ if(e){e.preventDefault(); e.stopPropagation();}
    $("tabSYAI").classList.add("active"); $("tabCompare").classList.remove("active");
    show($("viewSYAI"), true); show($("viewCompare"), false);
  }
  function activateCompare(e){ if(e){e.preventDefault(); e.stopPropagation();}
    $("tabCompare").classList.add("active"); $("tabSYAI").classList.remove("active");
    show($("viewSYAI"), false); show($("viewCompare"), true);
  }
  $("tabSYAI").addEventListener("click", activateSYAI);
  $("tabCompare").addEventListener("click", activateCompare);
  activateSYAI();

  // ---------- CSV helpers ----------
  function parseCSVText(text){
    const rows=[]; let i=0, cur="", inQ=false, row=[];
    const pushCell=()=>{ row.push(cur); cur=""; };
    const pushRow =()=>{ rows.push(row); row=[]; };
    while(i<text.length){
      const ch=text[i];
      if(inQ){
        if(ch==='\"'){ if(text[i+1]==='\"'){ cur+='\"'; i++; } else { inQ=false; } }
        else cur+=ch;
      }else{
        if(ch==='\"') inQ=true;
        else if(ch===',') pushCell();
        else if(ch==='\n'){ pushCell(); pushRow(); }
        else if(ch==='\r'){}
        else cur+=ch;
      }
      i++;
    }
    pushCell(); if(row.length>1 || row[0] !== "") pushRow();
    return rows;
  }
  const toNum=(v)=>{ const x=parseFloat(String(v).replace(/,/g,"")); return isFinite(x)?x:NaN; };
  const vectorNorm=(vals)=>{ const d=Math.sqrt(vals.reduce((s,v)=>s+(v*v),0))||1; return vals.map(v=>v/d); };

  // ---------- SAW utilities ----------
  function sawUnit(vals, type="Benefit", goal=null){
    const max=Math.max(...vals), min=Math.min(...vals);
    if(type==="Benefit"){
      const M = max || 1; return vals.map(x=> (x)/(M||1));
    }
    if(type==="Cost"){
      const m = min || 1; return vals.map(x=> (m)/(x||1));
    }
    // Ideal (Goal)
    const R=(max-min)||1;
    const g = isFinite(parseFloat(goal))? parseFloat(goal) : (min+max)/2;
    return vals.map(x=> Math.max(0, 1 - Math.abs(x-g)/R ));
  }

  // ================= TAB 1: SYAI =================
  let c1=[], r1=[], crit1=[], type1={}, ideal1={}, w1={}, wmode1='equal', beta1=0.5;
  $("beta1").oninput = ()=>{ beta1=parseFloat($("beta1").value); $("beta1v").textContent=beta1.toFixed(2); };
  $("w1eq").onchange = ()=>{ wmode1='equal'; $("wg1").style.display="none"; };
  $("w1c").onchange  = ()=>{ wmode1='custom'; $("wg1").style.display=""; };
  $("csv1").onchange = (e)=>{ const f=e.target.files[0]; if(!f) return; const r=new FileReader(); r.onload=()=>initSYAI(String(r.result)); r.readAsText(f); };

  function initSYAI(txt){
    const arr=parseCSVText(txt); if(!arr.length) return;
    c1 = arr[0].map(x=> String(x??"").trim());
    if(c1[0] !== "Alternative"){
      const idx = c1.indexOf("Alternative");
      if(idx>0){ const nm=c1.splice(idx,1)[0]; c1.unshift(nm); } else c1[0]="Alternative";
    }
    crit1 = c1.slice(1);
    r1 = arr.slice(1).filter(r=>r.length>=c1.length).map(r=>{ const o={}; c1.forEach((c,i)=> o[c]=r[i]); return o; });
    type1  = Object.fromEntries(crit1.map(c=>[c,"Benefit"]));
    ideal1 = Object.fromEntries(crit1.map(c=>[c,""]));
    w1     = Object.fromEntries(crit1.map(c=>[c,1]));
    renderMatrix("tblm1", c1, r1);
    renderTypes("types1", crit1, type1, ideal1);
    renderWeights("wg1", crit1, w1);
    show($("m1"),true); show($("t1"),true); show($("w1"),true); show($("b1"),true); show($("r1"),false);
  }

  $("runSYAI").onclick = ()=>{
    if(!r1.length) return;
    const res = computeSYAI_exact(r1, crit1, type1, ideal1, w1, wmode1, beta1)
                 .map(o=> ({Alternative:o.alt, Dp:o.Dp, Dm:o.Dm, Close:o.Close}));
    res.sort((a,b)=> b.Close-a.Close);
    res.forEach((r,i)=> r.Rank = i+1);

    const tb=$("tblr1"); tb.innerHTML="";
    const thead=document.createElement("thead"); thead.innerHTML="<tr><th>Alternative</th><th>D+</th><th>D-</th><th>Closeness</th><th>Rank</th></tr>"; tb.appendChild(thead);
    const tbody=document.createElement("tbody");
    res.forEach(r=>{
      const tr=document.createElement("tr");
      tr.innerHTML = `<td>${r.Alternative}</td><td>${r.Dp.toFixed(6)}</td><td>${r.Dm.toFixed(6)}</td><td>${r.Close.toFixed(6)}</td><td>${r.Rank}</td>`;
      tbody.appendChild(tr);
    });
    tb.appendChild(tbody);
    show($("r1"),true);

    drawSimpleBar("bar1", res.map(d=>({name:d.Alternative, value:d.Close})));
    drawSimpleLine("line1", res.map(d=>({rank:d.Rank, value:d.Close, name:d.Alternative})));
  };

  // ================= TAB 2: COMPARISON =================
  let c2=[], r2=[], crit2=[], type2={}, ideal2={}, w2={}, wmode2='equal';
  $("w2eq").onchange = ()=>{ wmode2='equal'; $("wg2").style.display="none"; };
  $("w2c").onchange  = ()=>{ wmode2='custom'; $("wg2").style.display=""; };
  $("csv2").onchange = (e)=>{ const f=e.target.files[0]; if(!f) return; const r=new FileReader(); r.onload=()=>initCmp(String(r.result)); r.readAsText(f); };

  function initCmp(txt){
    const arr=parseCSVText(txt); if(!arr.length) return;
    c2 = arr[0].map(x=> String(x??"").trim());
    if(c2[0] !== "Alternative"){
      const idx=c2.indexOf("Alternative");
      if(idx>0){ const nm=c2.splice(idx,1)[0]; c2.unshift(nm); } else c2[0]="Alternative";
    }
    crit2 = c2.slice(1);
    r2 = arr.slice(1).filter(r=>r.length>=c2.length).map(r=>{ const o={}; c2.forEach((c,i)=> o[c]=r[i]); return o; });
    type2  = Object.fromEntries(crit2.map(c=>[c,"Benefit"]));
    ideal2 = Object.fromEntries(crit2.map(c=>[c,""]));
    w2     = Object.fromEntries(crit2.map(c=>[c,1]));
    renderMatrix("tblm2", c2, r2);
    renderTypes("types2", crit2, type2, ideal2);
    renderWeights("wg2", crit2, w2);
    show($("m2"),true); show($("t2"),true); show($("w2"),true); show($("rcmp"),false);
  }

  // ---------- renderers ----------
  function renderMatrix(tid, cols, rows){
    const tb=$(tid); tb.innerHTML="";
    const thead=document.createElement("thead"); const trh=document.createElement("tr");
    cols.forEach(c=>{ const th=document.createElement("th"); th.textContent=c; trh.appendChild(th); });
    thead.appendChild(trh); tb.appendChild(thead);
    const tbody=document.createElement("tbody");
    rows.forEach(r=>{
      const tr=document.createElement("tr");
      cols.forEach(c=>{ const td=document.createElement("td"); td.textContent=String(r[c]??""); tr.appendChild(td); });
      tbody.appendChild(tr);
    });
    tb.appendChild(tbody);
  }

  function renderTypes(id, crits, types, ideals){
    const wrap=$(id); wrap.innerHTML="";
    crits.forEach(c=>{
      const box=document.createElement("div");
      const lab=document.createElement("div"); lab.className="label"; lab.textContent=c; box.appendChild(lab);
      const sel=document.createElement("select");
      ["Benefit","Cost","Ideal (Goal)"].forEach(v=>{
        const o=document.createElement("option"); o.textContent=v; sel.appendChild(o);
      });
      sel.value = types[c]||"Benefit";
      sel.onchange = ()=>{
        types[c]=sel.value;
        renderTypes(id,crits,types,ideals);
      };
      box.appendChild(sel);

      if((types[c]||"")==="Ideal (Goal)"){
        const inp=document.createElement("input"); inp.className="mt2"; inp.type="number"; inp.step="any"; inp.placeholder="Goal";
        inp.value=ideals[c]||""; inp.oninput=()=> ideals[c]=inp.value;
        box.appendChild(inp);
      } else {
        delete ideals[c];
      }
      wrap.appendChild(box);
    });
  }

  function renderWeights(id, crits, weights){
    const wrap=$(id); wrap.innerHTML="";
    crits.forEach(c=>{
      const box=document.createElement("div");
      const lab=document.createElement("div"); lab.className="label"; lab.textContent="w("+c+")"; box.appendChild(lab);
      const inp=document.createElement("input"); inp.type="number"; inp.step="0.001"; inp.min="0"; inp.value=weights[c]??0;
      inp.oninput=()=> weights[c]=inp.value; box.appendChild(inp);
      wrap.appendChild(box);
    });
  }

  // ---------- CORE compute ----------
  function computeWeights(crits, weights, mode){
    const w={};
    if(mode==='equal'){ crits.forEach(c=> w[c]=1/crits.length); }
    else{
      let s=0; crits.forEach(c=>{ const v=Math.max(0,parseFloat(weights[c]||0)); w[c]=isFinite(v)?v:0; s+=w[c]; });
      if(s<=0) crits.forEach(c=> w[c]=1/crits.length); else crits.forEach(c=> w[c]/=s);
    }
    return w;
  }

  function computeU(rows, crits, types, ideals){
    const U={};
    crits.forEach(c=>{
      const vals = rows.map(r=> toNum(r[c]));
      U[c] = sawUnit(vals, types[c]||"Benefit", ideals[c]);
    });
    return U;
  }

  // --------- SYAI (exact, per your working routine) ----------
  function normalizeColumn_SYAI(vals, ctype, goal){
    const max=Math.max(...vals), min=Math.min(...vals), R=max-min;
    let xStar;
    if(ctype==="Benefit") xStar=max;
    else if(ctype==="Cost") xStar=min;
    else {
      const g=parseFloat(goal);
      xStar = isFinite(g) ? g : (vals.reduce((s,v)=>s+(isFinite(v)?v:0),0)/vals.length);
    }
    if(Math.abs(R)<1e-12) return vals.map(_=>1.0);
    return vals.map(x=> Math.max(0.01, Math.min(1, 0.01 + (1-0.01)*(1-Math.abs(x-xStar)/R))));
  }

  function computeSYAI_exact(rows, crits, types, ideals, weights, wmode, beta){
    const N={};
    crits.forEach(c=>{
      const series = rows.map(r=> toNum(r[c]));
      N[c] = normalizeColumn_SYAI(series, types[c]||"Benefit", ideals[c]);
    });
    const w = computeWeights(crits, weights, wmode);
    const W = rows.map((_,i)=> Object.fromEntries(crits.map(c=>[c,N[c][i]*w[c]])) );

    const Aplus={}, Aminus={};
    crits.forEach(c=>{
      let mx=-Infinity, mn=Infinity;
      W.forEach(row=>{ if(row[c]>mx) mx=row[c]; if(row[c]<mn) mn=row[c]; });
      Aplus[c]=mx; Aminus[c]=mn;
    });

    return rows.map((r,i)=>{
      let Dp=0, Dm=0;
      crits.forEach(c=>{ Dp+=Math.abs(W[i][c]-Aplus[c]); Dm+=Math.abs(W[i][c]-Aminus[c]); });
      const denom = beta*Dp + (1-beta)*Dm || Number.EPSILON;
      const Close = ((1-beta)*Dm)/denom;
      return { alt:String(r["Alternative"]), Dp, Dm, Close };
    });
  }

  // --------- COBRA (per Sec. 2.2, Eqs. 6–26) ----------
function computeCOBRA(rows, crits, types, weights, wmode){
  const n = rows.length;
  const w = computeWeights(crits, weights, wmode);

  // Step 2 (Eq. 7): normalize by column max (for ALL criteria)
  const F = {}; // f_ij
  crits.forEach(c=>{
    const vals = rows.map(r=> toNum(r[c]));
    const maxv = Math.max(...vals) || 1;
    F[c] = vals.map(x => x / (maxv || 1));
  });

  // Step 3 (Eq. 8): weighted normalized matrix, r_ij = f_ij * w_j
  const Rw = rows.map((_,i)=> Object.fromEntries(crits.map(c=>[c, F[c][i] * w[c]])));

  // Step 4 (Eqs. 9–12): NIS, PIS per criterion; AS (Eq. 13)
  const PIS = {}, NIS = {}, AS = {};
  crits.forEach(c=>{
    const col = Rw.map(r => r[c]);
    if ((types[c] || "Benefit") === "Cost"){ // non-beneficial
      PIS[c] = Math.min(...col);
      NIS[c] = Math.max(...col);
    } else { // beneficial
      PIS[c] = Math.max(...col);
      NIS[c] = Math.min(...col);
    }
    AS[c] = col.reduce((s,v)=>s+v,0) / n;
  });

  // Helpers: Euclidean and Taxicab distances with optional ε gates
  function dE_to(target, gate=null){
    return Rw.map(row=>{
      let s = 0;
      crits.forEach(c=>{
        const use = gate ? gate(row[c], AS[c]) : 1;
        if (use>0){
          const d = target[c] - row[c];
          s += d*d;
        }
      });
      return Math.sqrt(s);
    });
  }
  function dT_to(target, gate=null){
    return Rw.map(row=>{
      let s = 0;
      crits.forEach(c=>{
        const use = gate ? gate(row[c], AS[c]) : 1;
        if (use>0) s += Math.abs(target[c] - row[c]);
      });
      return s;
    });
  }

  // Step 5: ε⁺ and ε⁻ (Eqs. 21, 24) — strict inequalities per paper
  const gatePos = (wij, asj)=> (asj < wij ? 1 : 0); // ε⁺=1 if AS_j < r_ij
  const gateNeg = (wij, asj)=> (asj > wij ? 1 : 0); // ε⁻=1 if AS_j > r_ij

  // Distances (Eqs. 16–23)
  const dE_PIS = dE_to(PIS),         dT_PIS = dT_to(PIS);
  const dE_NIS = dE_to(NIS),         dT_NIS = dT_to(NIS);
  const dE_ASp = dE_to(AS, gatePos), dT_ASp = dT_to(AS, gatePos);
  const dE_ASn = dE_to(AS, gateNeg), dT_ASn = dT_to(AS, gateNeg);

  // ρ (Eq. 14): max dE(S_j) − min dE(S_j) for each solution S
  const rho = arr => Math.max(...arr) - Math.min(...arr);
  const ρ_PIS = rho(dE_PIS);
  const ρ_NIS = rho(dE_NIS);
  const ρ_ASp = rho(dE_ASp);
  const ρ_ASn = rho(dE_ASn);

  // d(S_j) (Eq. 14): d = dE + ρ · dT   (no extra factor of dE)
  const D_PIS = dE_PIS.map((v,i)=> v + ρ_PIS * dT_PIS[i]);
  const D_NIS = dE_NIS.map((v,i)=> v + ρ_NIS * dT_NIS[i]);
  const D_ASp = dE_ASp.map((v,i)=> v + ρ_ASp * dT_ASp[i]);
  const D_ASn = dE_ASn.map((v,i)=> v + ρ_ASn * dT_ASn[i]);

  // Step 6 (Eq. 26): final comprehensive distances (smaller is better; can be negative)
  const dC = D_PIS.map((_,i)=> ( D_PIS[i] - D_NIS[i] - D_ASp[i] + D_ASn[i] ) / 4 );

  return dC;
}

  function runComparison(){
    if(!r2.length) return;

    const U = computeU(r2, crit2, type2, ideal2);
    const w = computeWeights(crit2, w2, wmode2);

    // ---------- SAW ----------
    const SAW = r2.map((_,i)=> crit2.reduce((s,c)=> s + w[c]*U[c][i], 0));

    // ---------- WASPAS ----------
    const WPM = r2.map((_,i)=> crit2.reduce((p,c)=> p * Math.pow(Math.max(U[c][i],1e-12), w[c]), 1));
    const WASPAS = r2.map((_,i)=> 0.5*SAW[i] + 0.5*WPM[i]);

    // ---------- MOORA ----------
    const NV={}; crit2.forEach(c=>{
      const vals = r2.map(r=> toNum(r[c]));
      NV[c] = ( (type2[c]||"Benefit")==="Ideal (Goal)") ? U[c] : vectorNorm(vals);
    });
    const MOORA = r2.map((_,i)=>{
      let sumB=0, sumC=0;
      crit2.forEach(c=>{
        if((type2[c]||"Benefit")==="Cost") sumC += w[c]*NV[c][i];
        else sumB += w[c]*NV[c][i];
      });
      return sumB - sumC;
    });

    // ---------- TOPSIS ----------
    const Nt={}; crit2.forEach(c=>{ Nt[c]=vectorNorm(r2.map(r=> toNum(r[c]))); });
    const Wt = r2.map((_,i)=> Object.fromEntries(crit2.map(c=>[c, Nt[c][i]*w[c]])) );
    const Aplus={}, Aminus={}; crit2.forEach(c=>{
      const arr=Wt.map(r=>r[c]);
      if((type2[c]||"Benefit")==="Cost"){ Aplus[c]=Math.min(...arr); Aminus[c]=Math.max(...arr); }
      else { Aplus[c]=Math.max(...arr); Aminus[c]=Math.min(...arr); }
    });
    const TOPSIS = r2.map((_,i)=>{
      let dp=0, dm=0;
      crit2.forEach(c=>{ const v=Wt[i][c]; dp+=(v-Aplus[c])**2; dm+=(v-Aminus[c])**2; });
      dp=Math.sqrt(dp); dm=Math.sqrt(dm);
      return dm/((dp+dm)||1e-12);
    });

    // ---------- VIKOR (lower better) ----------
    const fStar={}, fMin={}; crit2.forEach(c=>{
      const vals=r2.map(r=> toNum(r[c]));
      if((type2[c]||"Benefit")==="Cost"){ fStar[c]=Math.min(...vals); fMin[c]=Math.max(...vals); }
      else { fStar[c]=Math.max(...vals); fMin[c]=Math.min(...vals); }
    });
    const S = r2.map(r=> crit2.reduce((s,c)=>{
      const denom = Math.abs(fStar[c]-fMin[c])||1;
      const term = ((type2[c]||"Benefit")==="Cost") ? ((toNum(r[c])-fStar[c])/((fMin[c]-fStar[c])||1))
                                                    : ((fStar[c]-toNum(r[c]))/denom);
      return s + w[c]*term;
    },0));
    const R = r2.map(r=> Math.max(...crit2.map(c=>{
      const denom = Math.abs(fStar[c]-fMin[c])||1;
      const term = ((type2[c]||"Benefit")==="Cost") ? ((toNum(r[c])-fStar[c])/((fMin[c]-fStar[c])||1))
                                                    : ((fStar[c]-toNum(r[c]))/denom);
      return w[c]*term;
    })));
    const Smin=Math.min(...S), Smax=Math.max(...S), Rmin=Math.min(...R), Rmax=Math.max(...R);
    const VIKOR = S.map((_,i)=> 0.5*((S[i]-Smin)/((Smax-Smin)||1)) + 0.5*((R[i]-Rmin)/((Rmax-Rmin)||1)));

    // ---------- SYAI (exact) ----------
    const sy = computeSYAI_exact(r2, crit2, type2, ideal2, w2, wmode2, 0.5);
    const SYAI = sy.map(o=> o.Close);

    // ---------- COBRA (per paper; can be negative) ----------
    const COBRA = computeCOBRA(r2, crit2, type2, w2, wmode2);

    // ranks
    function ranksHigher(a){ const idx=a.map((v,i)=>({v,i})).sort((x,y)=> y.v-x.v); const rk=new Array(a.length); idx.forEach((o,k)=> rk[o.i]=k+1); return rk; }
    function ranksLower(a){ const idx=a.map((v,i)=>({v,i})).sort((x,y)=> x.v-y.v); const rk=new Array(a.length); idx.forEach((o,k)=> rk[o.i]=k+1); return rk; }

    const methods={TOPSIS, VIKOR, SAW, SYAI, COBRA, WASPAS, MOORA};
    const ranks={ TOPSIS:ranksHigher(TOPSIS), VIKOR:ranksLower(VIKOR), SAW:ranksHigher(SAW),
                  SYAI:ranksHigher(SYAI), COBRA:ranksLower(COBRA), WASPAS:ranksHigher(WASPAS), MOORA:ranksHigher(MOORA) };

    const order=["TOPSIS","VIKOR","SAW","SYAI","COBRA","WASPAS","MOORA"];

    // table
    const tb=$("mmc_table"); tb.innerHTML="";
    const thead=document.createElement("thead"); const trh=document.createElement("tr");
    ["Alternative"].concat(order).forEach(h=>{ const th=document.createElement("th"); th.textContent=h; trh.appendChild(th); });
    thead.appendChild(trh); tb.appendChild(thead);
    const tbody=document.createElement("tbody");
    r2.forEach((row,i)=>{
      const tr=document.createElement("tr");
      const t0=document.createElement("td"); t0.textContent=String(row["Alternative"]); tr.appendChild(t0);
      order.forEach(m=>{
        const td=document.createElement("td"); td.textContent = methods[m][i].toFixed(4)+" ("+ranks[m][i]+")"; tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    tb.appendChild(tbody);
    show($("rcmp"),true);

    // charts
    drawCmpBars(methods, ranks, r2.map(r=> String(r["Alternative"])));
    drawCmpScatter({methods, names:r2.map(r=> String(r["Alternative"]))}, $("mmc_x").value, $("mmc_y").value);
    drawHeatSpearman({methods});
  }

  // ---------- Tooltip ----------
  const TT = $("tt");
  function showTT(x,y,html){ TT.style.display="block"; TT.style.left=(x+12)+"px"; TT.style.top=(y+12)+"px"; TT.innerHTML=html; }
  function hideTT(){ TT.style.display="none"; }

  // ---------- Charts ----------
  function drawSimpleBar(svgId, data){
    const svg=$(svgId); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const W=(svg.getBoundingClientRect().width||800), H=(svg.getBoundingClientRect().height||360);
    svg.setAttribute("viewBox","0 0 "+W+" "+H);
    const padL=50,padR=20,padT=18,padB=44;
    const max=Math.max(...data.map(d=>d.value))||1;
    const cell=(W-padL-padR)/data.length, barW=cell*0.8;

    const yAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    yAxis.setAttribute("x1",padL); yAxis.setAttribute("x2",padL); yAxis.setAttribute("y1",padT); yAxis.setAttribute("y2",H-padB); yAxis.setAttribute("stroke","#000"); svg.appendChild(yAxis);
    const xAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    xAxis.setAttribute("x1",padL); xAxis.setAttribute("x2",W-padR); xAxis.setAttribute("y1",H-padB); xAxis.setAttribute("y2",H-padB); xAxis.setAttribute("stroke","#000"); svg.appendChild(xAxis);

    for(let t=0;t<=5;t++){
      const val=max*t/5, y=H-padB-(H-padT-padB)*(val/max);
      const gl=document.createElementNS("http://www.w3.org/2000/svg","line");
      gl.setAttribute("x1",padL); gl.setAttribute("x2",W-padR); gl.setAttribute("y1",y); gl.setAttribute("y2",y);
      gl.setAttribute("stroke","#000"); gl.setAttribute("stroke-dasharray","3 3"); svg.appendChild(gl);
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x",padL-10); tx.setAttribute("y",y+4); tx.setAttribute("text-anchor","end");
      tx.setAttribute("font-size","12"); tx.setAttribute("fill","#000"); tx.textContent=val.toFixed(2); svg.appendChild(tx);
    }

    data.forEach((d,i)=>{
      const x=padL+i*cell+(cell-barW)/2, h=(H-padT-padB)*(d.value/max), y=H-padB-h;
      const r=document.createElementNS("http://www.w3.org/2000/svg","rect");
      r.setAttribute("x",x); r.setAttribute("y",y); r.setAttribute("width",barW); r.setAttribute("height",h);
      r.setAttribute("fill", PASTELS[i%PASTELS.length]);
      r.addEventListener("mousemove",(ev)=> showTT(ev.clientX, ev.clientY, `<b>${d.name}</b><br/>${d.value.toFixed(6)}`));
      r.addEventListener("mouseleave", hideTT);
      svg.appendChild(r);

      const lbl=document.createElementNS("http://www.w3.org/2000/svg","text");
      lbl.setAttribute("x",x+barW/2); lbl.setAttribute("y",H-12); lbl.setAttribute("text-anchor","middle");
      lbl.setAttribute("font-size","12"); lbl.setAttribute("fill","#000"); lbl.textContent=d.name; svg.appendChild(lbl);
    });
  }

  function drawSimpleLine(svgId, data){
    const svg=$(svgId); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const W=(svg.getBoundingClientRect().width||800), H=(svg.getBoundingClientRect().height||300);
    svg.setAttribute("viewBox","0 0 "+W+" "+H);
    const padL=50,padR=20,padT=14,padB=30;
    const maxY=Math.max(...data.map(d=>d.value))||1, minX=1, maxX=Math.max(...data.map(d=>d.rank))||1;
    const sx=(r)=> padL+(W-padL-padR)*((r-minX)/(maxX-minX||1));
    const sy=(v)=> H-padB-(H-padT-padB)*(v/maxY);

    const yAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    yAxis.setAttribute("x1",padL); yAxis.setAttribute("x2",padL); yAxis.setAttribute("y1",padT); yAxis.setAttribute("y2",H-padB); yAxis.setAttribute("stroke","#000"); svg.appendChild(yAxis);
    const xAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    xAxis.setAttribute("x1",padL); xAxis.setAttribute("x2",W-padR); xAxis.setAttribute("y1",H-padB); xAxis.setAttribute("y2",H-padB); xAxis.setAttribute("stroke","#000"); svg.appendChild(xAxis);

    const p=document.createElementNS("http://www.w3.org/2000/svg","path");
    let dstr="";
    data.sort((a,b)=> a.rank-b.rank).forEach((pt,i)=>{
      const x=sx(pt.rank), y=sy(pt.value);
      dstr += (i===0? "M":"L")+x+" "+y+" ";
      const c=document.createElementNS("http://www.w3.org/2000/svg","circle");
      c.setAttribute("cx",x); c.setAttribute("cy",y); c.setAttribute("r","4"); c.setAttribute("fill","#64748b");
      c.addEventListener("mousemove",(ev)=> showTT(ev.clientX, ev.clientY, `<b>Rank ${pt.rank}</b><br/>${pt.value.toFixed(6)}`));
      c.addEventListener("mouseleave", hideTT);
      svg.appendChild(c);
    });
    p.setAttribute("d", dstr.trim()); p.setAttribute("fill","none"); p.setAttribute("stroke","#64748b"); p.setAttribute("stroke-width","2");
    svg.appendChild(p);
  }

  function drawCmpBars(methods, ranks, names){
    const svg=$("mmc_bar"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const W=(svg.getBoundingClientRect().width||900), H=(svg.getBoundingClientRect().height||360);
    svg.setAttribute("viewBox","0 0 "+W+" "+H);
    const padL=70,padR=20,padT=20,padB=66;
    const order=["TOPSIS","VIKOR","SAW","SYAI","COBRA","WASPAS","MOORA"];
    const vals = names.map((nm,i)=> order.map(m=> methods[m][i]));
    const max = Math.max(...vals.flat()), min = Math.min(...vals.flat());
    const yMin=Math.min(min,0), yMax=Math.max(max,0), range=(yMax-yMin)||1;

    const yAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    yAxis.setAttribute("x1",padL); yAxis.setAttribute("x2",padL); yAxis.setAttribute("y1",padT); yAxis.setAttribute("y2",H-padB); yAxis.setAttribute("stroke","#000"); svg.appendChild(yAxis);
    const xAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    xAxis.setAttribute("x1",padL); xAxis.setAttribute("x2",W-padR); xAxis.setAttribute("y1",H-padB); xAxis.setAttribute("y2",H-padB); xAxis.setAttribute("stroke","#000"); svg.appendChild(xAxis);

    for(let t=0;t<=5;t++){
      const val=yMin + range*t/5;
      const y=H-padB - (H-padT-padB)*((val-yMin)/range);
      const gl=document.createElementNS("http://www.w3.org/2000/svg","line");
      gl.setAttribute("x1",padL); gl.setAttribute("x2",W-padR); gl.setAttribute("y1",y); gl.setAttribute("y2",y);
      gl.setAttribute("stroke","#000"); gl.setAttribute("stroke-dasharray","3 3"); svg.appendChild(gl);
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x",padL-10); tx.setAttribute("y",y+4); tx.setAttribute("text-anchor","end");
      tx.setAttribute("font-size","12"); tx.setAttribute("fill","#000"); tx.textContent=val.toFixed(2); svg.appendChild(tx);
    }

    const cell=(W-padL-padR)/names.length;
    const gap=4; // small indent between method groups
    const barW=((cell*0.8)-(order.length-1)*gap)/order.length;

    names.forEach((nm,i)=>{
      const x0=padL + i*cell + (cell - (barW*order.length + gap*(order.length-1)))/2;
      const lbl=document.createElementNS("http://www.w3.org/2000/svg","text");
      lbl.setAttribute("x",x0 + (barW*order.length + gap*(order.length-1))/2); lbl.setAttribute("y",H-8);
      lbl.setAttribute("text-anchor","middle"); lbl.setAttribute("font-size","12"); lbl.setAttribute("fill","#000"); lbl.textContent=nm; svg.appendChild(lbl);
      order.forEach((m,k)=>{
        const v=methods[m][i];
        const y=H-padB - (H-padT-padB)*((v-yMin)/range);
        const h=H-padB - y;
        const rect=document.createElementNS("http://www.w3.org/2000/svg","rect");
        rect.setAttribute("x",x0 + k*(barW+gap)); rect.setAttribute("y",h>=0? y : H-padB);
        rect.setAttribute("width",barW); rect.setAttribute("height",Math.abs(h));
        rect.setAttribute("fill", METHOD_COLORS[m] || PASTELS[k%PASTELS.length]);
        rect.addEventListener("mousemove",(ev)=> showTT(ev.clientX, ev.clientY, `<b>${m}</b> • ${nm}<br/>${v.toFixed(6)}`));
        rect.addEventListener("mouseleave", hideTT);
        svg.appendChild(rect);
      });
    });

    // Legend (method → color)
    const leg = $("legend"); leg.innerHTML="";
    order.forEach(m=>{
      const pill = document.createElement("span"); pill.className="pill";
      const sw = document.createElement("span"); sw.className="sw"; sw.style.background = METHOD_COLORS[m] || "#bbb";
      const txt = document.createElement("span"); txt.textContent = m;
      pill.appendChild(sw); pill.appendChild(txt);
      leg.appendChild(pill);
    });
  }

  // Scatter (STRIKING per alternative)
  function drawCmpScatter(res, mx, my){
    const svg=$("mmc_sc"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const W=(svg.getBoundingClientRect().width||900), H=(svg.getBoundingClientRect().height||360);
    svg.setAttribute("viewBox","0 0 "+W+" "+H);
    const padL=60,padR=20,padT=20,padB=50;
    const xs=res.methods[mx], ys=res.methods[my];
    const Xmin=Math.min(...xs), Xmax=Math.max(...xs), Ymin=Math.min(...ys), Ymax=Math.max(...ys);
    const sx=(x)=> padL + (W-padL-padR)*((x-Xmin)/((Xmax-Xmin)||1));
    const sy=(y)=> H-padB - (H-padT-padB)*((y-Ymin)/((Ymax-Ymin)||1));

    const ax=document.createElementNS("http://www.w3.org/2000/svg","line");
    ax.setAttribute("x1",padL); ax.setAttribute("x2",padL); ax.setAttribute("y1",padT); ax.setAttribute("y2",H-padB); ax.setAttribute("stroke","#000"); svg.appendChild(ax);
    const ay=document.createElementNS("http://www.w3.org/2000/svg","line");
    ay.setAttribute("x1",padL); ay.setAttribute("x2",W-padR); ay.setAttribute("y1",H-padB); ay.setAttribute("y2",H-padB); ay.setAttribute("stroke","#000"); svg.appendChild(ay);

    res.names.forEach((nm,i)=>{
      const c=document.createElementNS("http://www.w3.org/2000/svg","circle");
      c.setAttribute("cx",sx(xs[i])); c.setAttribute("cy",sy(ys[i])); c.setAttribute("r","5");
      c.setAttribute("fill", STRIKING[i % STRIKING.length]);
      c.addEventListener("mousemove",(ev)=> showTT(ev.clientX, ev.clientY, `<b>${nm}</b><br/>${mx}: ${xs[i].toFixed(6)}<br/>${my}: ${ys[i].toFixed(6)}`));
      c.addEventListener("mouseleave", hideTT);
      svg.appendChild(c);
    });

    const mean=(a)=> a.reduce((s,v)=>s+v,0)/a.length;
    const mxv=mean(xs), myv=mean(ys);
    let num=0, dx=0, dy=0;
    for(let i=0;i<xs.length;i++){ const a=xs[i]-mxv, b=ys[i]-myv; num+=a*b; dx+=a*a; dy+=b*b; }
    const r = num/Math.sqrt((dx||1)*(dy||1));
    const b = num/(dx||1), a = myv - b*mxv;
    const line=document.createElementNS("http://www.w3.org/2000/svg","line");
    line.setAttribute("x1",padL); line.setAttribute("y1",sy(a+b*Xmin));
    line.setAttribute("x2",W-padR); line.setAttribute("y2",sy(a+b*Xmax));
    line.setAttribute("stroke","#000"); line.setAttribute("stroke-width","2"); svg.appendChild(line);
    const cap=document.createElementNS("http://www.w3.org/2000/svg","text");
    cap.setAttribute("x",(padL+W-padR)/2); cap.setAttribute("y",padT+14); cap.setAttribute("text-anchor","middle");
    cap.setAttribute("font-size","12"); cap.setAttribute("fill","#000"); cap.textContent="Pearson r = "+r.toFixed(3); svg.appendChild(cap);
  }

  // Spearman heatmap — HOT PINK palette + legend + hover
  function drawHeatSpearman(res){
    const methods=["TOPSIS","VIKOR","SAW","SYAI","COBRA","WASPAS","MOORA"];
    const svg=$("mmc_heat"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const W=(svg.getBoundingClientRect().width||900), H=(svg.getBoundingClientRect().height||480);
    svg.setAttribute("viewBox","0 0 "+W+" "+H);
    const padL=120, padR=60, padT=60, padB=80;
    const n=methods.length;

    function rankArray(a){
      const idx=a.map((v,i)=>({v,i})).sort((x,y)=> x.v-y.v);
      const r=new Array(a.length); let i=0;
      while(i<idx.length){
        let j=i; while(j+1<idx.length && idx[j+1].v===idx[i].v) j++;
        const avg=(i+j)/2 + 1; for(let k=i;k<=j;k++) r[idx[k].i]=avg; i=j+1;
      }
      return r;
    }
    function pearson(x,y){
      const n=x.length; const mx=x.reduce((s,v)=>s+v,0)/n, my=y.reduce((s,v)=>s+v,0)/n;
      let num=0, dx=0, dy=0; for(let i=0;i<n;i++){ const a=x[i]-mx, b=y[i]-my; num+=a*b; dx+=a*a; dy+=b*b; }
      return num/Math.sqrt((dx||1)*(dy||1));
    }

    const data = methods.map(m=> res.methods[m]);
    const ranks = data.map(arr=> rankArray(arr));
    const R = methods.map((_,i)=> methods.map((_,j)=> pearson(ranks[i], ranks[j])));

    function colorFor(v){ // v in [-1,1]
      const t = (v+1)/2; // 0..1
      const c0 = {r:255,g:233,b:242}; // #ffe9f2 very light pink
      const c1 = {r:236,g: 72,b:153}; // #ec4899 hot pink
      const r = Math.round(c0.r + (c1.r-c0.r)*t);
      const g = Math.round(c0.g + (c1.g-c0.g)*t);
      const b = Math.round(c0.b + (c1.b-c0.b)*t);
      return "rgb("+r+","+g+","+b+")";
    }

    const cellW=(W-padL-padR)/n, cellH=(H-padT-padB)/n;

    // axis labels
    for(let i=0;i<n;i++){
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x", padL + i*cellW + cellW/2); tx.setAttribute("y", padT-12);
      tx.setAttribute("transform","rotate(-45 "+(padL + i*cellW + cellW/2)+" "+(padT-12)+")");
      tx.setAttribute("text-anchor","end"); tx.setAttribute("font-size","12"); tx.setAttribute("fill","#000"); tx.textContent=methods[i]; svg.appendChild(tx);
      const ty=document.createElementNS("http://www.w3.org/2000/svg","text");
      ty.setAttribute("x", padL-10); ty.setAttribute("y", padT + i*cellH + cellH/2 + 4);
      ty.setAttribute("text-anchor","end"); ty.setAttribute("font-size","12"); ty.setAttribute("fill","#000"); ty.textContent=methods[i]; svg.appendChild(ty);
    }

    // cells with hover values
    for(let i=0;i<n;i++){
      for(let j=0;j<n;j++){
        const val = R[i][j];
        const x=padL + j*cellW, y=padT + i*cellH;
        const rect=document.createElementNS("http://www.w3.org/2000/svg","rect");
        rect.setAttribute("x",x); rect.setAttribute("y",y); rect.setAttribute("width",cellW-1); rect.setAttribute("height",cellH-1);
        rect.setAttribute("fill", colorFor(val)); rect.setAttribute("stroke","#ffffff"); rect.setAttribute("stroke-width","0.5");
        rect.addEventListener("mousemove",(ev)=> showTT(ev.clientX, ev.clientY, `<b>${methods[i]}</b> vs <b>${methods[j]}</b><br/>ρ = ${val.toFixed(3)}`));
        rect.addEventListener("mouseleave", hideTT);
        svg.appendChild(rect);
      }
    }

    // legend on right
    const Lx = padL + (cellW*n) + 20, Ly = padT, Lw = 16, Lh = cellH*n;
    const steps = 60;
    for(let s=0;s<steps;s++){
      const t = s/(steps-1);
      const val = -1 + 2*t;
      const rr=document.createElementNS("http://www.w3.org/2000/svg","rect");
      rr.setAttribute("x",Lx); rr.setAttribute("y", Ly + (1-t)*Lh);
      rr.setAttribute("width",Lw); rr.setAttribute("height", Lh/steps + 1);
      rr.setAttribute("fill", colorFor(val)); svg.appendChild(rr);
    }
    const frame=document.createElementNS("http://www.w3.org/2000/svg","rect");
    frame.setAttribute("x",Lx); frame.setAttribute("y",Ly); frame.setAttribute("width",Lw); frame.setAttribute("height",Lh);
    frame.setAttribute("fill","none"); frame.setAttribute("stroke","#000"); frame.setAttribute("stroke-width","0.8"); svg.appendChild(frame);
    [-1,-0.5,0,0.5,1].forEach(v=>{
      const y = Ly + (1-(v+1)/2)*Lh;
      const t=document.createElementNS("http://www.w3.org/2000/svg","text");
      t.setAttribute("x", Lx + Lw + 6); t.setAttribute("y", y+4); t.setAttribute("font-size","12"); t.setAttribute("fill","#000");
      t.textContent = v.toFixed(1); svg.appendChild(t);
    });
    const lh=document.createElementNS("http://www.w3.org/200/svg","text");
    lh.setAttribute("x", Lx-2); lh.setAttribute("y", Ly-10); lh.setAttribute("text-anchor","end");
    lh.setAttribute("font-size","12"); lh.setAttribute("fill","#000"); lh.textContent="Spearman ρ (hot pink)"; svg.appendChild(lh);
  }

  // ---------- events ----------
  $("runCmp").onclick = ()=> runComparison();
  $("mmc_x").onchange = ()=> runComparison();
  $("mmc_y").onchange = ()=> runComparison();

  // ---------- preload sample on SYAI tab ----------
  initSYAI(SAMPLE_TEXT);

})();
</script>
</body>
</html>
"""

# inject image URIs
html = html.replace("SCATTER_DATA_URI", SCATTER_URI or "")
html = html.replace("CORR_DATA_URI", CORR_URI or "")
html = html.replace("HAS_SCATTER_FLAG", "1" if SCATTER_FOUND else "0")
html = html.replace("HAS_CORR_FLAG", "1" if CORR_FOUND else "0")

# inject *exact same* sample text used by both Load and Download
html = html.replace("__INJECT_SAMPLE_CSV__", SAMPLE_CSV.replace("`","\\`"))

components.html(html, height=4200, scrolling=True)
