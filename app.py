# app.py
import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SYAI-Rank", layout="wide")

APP_DIR = Path(__file__).resolve().parent

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

st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #0b0b0f 0%, #0b0b0f 35%, #ffe4e6 120%) !important; }
[data-testid="stSidebar"] { background: rgba(255, 228, 230, 0.08) !important; backdrop-filter: blur(6px); }
</style>
""", unsafe_allow_html=True)

html = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>SYAI-Rank</title>
<style>
  :root{
    --bg-dark:#0b0b0f; --bg-light:#f8fafc; --grad-light:#ffe4e6;
    --card-dark:#0f1115cc; --card-light:#ffffffcc; --text-light:#f5f5f5;
    --pink:#ec4899; --pink-700:#db2777; --border-dark:#262b35; --border-light:#fbcfe8;
  }
  *{box-sizing:border-box} html,body{height:100%;margin:0}
  body{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Ubuntu,Cantarell,"Noto Sans","Helvetica Neue",Arial}
  body.theme-dark{ color:var(--text-light); background:linear-gradient(180deg,#0b0b0f 0%,#0b0b0f 35%,var(--grad-light) 120%); }
  body.theme-light{ color:#111; background:linear-gradient(180deg,#f8fafc 0%,#f8fafc 40%,var(--grad-light) 120%); }

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
  .label{display:block;font-size:12px;opacity:.85;margin-bottom:4px}
  input[type="number"],select{width:100%;padding:10px 12px;border-radius:10px;border:1px solid #ddd;background:#f8fafc;color:#111}
  .hint{font-size:12px;opacity:.8}

  .table-wrap{overflow:auto;max-height:360px}
  table{width:100%;border-collapse:collapse;font-size:14px;color:#000}
  th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #e5e7eb}

  .mt2{margin-top:8px}.mt4{margin-top:16px}.mt6{margin-top:24px}.mb2{margin-bottom:8px}
  .w100{width:100%}

  .chart,.linechart{width:100%;border:1px dashed #2a2f38;border-radius:12px;padding:8px;background:transparent}
  .chart{height:360px}
  .linechart{height:300px}

  .chart2{width:100%;height:360px;border:1px dashed #2a2f38;border-radius:12px}
</style>
</head>
<body class="theme-dark">
<div class="container">
  <div id="err" style="display:none;background:#7f1d1d;color:#fff;padding:10px 12px;border:1px solid #fecaca;border-radius:8px;margin-bottom:8px"></div>

  <div class="header">
    <div class="title">SYAI-Rank</div>
    <div class="row">
      <a class="btn" id="downloadSample">⬇️ Sample CSV</a>
      <button class="toggle" id="themeToggle">🌙 Dark</button>
    </div>
  </div>

  <div class="tabs">
    <button class="tab active" id="tabSYAI">SYAI Method</button>
    <button class="tab" id="tabCompare">Comparison (TOPSIS, VIKOR, SAW, SYAI, COBRA, WASPAS, MOORA)</button>
  </div>

  <!-- ============= TAB 1: SYAI ONLY ============= -->
  <div id="viewSYAI">
    <div class="grid">
      <div>
        <div class="card dark">
          <div class="section-title">Step 1: Upload CSV</div>
          <label for="csv1" class="btn">📤 Choose CSV</label>
          <input id="csv1" type="file" accept=".csv" style="display:none"/>
          <p class="hint mt2">First column must be <b>Alternative</b>. Others are criteria.</p>
        </div>

        <div id="t1" class="card dark" style="display:none">
          <div class="section-title">Step 2: Criteria Types</div>
          <div id="types1" class="row" style="flex-wrap:wrap"></div>
        </div>

        <div id="w1" class="card dark" style="display:none">
          <div class="section-title">Step 3: Weights</div>
          <div class="row mb2" style="gap:16px">
            <label><input type="radio" name="wmode1" id="w1eq" checked> Equal (1/m)</label>
            <label><input type="radio" name="wmode1" id="w1c"> Custom (raw; normalized on run)</label>
          </div>
          <div id="wg1" class="row" style="display:none;flex-wrap:wrap"></div>
        </div>

        <div id="b1" class="card dark" style="display:none">
          <div class="section-title">Step 4: β (blend of D⁺ and D⁻)</div>
          <input id="beta1" type="range" min="0" max="1" step="0.01" value="0.5" class="w100"/>
          <div class="hint mt2">β = <b id="beta1v">0.50</b></div>
          <button class="btn mt4" id="runSYAI">Run SYAI</button>
        </div>
      </div>

      <div>
        <div id="m1" class="card" style="display:none">
          <div class="section-title">Decision Matrix (first 10 rows)</div>
          <div class="table-wrap"><table id="tblm1"></table></div>
        </div>
        <div id="r1" class="card" style="display:none">
          <div class="section-title">SYAI Results</div>
          <div class="table-wrap"><table id="tblr1"></table></div>
          <div class="mt6">
            <div class="hint mb2">Bar Chart (Closeness)</div>
            <div class="chart"><svg id="bar1" width="100%" height="100%"></svg></div>
          </div>
          <div class="mt6">
            <div class="hint mb2">Line Chart (Rank vs Closeness)</div>
            <div class="linechart"><svg id="line1" width="100%" height="100%"></svg></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ============= TAB 2: COMPARISON ============= -->
  <div id="viewCompare" style="display:none">
    <div class="grid">
      <div>
        <div class="card dark">
          <div class="section-title">Step A: Upload CSV</div>
          <label for="csv2" class="btn">📤 Choose CSV</label>
          <input id="csv2" type="file" accept=".csv" style="display:none"/>
          <button class="btn mt2" id="demo2">📄 Load Demo CSV</button>
          <p class="hint mt2">First column is <b>Alternative</b>.</p>
        </div>

        <div id="t2" class="card dark" style="display:none">
          <div class="section-title">Step B: Criteria Types</div>
          <div id="types2" class="row" style="flex-wrap:wrap"></div>
        </div>

        <div id="w2" class="card dark" style="display:none">
          <div class="section-title">Step C: Weights</div>
          <div class="row mb2" style="gap:16px">
            <label><input type="radio" name="wmode2" id="w2eq" checked> Equal (1/m)</label>
            <label><input type="radio" name="wmode2" id="w2c"> Custom (raw; normalized)</label>
          </div>
          <div id="wg2" class="row" style="display:none;flex-wrap:wrap"></div>
        </div>

        <div class="card dark">
          <div class="section-title">Step D: Run</div>
          <button class="btn" id="runCmp">▶️ Run Comparison</button>
        </div>
      </div>

      <div>
        <div id="m2" class="card" style="display:none">
          <div class="section-title">Decision Matrix (first 10 rows)</div>
          <div class="table-wrap"><table id="tblm2"></table></div>
        </div>

        <div id="rcmp" class="card" style="display:none">
          <div class="section-title">Scores & Ranks</div>
          <div class="table-wrap"><table id="mmc_table"></table></div>

          <div class="mt6">
            <div class="hint mb2">Grouped Bar — <b>rank only</b> (axes black)</div>
            <div class="chart2"><svg id="mmc_bar" width="100%" height="100%"></svg></div>
          </div>

          <div class="mt6">
            <div class="hint">Scatter (axes black, Pearson r line)</div>
            <div class="row" style="gap:12px;align-items:center">
              <div class="hint">X:</div>
              <select id="mmc_x"><option>SYAI</option><option>TOPSIS</option><option>VIKOR</option><option>SAW</option><option>COBRA</option><option>WASPAS</option><option>MOORA</option></select>
              <div class="hint">Y:</div>
              <select id="mmc_y"><option>TOPSIS</option><option>SYAI</option><option>VIKOR</option><option>SAW</option><option>COBRA</option><option>WASPAS</option><option>MOORA</option></select>
            </div>
            <div class="chart2"><svg id="mmc_sc" width="100%" height="100%"></svg></div>
          </div>

          <div class="mt6">
            <div class="hint mb2">Correlation Heatmap — Pearson r and p-values (axes black)</div>
            <div class="chart2" style="height:460px"><svg id="mmc_heat" width="100%" height="100%"></svg></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
(function(){
  const $ = (id)=> document.getElementById(id);
  const show = (el,on=true)=> el.style.display = on ? "" : "none";
  const err = (msg)=>{ const e=$("err"); e.textContent="Error: "+msg; e.style.display="block"; };

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
  $("tabSYAI").onclick = ()=>{ $("tabSYAI").classList.add("active"); $("tabCompare").classList.remove("active"); show($("viewSYAI"),true); show($("viewCompare"),false); };
  $("tabCompare").onclick = ()=>{ $("tabCompare").classList.add("active"); $("tabSYAI").classList.remove("active"); show($("viewSYAI"),false); show($("viewCompare"),true); };

  // sample CSV
  const sampleCSV = `Alternative,Cost,Quality,Delivery
A1,200,8,4
A2,250,7,5
A3,300,9,6
A4,220,8,4
A5,180,6,7
`;
  $("downloadSample").href = "data:text/csv;charset=utf-8,"+encodeURIComponent(sampleCSV);
  $("downloadSample").download = "sample.csv";

  // helpers
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
  function vectorNorm(vals){ const d=Math.sqrt(vals.reduce((s,v)=>s+(v*v),0))||1; return vals.map(v=>v/d); }

  // unified normalization (maps to [0.01,1])
  function normalizeColumn(vals, ctype, goal){
    const max=Math.max(...vals), min=Math.min(...vals), R=max-min;
    let xStar;
    if(ctype==="Benefit") xStar=max;
    else if(ctype==="Cost") xStar=min;
    else {
      const g=parseFloat(goal);
      xStar=isFinite(g)? g : (vals.reduce((s,v)=>s+(isFinite(v)?v:0),0)/vals.length);
    }
    if(Math.abs(R)<1e-12) return vals.map(_=>1.0);
    return vals.map(x=> Math.max(0.01, Math.min(1, 0.01 + (1-0.01)*(1-Math.abs(x-xStar)/R))));
  }

  // ======= TAB 1 (SYAI) state =======
  let c1=[], r1=[], crit1=[], type1={}, ideal1={}, w1={}, wmode1='equal', beta1=0.5;
  $("beta1").oninput = ()=>{ beta1=parseFloat($("beta1").value); $("beta1v").textContent=beta1.toFixed(2); };
  $("w1eq").onchange = ()=>{ wmode1='equal'; $("wg1").style.display="none"; };
  $("w1c").onchange  = ()=>{ wmode1='custom'; $("wg1").style.display=""; };

  $("csv1").onchange = (e)=> {
    const f=e.target.files[0]; if(!f) return;
    const r=new FileReader();
    r.onload=()=> initSYAI(String(r.result));
    r.readAsText(f);
  };

  function initSYAI(txt){
    const arr=parseCSVText(txt);
    c1 = arr[0].map(x=>String(x??"").trim());
    if(c1[0] !== "Alternative"){
      const idx=c1.indexOf("Alternative");
      if(idx>0){ const nm=c1.splice(idx,1)[0]; c1.unshift(nm); } else c1[0]="Alternative";
    }
    crit1 = c1.slice(1);
    r1 = arr.slice(1).filter(r=>r.length>=c1.length).map(r=>{
      const o={}; c1.forEach((c,i)=> o[c]=r[i]); return o;
    });
    type1  = Object.fromEntries(crit1.map(c=>[c,"Benefit"]));
    ideal1 = Object.fromEntries(crit1.map(c=>[c,""]));
    w1     = Object.fromEntries(crit1.map(c=>[c,1]));
    renderMatrix("tblm1", c1, r1);
    renderTypes("types1", crit1, type1, ideal1);
    renderWeights("wg1", crit1, w1);
    show($("m1"),true); show($("t1"),true); show($("w1"),true); show($("b1"),true); show($("r1"),false);
  }

  // ======= TAB 2 (Comparison) state =======
  let c2=[], r2=[], crit2=[], type2={}, ideal2={}, w2={}, wmode2='equal';
  $("w2eq").onchange = ()=>{ wmode2='equal'; $("wg2").style.display="none"; };
  $("w2c").onchange  = ()=>{ wmode2='custom'; $("wg2").style.display=""; };
  $("csv2").onchange = (e)=> {
    const f=e.target.files[0]; if(!f) return;
    const r=new FileReader();
    r.onload=()=> initCmp(String(r.result));
    r.readAsText(f);
  };
  $("demo2").onclick = ()=> initCmp(sampleCSV);

  function initCmp(txt){
    const arr=parseCSVText(txt);
    c2 = arr[0].map(x=>String(x??"").trim());
    if(c2[0] !== "Alternative"){
      const idx=c2.indexOf("Alternative");
      if(idx>0){ const nm=c2.splice(idx,1)[0]; c2.unshift(nm); } else c2[0]="Alternative";
    }
    crit2 = c2.slice(1);
    r2 = arr.slice(1).filter(r=>r.length>=c2.length).map(r=>{
      const o={}; c2.forEach((c,i)=> o[c]=r[i]); return o;
    });
    type2  = Object.fromEntries(crit2.map(c=>[c,"Benefit"]));
    ideal2 = Object.fromEntries(crit2.map(c=>[c,""]));
    w2     = Object.fromEntries(crit2.map(c=>[c,1]));
    renderMatrix("tblm2", c2, r2);
    renderTypes("types2", crit2, type2, ideal2);
    renderWeights("wg2", crit2, w2);
    show($("m2"),true); show($("t2"),true); show($("w2"),true); show($("rcmp"),false);
  }

  // ======= shared UI pieces =======
  function renderMatrix(tid, cols, rows){
    const tb=$(tid); tb.innerHTML="";
    const thead=document.createElement("thead"); const trh=document.createElement("tr");
    cols.forEach(c=>{ const th=document.createElement("th"); th.textContent=c; trh.appendChild(th); });
    thead.appendChild(trh); tb.appendChild(thead);
    const tbody=document.createElement("tbody");
    rows.slice(0,10).forEach(r=>{
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
      box.style.minWidth="220px"; box.style.marginRight="12px";
      const lab=document.createElement("div"); lab.className="label"; lab.textContent=c; box.appendChild(lab);
      const sel=document.createElement("select");
      ["Benefit","Cost","Ideal (Goal)"].forEach(v=>{ const o=document.createElement("option"); o.textContent=v; sel.appendChild(o); });
      sel.value = types[c]||"Benefit";
      sel.onchange = ()=>{ types[c]=sel.value; renderTypes(id,crits,types,ideals); };
      box.appendChild(sel);
      if((types[c]||"")==="Ideal (Goal)"){
        const inp=document.createElement("input"); inp.className="mt2"; inp.type="number"; inp.step="any"; inp.placeholder="Goal";
        inp.value=ideals[c]||""; inp.oninput=()=> ideals[c]=inp.value; box.appendChild(inp);
      } else { delete ideals[c]; }
      wrap.appendChild(box);
    });
  }

  function renderWeights(id, crits, weights){
    const wrap=$(id); wrap.innerHTML="";
    crits.forEach(c=>{
      const box=document.createElement("div"); box.style.minWidth="140px"; box.style.marginRight="12px";
      const lab=document.createElement("div"); lab.className="label"; lab.textContent="w("+c+")"; box.appendChild(lab);
      const inp=document.createElement("input"); inp.type="number"; inp.step="0.001"; inp.min="0"; inp.value=weights[c]??0;
      inp.oninput=()=> weights[c]=inp.value; box.appendChild(inp);
      wrap.appendChild(box);
    });
  }

  // ======= Core SYAI compute (used in both tabs) =======
  function computeSYAI(rows, crits, types, ideals, weights, wmode, beta){
    const X = rows.map(r=> Object.fromEntries(crits.map(c=>[c, toNum(r[c])])) );
    const N = {};
    crits.forEach(c=>{
      const vals = X.map(row=>row[c]);
      N[c] = normalizeColumn(vals, types[c]||"Benefit", ideals[c]);
    });

    const w={};
    if(wmode==='equal'){ crits.forEach(c=> w[c]=1/crits.length); }
    else{
      let s=0; crits.forEach(c=>{ const v=Math.max(0,parseFloat(weights[c]||0)); w[c]=isFinite(v)?v:0; s+=w[c]; });
      if(s<=0) crits.forEach(c=> w[c]=1/crits.length); else crits.forEach(c=> w[c]/=s);
    }

    const W = rows.map((_,i)=> Object.fromEntries(crits.map(c=>[c, N[c][i]*w[c]])) );
    const Aplus={}, Aminus={};
    crits.forEach(c=>{
      let mx=-Infinity, mn=Infinity;
      W.forEach(r=>{ if(r[c]>mx) mx=r[c]; if(r[c]<mn) mn=r[c]; });
      Aplus[c]=mx; Aminus[c]=mn;
    });

    return rows.map((r,i)=>{
      let Dp=0, Dm=0;
      crits.forEach(c=>{ Dp+=Math.abs(W[i][c]-Aplus[c]); Dm+=Math.abs(W[i][c]-Aminus[c]); });
      const denom = beta*Dp + (1-beta)*Dm || Number.EPSILON;
      const Close = ((1-beta)*Dm)/denom;
      return { alt:String(r["Alternative"]), Dp, Dm, Close, Wrow:W[i], Nrow:Object.fromEntries(crits.map(c=>[c,N[c][i]])), w };
    });
  }

  // ======= TAB 1: run SYAI =======
  $("runSYAI").onclick = ()=>{
    if(!r1.length) return;
    const res = computeSYAI(r1, crit1, type1, ideal1, w1, wmode1, beta1)
      .map(o=> ({Alternative:o.alt, Dp:o.Dp, Dm:o.Dm, Close:o.Close}));
    res.sort((a,b)=> b.Close-a.Close);
    res.forEach((r,i,arr)=> r.Rank = i+1);

    // table
    const tb=$("tblr1"); tb.innerHTML="";
    const thead=document.createElement("thead"); const trh=document.createElement("tr");
    ["Alternative","D+","D-","Closeness","Rank"].forEach(h=>{ const th=document.createElement("th"); th.textContent=h; trh.appendChild(th); });
    thead.appendChild(trh); tb.appendChild(thead);
    const tbody=document.createElement("tbody");
    res.forEach(r=>{
      const tr=document.createElement("tr");
      [r.Alternative, r.Dp.toFixed(6), r.Dm.toFixed(6), r.Close.toFixed(6), r.Rank].forEach(v=>{
        const td=document.createElement("td"); td.textContent=String(v); tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    tb.appendChild(tbody);
    show($("r1"),true);

    // charts
    drawBar("bar1", res.map(d=>({name:d.Alternative, value:d.Close})));
    drawLine("line1", res.map(d=>({rank:d.Rank, value:d.Close, name:d.Alternative})));
  };

  // ======= TAB 2: run comparison =======
  $("runCmp").onclick = ()=>{
    if(!r2.length) return;

    // shared bases
    const sy = computeSYAI(r2, crit2, type2, ideal2, w2, wmode2, 0.5); // beta fixed 0.5 for comparison
    const w = sy[0].w;

    // SAW utilities (same normalization)
    const U={};
    crit2.forEach(c=>{ U[c] = sy.map(o=> o.Nrow[c]); });

    // ---------- SAW ----------
    const SAW = sy.map((_,i)=> crit2.reduce((s,c)=> s + w[c]*U[c][i], 0));

    // ---------- WASPAS ----------
    const WSM = SAW.slice();
    const WPM = sy.map((_,i)=> crit2.reduce((p,c)=> p * Math.pow(Math.max(U[c][i],1e-12), w[c]), 1));
    const WASPAS = sy.map((_,i)=> 0.5*WSM[i] + 0.5*WPM[i]);

    // ---------- MOORA ----------
    const N_vec={}; crit2.forEach(c=>{
      const raw = r2.map(r=> toNum(r[c]));
      if((type2[c]||"Benefit")==="Ideal (Goal)"){ N_vec[c]=U[c]; }
      else N_vec[c]=vectorNorm(raw);
    });
    const MOORA = sy.map((_,i)=>{
      let sumB=0, sumC=0;
      crit2.forEach(c=>{
        if((type2[c]||"Benefit")==="Cost") sumC += w[c]*N_vec[c][i];
        else sumB += w[c]*N_vec[c][i];
      });
      return sumB - sumC;
    });

    // ---------- TOPSIS ----------
    const Nt={}; crit2.forEach(c=>{ Nt[c]=vectorNorm(r2.map(r=> toNum(r[c]))); });
    const Wt = sy.map((_,i)=> Object.fromEntries(crit2.map(c=>[c, Nt[c][i]*w[c]])) );
    const Aplus={}, Aminus={}; crit2.forEach(c=>{
      const arr=Wt.map(r=>r[c]);
      if((type2[c]||"Benefit")==="Cost"){ Aplus[c]=Math.min(...arr); Aminus[c]=Math.max(...arr); }
      else { Aplus[c]=Math.max(...arr); Aminus[c]=Math.min(...arr); }
    });
    const TOPSIS = sy.map((_,i)=>{
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
    const v=0.5;
    const VIKOR = S.map((_,i)=> v*((S[i]-Smin)/((Smax-Smin)||1)) + (1-v)*((R[i]-Rmin)/((Rmax-Rmin)||1)));

    // ---------- SYAI (from compute) ----------
    const SYAI = sy.map(o=> o.Close);

    // ---------- COBRA (centered distance to ideal in SAW-unit space; lower=better; can be negative) ----------
    const d = sy.map((_,i)=> crit2.reduce((s,c)=> s + w[c]*(1 - U[c][i]), 0));
    const meanD = d.reduce((s,v)=>s+v,0)/d.length;
    const COBRA = d.map(v=> v - meanD); // centered → best are most negative

    // ranks
    function ranksHigher(a){ const idx=a.map((v,i)=>({v,i})).sort((x,y)=> y.v-x.v); const rk=new Array(a.length); idx.forEach((o,k)=> rk[o.i]=k+1); return rk; }
    function ranksLower(a){ const idx=a.map((v,i)=>({v,i})).sort((x,y)=> x.v-y.v); const rk=new Array(a.length); idx.forEach((o,k)=> rk[o.i]=k+1); return rk; }

    const methods={TOPSIS, VIKOR, SAW, SYAI, COBRA, WASPAS, MOORA};
    const ranks={ TOPSIS:ranksHigher(TOPSIS), VIKOR:ranksLower(VIKOR), SAW:ranksHigher(SAW),
                  SYAI:ranksHigher(SYAI), COBRA:ranksLower(COBRA), WASPAS:ranksHigher(WASPAS), MOORA:ranksHigher(MOORA) };

    // table
    const methodsOrder=["TOPSIS","VIKOR","SAW","SYAI","COBRA","WASPAS","MOORA"];
    const tb=$("mmc_table"); tb.innerHTML="";
    const thead=document.createElement("thead"); const trh=document.createElement("tr");
    ["Alternative"].concat(methodsOrder).forEach(h=>{ const th=document.createElement("th"); th.textContent=h; trh.appendChild(th); });
    thead.appendChild(trh); tb.appendChild(thead);
    const tbody=document.createElement("tbody");
    r2.forEach((row,i)=>{
      const tr=document.createElement("tr");
      const t0=document.createElement("td"); t0.textContent=String(row["Alternative"]); tr.appendChild(t0);
      methodsOrder.forEach(m=>{
        const td=document.createElement("td"); td.textContent = methods[m][i].toFixed(4)+" ("+ranks[m][i]+")"; tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    tb.appendChild(tbody);
    show($("rcmp"),true);

    // charts
    drawCmpBars(methods, ranks, r2.map(r=> String(r["Alternative"])));
    const res={methods, ranks, names:r2.map(r=> String(r["Alternative"]))};
    drawCmpScatter(res);
    drawHeat(res);
  };

  // ================= Charts & Heatmap =================
  const COLORS=["#111827","#1f2937","#374151","#4b5563","#6b7280","#9ca3af","#d1d5db","#e5e7eb"];

  function drawBar(svgId, data){
    const svg=$(svgId); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const W=(svg.getBoundingClientRect().width||800), H=(svg.getBoundingClientRect().height||360);
    svg.setAttribute("viewBox","0 0 "+W+" "+H);
    const padL=50,padR=20,padT=18,padB=44;
    const max=Math.max(...data.map(d=>d.value))||1;
    const cell=(W-padL-padR)/data.length, barW=cell*0.8;

    // axes lines (black)
    const yAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    yAxis.setAttribute("x1",String(padL)); yAxis.setAttribute("x2",String(padL));
    yAxis.setAttribute("y1",String(padT)); yAxis.setAttribute("y2",String(H-padB)); yAxis.setAttribute("stroke","#000"); svg.appendChild(yAxis);
    const xAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    xAxis.setAttribute("x1",String(padL)); xAxis.setAttribute("x2",String(W-padR));
    xAxis.setAttribute("y1",String(H-padB)); xAxis.setAttribute("y2",String(H-padB)); xAxis.setAttribute("stroke","#000"); svg.appendChild(xAxis);

    for(let t=0;t<=5;t++){
      const val=max*t/5, y=H-padB-(H-padT-padB)*(val/max);
      const gl=document.createElementNS("http://www.w3.org/2000/svg","line");
      gl.setAttribute("x1",String(padL)); gl.setAttribute("x2",String(W-padR));
      gl.setAttribute("y1",String(y)); gl.setAttribute("y2",String(y));
      gl.setAttribute("stroke","#000"); gl.setAttribute("stroke-dasharray","3 3"); svg.appendChild(gl);
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x",String(padL-10)); tx.setAttribute("y",String(y+4)); tx.setAttribute("text-anchor","end");
      tx.setAttribute("font-size","12"); tx.setAttribute("fill","#000"); tx.textContent=val.toFixed(2); svg.appendChild(tx);
    }

    data.forEach((d,i)=>{
      const x=padL+i*cell+(cell-barW)/2; const h=(H-padT-padB)*(d.value/max); const y=H-padB-h;
      const r=document.createElementNS("http://www.w3.org/2000/svg","rect");
      r.setAttribute("x",String(x)); r.setAttribute("y",String(y)); r.setAttribute("width",String(barW)); r.setAttribute("height",String(h));
      r.setAttribute("fill","#f9a8d4"); svg.appendChild(r);
      const lbl=document.createElementNS("http://www.w3.org/2000/svg","text");
      lbl.setAttribute("x",String(x+barW/2)); lbl.setAttribute("y",String(H-12)); lbl.setAttribute("text-anchor","middle");
      lbl.setAttribute("font-size","12"); lbl.setAttribute("fill","#000"); lbl.textContent=d.name; svg.appendChild(lbl);
    });
  }

  function drawLine(svgId, data){
    const svg=$(svgId); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const W=(svg.getBoundingClientRect().width||800), H=(svg.getBoundingClientRect().height||300);
    svg.setAttribute("viewBox","0 0 "+W+" "+H);
    const padL=50,padR=20,padT=14,padB=30;
    const maxY=Math.max(...data.map(d=>d.value))||1, minX=1, maxX=Math.max(...data.map(d=>d.rank))||1;
    const sx=(r)=> padL+(W-padL-padR)*((r-minX)/(maxX-minX||1));
    const sy=(v)=> H-padB-(H-padT-padB)*(v/maxY);

    // axes
    const yAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    yAxis.setAttribute("x1",String(padL)); yAxis.setAttribute("x2",String(padL));
    yAxis.setAttribute("y1",String(padT)); yAxis.setAttribute("y2",String(H-padB)); yAxis.setAttribute("stroke","#000"); svg.appendChild(yAxis);
    const xAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    xAxis.setAttribute("x1",String(padL)); xAxis.setAttribute("x2",String(W-padR));
    xAxis.setAttribute("y1",String(H-padB)); xAxis.setAttribute("y2",String(H-padB)); xAxis.setAttribute("stroke","#000"); svg.appendChild(xAxis);

    const p=document.createElementNS("http://www.w3.org/2000/svg","path");
    let dstr="";
    data.sort((a,b)=> a.rank-b.rank).forEach((pt,i)=>{
      const x=sx(pt.rank), y=sy(pt.value);
      dstr += (i===0? "M":"L")+x+" "+y+" ";
      const c=document.createElementNS("http://www.w3.org/2000/svg","circle");
      c.setAttribute("cx",String(x)); c.setAttribute("cy",String(y)); c.setAttribute("r","4"); c.setAttribute("fill","#64748b");
      svg.appendChild(c);
      const t=document.createElementNS("http://www.w3.org/2000/svg","text");
      t.setAttribute("x",String(x+6)); t.setAttribute("y",String(y-6)); t.setAttribute("font-size","12"); t.setAttribute("fill","#000");
      t.textContent=pt.value.toFixed(3); svg.appendChild(t);
    });
    p.setAttribute("d", dstr.trim()); p.setAttribute("fill","none"); p.setAttribute("stroke","#64748b"); p.setAttribute("stroke-width","2");
    svg.appendChild(p);

    for(let r=1;r<=maxX;r++){
      const x=sx(r);
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x",String(x)); tx.setAttribute("y",String(H-8)); tx.setAttribute("text-anchor","middle"); tx.setAttribute("font-size","12"); tx.setAttribute("fill","#000");
      tx.textContent=String(r); svg.appendChild(tx);
    }
  }

  function drawCmpBars(methods, ranks, names){
    const svg=$("mmc_bar"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const W=(svg.getBoundingClientRect().width||900), H=(svg.getBoundingClientRect().height||360);
    svg.setAttribute("viewBox","0 0 "+W+" "+H);
    const padL=70,padR=20,padT=20,padB=60;
    const mOrder=["TOPSIS","VIKOR","SAW","SYAI","COBRA","WASPAS","MOORA"];
    const vals = names.map((nm,i)=> mOrder.map(m=> methods[m][i]));
    const max = Math.max(...vals.flat()), min = Math.min(...vals.flat());
    const yMin=Math.min(min,0), yMax=Math.max(max,0), range=(yMax-yMin)||1;

    // axes (black)
    const yAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    yAxis.setAttribute("x1",String(padL)); yAxis.setAttribute("x2",String(padL));
    yAxis.setAttribute("y1",String(padT)); yAxis.setAttribute("y2",String(H-padB)); yAxis.setAttribute("stroke","#000"); svg.appendChild(yAxis);
    const xAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    xAxis.setAttribute("x1",String(padL)); xAxis.setAttribute("x2",String(W-padR));
    xAxis.setAttribute("y1",String(H-padB)); xAxis.setAttribute("y2",String(H-padB)); xAxis.setAttribute("stroke","#000"); svg.appendChild(xAxis);

    for(let t=0;t<=5;t++){
      const val=yMin + range*t/5;
      const y=H-padB - (H-padT-padB)*((val-yMin)/range);
      const gl=document.createElementNS("http://www.w3.org/2000/svg","line");
      gl.setAttribute("x1",String(padL)); gl.setAttribute("x2",String(W-padR));
      gl.setAttribute("y1",String(y)); gl.setAttribute("y2",String(y));
      gl.setAttribute("stroke","#000"); gl.setAttribute("stroke-dasharray","3 3"); svg.appendChild(gl);
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x",String(padL-10)); tx.setAttribute("y",String(y+4)); tx.setAttribute("text-anchor","end");
      tx.setAttribute("font-size","12"); tx.setAttribute("fill","#000"); tx.textContent=val.toFixed(2); svg.appendChild(tx);
    }

    const cell=(W-padL-padR)/names.length;
    const barW=(cell*0.8)/mOrder.length;

    names.forEach((nm,i)=>{
      const x0=padL + i*cell + (cell - barW*mOrder.length)/2;
      const lbl=document.createElementNS("http://www.w3.org/2000/svg","text");
      lbl.setAttribute("x",String(x0 + barW*mOrder.length/2)); lbl.setAttribute("y",String(H-8));
      lbl.setAttribute("text-anchor","middle"); lbl.setAttribute("font-size","12"); lbl.setAttribute("fill","#000"); lbl.textContent=nm; svg.appendChild(lbl);
      mOrder.forEach((m,k)=>{
        const v=methods[m][i];
        const y=H-padB - (H-padT-padB)*((v-yMin)/range);
        const h=H-padB - y;
        const rect=document.createElementNS("http://www.w3.org/2000/svg","rect");
        rect.setAttribute("x",String(x0 + k*barW)); rect.setAttribute("y",String(h>=0? y : H-padB));
        rect.setAttribute("width",String(barW-1.5)); rect.setAttribute("height",String(Math.abs(h)));
        rect.setAttribute("fill", COLORS[k%COLORS.length]); svg.appendChild(rect);

        // rank only
        const t=document.createElementNS("http://www.w3.org/2000/svg","text");
        t.setAttribute("x",String(x0 + k*barW + (barW-1.5)/2)); t.setAttribute("y",String((h>=0? y : H-padB)-4));
        t.setAttribute("text-anchor","middle"); t.setAttribute("font-size","11"); t.setAttribute("fill","#000");
        t.textContent=String(ranks[m][i]); svg.appendChild(t);
      });
    });
  }

  // Pearson p-value helpers
  function betacf(a,b,x){ const MAXIT=200, EPS=3e-7, FPMIN=1e-30; let qab=a+b,qap=a+1,qam=a-1; let c=1,d=1-(qab*x/qap); if(Math.abs(d)<FPMIN) d=FPMIN; d=1/d; let h=d;
    for(let m=1, m2=2; m<=MAXIT; m++, m2+=2){ let aa=m*(b-m)*x/((qam+m2)*(a+m2)); d=1+aa*d; if(Math.abs(d)<FPMIN) d=FPMIN; c=1+aa/c; if(Math.abs(c)<FPMIN) c=FPMIN; d=1/d; h*=d*c;
      aa=-(a+m)*(qab+m)*x/((a+m2)*(qap+m2)); d=1+aa*d; if(Math.abs(d)<FPMIN) d=FPMIN; c=1+aa/c; if(Math.abs(c)<FPMIN) c=FPMIN; d=1/d; const del=d*c; h*=del; if(Math.abs(del-1)<EPS) break;}
    return h; }
  Math.logGamma = function(z){ const g=7, p=[0.99999999999980993,676.5203681218851,-1259.1392167224028,771.32342877765313,-176.61502916214059,12.507343278686905,-0.13857109526572012,9.9843695780195716e-6,1.5056327351493116e-7];
    if(z<0.5) return Math.log(Math.PI)-Math.log(Math.sin(Math.PI*z))-Math.logGamma(1-z);
    z-=1; let x=p[0]; for(let i=1;i<g+2;i++) x+=p[i]/(z+i); const t=z+g+0.5;
    return 0.5*Math.log(2*Math.PI)+(z+0.5)*Math.log(t)-t+Math.log(x)-Math.log(z+1); }
  Math.logBeta = (a,b)=> Math.logGamma(a)+Math.logGamma(b)-Math.logGamma(a+b);
  function tCDF(t, df){ const x=df/(df+t*t); const a=df/2, b=0.5; const bt = Math.exp((a*Math.log(x)) + (b*Math.log(1-x)) - Math.logBeta(a,b));
    const val = x< (a+1)/(a+b+2) ? bt*betacf(a,b,x)/a : 1 - bt*betacf(b,a,1-x)/b; return t>0 ? 1 - 0.5*val : 0.5*val; }
  function pearsonP(r,n){ const df=n-2; if(df<=0) return 1; const t=Math.abs(r)*Math.sqrt(df/(1-r*r+1e-12)); return Math.max(0, Math.min(1, 2*(1 - tCDF(t,df)))); }

  function drawCmpScatter(res){
    const svg=$("mmc_sc"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const W=(svg.getBoundingClientRect().width||900), H=(svg.getBoundingClientRect().height||360);
    svg.setAttribute("viewBox","0 0 "+W+" "+H);
    const padL=60,padR=20,padT=20,padB=50;
    const mx=$("mmc_x").value, my=$("mmc_y").value;
    const xs=res.methods[mx], ys=res.methods[my];
    const Xmin=Math.min(...xs), Xmax=Math.max(...xs), Ymin=Math.min(...ys), Ymax=Math.max(...ys);
    const sx=(x)=> padL + (W-padL-padR)*((x-Xmin)/((Xmax-Xmin)||1));
    const sy=(y)=> H-padB - (H-padT-padB)*((y-Ymin)/((Ymax-Ymin)||1));

    // axes (black)
    const ax=document.createElementNS("http://www.w3.org/2000/svg","line");
    ax.setAttribute("x1",String(padL)); ax.setAttribute("x2",String(padL)); ax.setAttribute("y1",String(padT)); ax.setAttribute("y2",String(H-padB)); ax.setAttribute("stroke","#000"); svg.appendChild(ax);
    const ay=document.createElementNS("http://www.w3.org/2000/svg","line");
    ay.setAttribute("x1",String(padL)); ay.setAttribute("x2",String(W-padR)); ay.setAttribute("y1",String(H-padB)); ay.setAttribute("y2",String(H-padB)); ay.setAttribute("stroke","#000"); svg.appendChild(ay);

    // points
    res.names.forEach((nm,i)=>{
      const c=document.createElementNS("http://www.w3.org/2000/svg","circle");
      c.setAttribute("cx",String(sx(xs[i]))); c.setAttribute("cy",String(sy(ys[i]))); c.setAttribute("r","5"); c.setAttribute("fill","#94a3b8");
      svg.appendChild(c);
      const t=document.createElementNS("http://www.w3.org/2000/svg","text");
      t.setAttribute("x",String(sx(xs[i])+6)); t.setAttribute("y",String(sy(ys[i])-6)); t.setAttribute("font-size","12"); t.setAttribute("fill","#000");
      t.textContent=nm; svg.appendChild(t);
    });

    // r line
    const mean=(a)=> a.reduce((s,v)=>s+v,0)/a.length;
    const mxv=mean(xs), myv=mean(ys);
    let num=0, dx=0, dy=0;
    for(let i=0;i<xs.length;i++){ const a=xs[i]-mxv, b=ys[i]-myv; num+=a*b; dx+=a*a; dy+=b*b; }
    const r = num/Math.sqrt((dx||1)*(dy||1));
    const b = num/(dx||1), a = myv - b*mxv;
    const line=document.createElementNS("http://www.w3.org/2000/svg","line");
    line.setAttribute("x1",String(padL)); line.setAttribute("y1",String(sy(a+b*Xmin)));
    line.setAttribute("x2",String(W-padR)); line.setAttribute("y2",String(sy(a+b*Xmax)));
    line.setAttribute("stroke","#000"); line.setAttribute("stroke-width","2"); svg.appendChild(line);
    const cap=document.createElementNS("http://www.w3.org/2000/svg","text");
    cap.setAttribute("x",String((padL+W-padR)/2)); cap.setAttribute("y",String(padT+14)); cap.setAttribute("text-anchor","middle");
    cap.setAttribute("font-size","12"); cap.setAttribute("fill","#000"); cap.textContent="Pearson r = "+r.toFixed(3);
    svg.appendChild(cap);
  }
  $("mmc_x").onchange = ()=>{ const names=[].slice.call(document.querySelectorAll("#mmc_table tbody tr td:first-child")).map(td=>td.textContent); };
  $("mmc_y").onchange = ()=> drawCmpScatter(window.__lastRes||{methods:{SYAI:[],TOPSIS:[]},names:[]});

  function drawHeat(res){
    window.__lastRes = res;
    const svg=$("mmc_heat"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const W=(svg.getBoundingClientRect().width||900), H=(svg.getBoundingClientRect().height||460);
    svg.setAttribute("viewBox","0 0 "+W+" "+H);
    const padL=110, padR=20, padT=50, padB=80;
    const methods=["TOPSIS","VIKOR","SAW","SYAI","COBRA","WASPAS","MOORA"];
    const n=methods.length;
    const mat = methods.map(m => res.methods[m]);

    function corr(i,j){
      const x=mat[i], y=mat[j]; const m=x.length;
      const mx=x.reduce((s,v)=>s+v,0)/m, my=y.reduce((s,v)=>s+v,0)/m;
      let num=0, dx=0, dy=0;
      for(let k=0;k<m;k++){ const a=x[k]-mx, b=y[k]-my; num+=a*b; dx+=a*a; dy+=b*b; }
      const r = num/Math.sqrt((dx||1)*(dy||1));
      return {r, p: pearsonP(r,m)};
    }
    const RP = methods.map((_,i)=> methods.map((_,j)=> corr(i,j)));

    const cellW=(W-padL-padR)/n, cellH=(H-padT-padB)/n;
    function colorFor(r){ const v=Math.abs(r); const x=Math.floor(255*(1-v)); return "rgb("+x+","+x+",255)"; }

    // labels + axes (black)
    for(let i=0;i<n;i++){
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x",String(padL + i*cellW + cellW/2)); tx.setAttribute("y",String(padT-12));
      tx.setAttribute("transform","rotate(-45 "+(padL + i*cellW + cellW/2)+" "+(padT-12)+")");
      tx.setAttribute("text-anchor","end"); tx.setAttribute("font-size","12"); tx.setAttribute("fill","#000"); tx.textContent=methods[i]; svg.appendChild(tx);
      const ty=document.createElementNS("http://www.w3.org/2000/svg","text");
      ty.setAttribute("x",String(padL-10)); ty.setAttribute("y",String(padT + i*cellH + cellH/2 + 4));
      ty.setAttribute("text-anchor","end"); ty.setAttribute("font-size","12"); ty.setAttribute("fill","#000"); ty.textContent=methods[i]; svg.appendChild(ty);
    }

    for(let i=0;i<n;i++){
      for(let j=0;j<n;j++){
        const {r,p}=RP[i][j];
        const x=padL + j*cellW, y=padT + i*cellH;
        const rect=document.createElementNS("http://www.w3.org/2000/svg","rect");
        rect.setAttribute("x",String(x)); rect.setAttribute("y",String(y)); rect.setAttribute("width",String(cellW-1)); rect.setAttribute("height",String(cellH-1));
        rect.setAttribute("fill",colorFor(r)); rect.setAttribute("stroke","#000"); rect.setAttribute("stroke-width","0.3"); svg.appendChild(rect);
        const t1=document.createElementNS("http://www.w3.org/2000/svg","text");
        t1.setAttribute("x",String(x+cellW/2)); t1.setAttribute("y",String(y+cellH/2-2)); t1.setAttribute("text-anchor","middle");
        t1.setAttribute("font-size","12"); t1.setAttribute("fill","#000"); t1.textContent=r.toFixed(3); svg.appendChild(t1);
        const t2=document.createElementNS("http://www.w3.org/2000/svg","text");
        t2.setAttribute("x",String(x+cellW/2)); t2.setAttribute("y",String(y+cellH/2+14)); t2.setAttribute("text-anchor","middle");
        t2.setAttribute("font-size","11"); t2.setAttribute("fill","#000"); t2.textContent="p="+p.toExponential(2); svg.appendChild(t2);
      }
    }
  }
})();
</script>
</body>
</html>
"""

# Inject image URIs (kept for future extension if you want to show static big images)
html = html.replace("SCATTER_DATA_URI", SCATTER_URI or "")
html = html.replace("CORR_DATA_URI", CORR_URI or "")
html = html.replace("HAS_SCATTER_FLAG", "1" if SCATTER_FOUND else "0")
html = html.replace("HAS_CORR_FLAG", "1" if CORR_FOUND else "0")

components.html(html, height=3500, scrolling=True)
