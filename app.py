# app.py
import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SYAI-Rank", layout="wide")
APP_DIR = Path(__file__).resolve().parent

# (optional) embed local images if you add them later
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
    --pink:#ec4899; --pink-700:#db2777;
    --card:#ffffff; --border:#e5e7eb;
  }
  *{box-sizing:border-box}
  html,body{height:100%;margin:0}
  body{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial}

  .container{max-width:1200px;margin:24px auto;padding:0 16px}
  .header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
  .title{font-weight:800;font-size:28px;color:#111}
  .row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}

  .btn{display:inline-flex;align-items:center;gap:8px;padding:10px 14px;border-radius:12px;border:1px solid var(--pink-700);background:var(--pink);color:#fff;cursor:pointer}
  .btn:hover{filter:brightness(0.96)}
  .tabs{display:flex;gap:8px;margin:12px 0;position:relative;z-index:10}
  .tab{padding:10px 14px;border-radius:12px;border:1px solid #333;background:#e5e7eb;color:#111;cursor:pointer}
  .tab.active{background:var(--pink);border-color:var(--pink-700);color:#fff}

  .grid{display:grid;gap:16px;grid-template-columns:1fr}
  @media (min-width:1024px){.grid{grid-template-columns:1fr 2fr}}

  .card{background:var(--card);color:#111;border-radius:16px;padding:18px;border:1px solid var(--border)}
  .section-title{font-weight:700;font-size:18px;margin-bottom:12px;color:#db2777}
  .label{display:block;font-size:12px;opacity:.85;margin-bottom:4px}
  input[type="number"],select{width:100%;padding:10px 12px;border-radius:10px;border:1px solid #ddd;background:#f8fafc;color:#111}
  .hint{font-size:12px;opacity:.8}

  .table-wrap{overflow:auto;max-height:360px}
  table{width:100%;border-collapse:collapse;font-size:14px;color:#111}
  th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #e5e7eb}

  .chart2{width:100%;height:360px;border:1px dashed #9ca3af;border-radius:12px;background:#f9fafb}
  .chartTall{width:100%;height:480px;border:1px dashed #9ca3af;border-radius:12px;background:#f9fafb}

  .grid2{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}

  /* Tooltip */
  #tt{position:fixed;display:none;pointer-events:none;background:#111;color:#fff;
      padding:6px 8px;border-radius:8px;font-size:12px;box-shadow:0 4px 14px rgba(0,0,0,.25);z-index:9999}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="title">SYAI-Rank</div>
    <div class="row">
      <a class="btn" id="downloadSample">⬇️ Sample CSV</a>
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
        <div class="card">
          <div class="section-title">Step 1: Upload CSV</div>
          <label for="csv1" class="btn">📤 Choose CSV</label>
          <input id="csv1" type="file" accept=".csv" style="display:none"/>
          <button type="button" class="btn" id="demo1">📄 Load Demo CSV</button>
          <p class="hint mt2">First column is <b>Alternative</b>. Others are criteria.</p>
        </div>

        <div id="t1" class="card" style="display:none">
          <div class="section-title">Step 2: Criteria Types</div>
          <div id="types1" class="grid2"></div>
        </div>

        <div id="w1" class="card" style="display:none">
          <div class="section-title">Step 3: Weights</div>
          <div class="row mb2" style="gap:16px">
            <label><input type="radio" name="wmode1" id="w1eq" checked> Equal (1/m)</label>
            <label><input type="radio" name="wmode1" id="w1c"> Custom (raw; normalized)</label>
          </div>
          <div id="wg1" class="grid2" style="display:none"></div>
        </div>

        <div id="b1" class="card" style="display:none">
          <div class="section-title">Step 4: β (blend of D⁺ and D⁻)</div>
          <input id="beta1" type="range" min="0" max="1" step="0.01" value="0.5" style="width:100%"/>
          <div class="hint mt2">β = <b id="beta1v">0.50</b></div>
          <button type="button" class="btn mt4" id="runSYAI">Run SYAI</button>
        </div>
      </div>

      <div>
        <div id="m1" class="card" style="display:none">
          <div class="section-title">Decision Matrix (all rows)</div>
          <div class="table-wrap"><table id="tblm1"></table></div>
        </div>
        <div id="r1" class="card" style="display:none">
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
        <div class="card">
          <div class="section-title">Step A: Upload CSV</div>
          <label for="csv2" class="btn">📤 Choose CSV</label>
          <input id="csv2" type="file" accept=".csv" style="display:none"/>
          <button type="button" class="btn" id="demo2">📄 Load Demo CSV</button>
          <p class="hint mt2">First column is <b>Alternative</b>.</p>
        </div>

        <div id="t2" class="card" style="display:none">
          <div class="section-title">Step B: Criteria Types</div>
          <div id="types2" class="grid2"></div>
        </div>

        <div id="w2" class="card" style="display:none">
          <div class="section-title">Step C: Weights</div>
          <div class="row mb2" style="gap:16px">
            <label><input type="radio" name="wmode2" id="w2eq" checked> Equal (1/m)</label>
            <label><input type="radio" name="wmode2" id="w2c"> Custom (raw; normalized)</label>
          </div>
          <div id="wg2" class="grid2" style="display:none"></div>
        </div>

        <div class="card">
          <div class="section-title">Step D: Run</div>
          <button type="button" class="btn" id="runCmp">▶️ Run Comparison</button>
        </div>
      </div>

      <div>
        <div id="m2" class="card" style="display:none">
          <div class="section-title">Decision Matrix (all rows)</div>
          <div class="table-wrap"><table id="tblm2"></table></div>
        </div>

        <div id="rcmp" class="card" style="display:none">
          <div class="section-title">Scores & Ranks</div>
          <div class="table-wrap"><table id="mmc_table"></table></div>

          <div class="mt6">
            <div class="hint mb2">Grouped Bar — <b>rank only</b> (axes black, pastel fill; value on hover)</div>
            <div class="chart2"><svg id="mmc_bar" width="100%" height="100%"></svg></div>
          </div>

          <div class="mt6">
            <div class="hint">Scatter (axes black, Pearson line)</div>
            <div class="row" style="gap:12px;align-items:center">
              <div class="hint">X:</div>
              <select id="mmc_x"><option>SYAI</option><option>TOPSIS</option><option>VIKOR</option><option>SAW</option><option>COBRA</option><option>WASPAS</option><option>MOORA</option></select>
              <div class="hint">Y:</div>
              <select id="mmc_y"><option>TOPSIS</option><option>SYAI</option><option>VIKOR</option><option>SAW</option><option>COBRA</option><option>WASPAS</option><option>MOORA</option></select>
            </div>
            <div class="chart2"><svg id="mmc_sc" width="100%" height="100%"></svg></div>
          </div>

          <div class="mt6">
            <div class="hint mb2">Correlation Heatmap — <b>Spearman</b> (soft blue palette with legend on right; value on hover)</div>
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
  const PASTELS = ["#cdeafe","#d5e8d4","#ffe6cc","#fbd5e7","#e3f2fd","#e8eaf6","#dcedc8","#ffecb3"]; // soft bar colors

  const sampleCSV = `Alternative,Cost,Quality,Delivery
A1,200,8,4
A2,250,7,5
A3,300,9,6
A4,220,8,4
A5,180,6,7
`;

  // sample link
  $("downloadSample").href = "data:text/csv;charset=utf-8,"+encodeURIComponent(sampleCSV);
  $("downloadSample").download = "sample.csv";

  // tab switching
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

  // CSV helpers
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

  // SAW utilities
  function sawUnit(vals, type="Benefit", goal=null){
    const max=Math.max(...vals), min=Math.min(...vals);
    if(type==="Benefit"){
      const M = max || 1; return vals.map(x=> (x)/(M||1));
    }
    if(type==="Cost"){
      const m = min || 1; return vals.map(x=> (m)/(x||1));
    }
    // Goal/Ideal
    const R=(max-min)||1;
    const g = isFinite(parseFloat(goal))? parseFloat(goal) : (min+max)/2;
    return vals.map(x=> Math.max(0, 1 - Math.abs(x-g)/R ));
  }

  // ======= TAB 1: SYAI =======
  let c1=[], r1=[], crit1=[], type1={}, ideal1={}, w1={}, wmode1='equal', beta1=0.5;
  $("beta1").oninput = ()=>{ beta1=parseFloat($("beta1").value); $("beta1v").textContent=beta1.toFixed(2); };
  $("w1eq").onchange = ()=>{ wmode1='equal'; $("wg1").style.display="none"; };
  $("w1c").onchange  = ()=>{ wmode1='custom'; $("wg1").style.display=""; };

  $("demo1").onclick = ()=> initSYAI(sampleCSV);
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
    const res = computeSYAI(r1, crit1, type1, ideal1, w1, wmode1, beta1)
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

  // ======= TAB 2: COMPARISON =======
  let c2=[], r2=[], crit2=[], type2={}, ideal2={}, w2={}, wmode2='equal';
  $("w2eq").onchange = ()=>{ wmode2='equal'; $("wg2").style.display="none"; };
  $("w2c").onchange  = ()=>{ wmode2='custom'; $("wg2").style.display=""; };

  $("demo2").onclick = ()=> initCmp(sampleCSV);
  $("csv2").onchange = (e)=>{ const f=e.target.files[0]; if(!f) return; const r=new FileReader(); r.onload=()=>initCmp(String(r.result)); r.readAsText(f); };
  $("runCmp").onclick = ()=> runComparison();

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

  // ------- shared renderers -------
  function renderMatrix(tid, cols, rows){
    const tb=$(tid); tb.innerHTML="";
    const thead=document.createElement("thead"); const trh=document.createElement("tr");
    cols.forEach(c=>{ const th=document.createElement("th"); th.textContent=c; trh.appendChild(th); });
    thead.appendChild(trh); tb.appendChild(thead);
    const tbody=document.createElement("tbody");
    // show ALL rows (no 10-row limit)
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
      const box=document.createElement("div");
      const lab=document.createElement("div"); lab.className="label"; lab.textContent="w("+c+")"; box.appendChild(lab);
      const inp=document.createElement("input"); inp.type="number"; inp.step="0.001"; inp.min="0"; inp.value=weights[c]??0;
      inp.oninput=()=> weights[c]=inp.value; box.appendChild(inp);
      wrap.appendChild(box);
    });
  }

  // ================= CORE COMPUTE (shared) =================
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

  // --------- SYAI core (FIXED: ideals from U; weights applied inside distance) ----------
  function computeSYAI(rows, crits, types, ideals, weights, wmode, beta){
    const U = computeU(rows, crits, types, ideals);
    const w = computeWeights(crits, weights, wmode);

    // ideals computed in normalized U-space
    const Aplus={}, Aminus={};
    crits.forEach(c=>{
      const arr = U[c];
      Aplus[c]  = Math.max(...arr);
      Aminus[c] = Math.min(...arr);
    });

    return rows.map((r,i)=>{
      let Dp=0, Dm=0;
      crits.forEach(c=>{
        Dp += w[c]*Math.abs(U[c][i] - Aplus[c]);
        Dm += w[c]*Math.abs(U[c][i] - Aminus[c]);
      });
      const denom = beta*Dp + (1-beta)*Dm || Number.EPSILON;
      const Close = ((1-beta)*Dm)/denom;
      return { alt:String(r["Alternative"]), Dp, Dm, Close, Urow:Object.fromEntries(crits.map(c=>[c,U[c][i]])), w };
    });
  }

  function runComparison(){
    if(!r2.length) return;

    // SAW-space U and weights (one source of truth)
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
      return sumB - sumC;   // may be negative
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

    // ---------- SYAI (fixed) ----------
    const sy = computeSYAI(r2, crit2, type2, ideal2, w2, wmode2, 0.5);
    const SYAI = sy.map(o=> o.Close);

    // ---------- COBRA (FIXED: mean-centered SAW utilities; lower = better; can be negative) ----------
    const mu = Object.fromEntries(crit2.map(c=>{
      const avg = (U[c].reduce((s,v)=>s+v,0)/U[c].length);
      return [c, avg];
    }));
    const COBRA = r2.map((_,i)=> crit2.reduce((s,c)=> s + w[c]*(mu[c] - U[c][i]), 0));

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
    drawHeatSpearman({methods});  // soft palette + legend + hover
  }

  // ======== Tooltip helpers ========
  const TT = $("tt");
  function showTT(x,y,html){
    TT.style.display="block";
    TT.style.left = (x+12)+"px";
    TT.style.top  = (y+12)+"px";
    TT.innerHTML = html;
  }
  function hideTT(){ TT.style.display="none"; }

  // ======== Charts ========
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
    const padL=70,padR=20,padT=20,padB=60;
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
    const barW=(cell*0.8)/order.length;

    names.forEach((nm,i)=>{
      const x0=padL + i*cell + (cell - barW*order.length)/2;
      const lbl=document.createElementNS("http://www.w3.org/2000/svg","text");
      lbl.setAttribute("x",x0 + barW*order.length/2); lbl.setAttribute("y",H-8);
      lbl.setAttribute("text-anchor","middle"); lbl.setAttribute("font-size","12"); lbl.setAttribute("fill","#000"); lbl.textContent=nm; svg.appendChild(lbl);
      order.forEach((m,k)=>{
        const v=methods[m][i];
        const y=H-padB - (H-padT-padB)*((v-yMin)/range);
        const h=H-padB - y;
        const rect=document.createElementNS("http://www.w3.org/2000/svg","rect");
        rect.setAttribute("x",x0 + k*barW); rect.setAttribute("y",h>=0? y : H-padB);
        rect.setAttribute("width",barW-1.5); rect.setAttribute("height",Math.abs(h));
        rect.setAttribute("fill", PASTELS[k%PASTELS.length]);
        rect.addEventListener("mousemove",(ev)=> showTT(ev.clientX, ev.clientY, `<b>${m}</b> • ${nm}<br/>${v.toFixed(6)}`));
        rect.addEventListener("mouseleave", hideTT);
        svg.appendChild(rect);
      });
    });
  }

  // Scatter (Pearson)
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
      c.setAttribute("cx",sx(xs[i])); c.setAttribute("cy",sy(ys[i])); c.setAttribute("r","5"); c.setAttribute("fill","#6b7280");
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

  // Spearman heatmap (soft readable blues) + legend + hover
  function drawHeatSpearman(res){
    const methods=["TOPSIS","VIKOR","SAW","SYAI","COBRA","WASPAS","MOORA"];
    const svg=$("mmc_heat"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const W=(svg.getBoundingClientRect().width||900), H=(svg.getBoundingClientRect().height||480);
    svg.setAttribute("viewBox","0 0 "+W+" "+H);
    const padL=120, padR=60, padT=60, padB=80;
    const n=methods.length;

    // rank arrays
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

    // soft readable palette (white -> light blue -> deep blue)
    function colorFor(v){ // v in [-1,1]
      const t = (v+1)/2; // 0..1
      const r = Math.round(255*(1 - 0.4*t));
      const g = Math.round(255*(1 - 0.65*t));
      const b = Math.round(255*(1 - (1-t)*0.1));
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

    // cells (no static numbers; show value on hover)
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

    // ---- legend (color scale -1..1) on right ----
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
    // ticks
    [-1,-0.5,0,0.5,1].forEach(v=>{
      const y = Ly + (1-(v+1)/2)*Lh;
      const t=document.createElementNS("http://www.w3.org/2000/svg","text");
      t.setAttribute("x", Lx + Lw + 6); t.setAttribute("y", y+4); t.setAttribute("font-size","12"); t.setAttribute("fill","#000");
      t.textContent = v.toFixed(1); svg.appendChild(t);
    });
    const lh=document.createElementNS("http://www.w3.org/2000/svg","text");
    lh.setAttribute("x", Lx-2); lh.setAttribute("y", Ly-10); lh.setAttribute("text-anchor","end");
    lh.setAttribute("font-size","12"); lh.setAttribute("fill","#000"); lh.textContent="Spearman ρ"; svg.appendChild(lh);
  }

  // events
  $("mmc_x").onchange = ()=> runComparison();
  $("mmc_y").onchange = ()=> runComparison();

})();
</script>
</body>
</html>
"""

# inject placeholders (kept for future static images)
html = html.replace("SCATTER_DATA_URI", SCATTER_URI or "")
html = html.replace("CORR_DATA_URI", CORR_URI or "")
html = html.replace("HAS_SCATTER_FLAG", "1" if SCATTER_FOUND else "0")
html = html.replace("HAS_CORR_FLAG", "1" if CORR_FOUND else "0")

components.html(html, height=4000, scrolling=True)
