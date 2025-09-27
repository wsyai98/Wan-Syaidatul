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
    --bg-dark:#0b0b0f; --bg-light:#f8fafc;
    --grad-light:#ffe4e6;
    --card-dark:#0f1115cc; --card-light:#ffffffcc;
    --text-light:#f5f5f5;
    --pink:#ec4899; --pink-700:#db2777;
    --border-dark:#262b35; --border-light:#fbcfe8;
  }
  *{box-sizing:border-box} html,body{height:100%;margin:0}
  body{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Ubuntu,Cantarell,"Noto Sans","Helvetica Neue",Arial}
  body.theme-dark{ color:var(--text-light);
    background:linear-gradient(180deg,#0b0b0f 0%,#0b0b0f 35%,var(--grad-light) 120%); }
  body.theme-light{ color:#111;
    background:linear-gradient(180deg,#f8fafc 0%,#f8fafc 40%,var(--grad-light) 120%); }

  .container{max-width:1200px;margin:24px auto;padding:0 16px}
  .header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
  .title{font-weight:800;font-size:28px;color:#fce7f3}
  body.theme-light .title{color:#000 !important;}

  .row{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
  .btn{display:inline-flex;align-items:center;gap:8px;padding:10px 14px;border-radius:12px;border:1px solid var(--pink-700);background:var(--pink);color:#fff;cursor:pointer}
  .btn:hover{background:var(--pink-700)}
  .toggle{padding:8px 12px;border-radius:12px;border:1px solid #333;background:#111;color:#eee;cursor:pointer}
  body.theme-light .toggle{background:#fff;color:#111;border-color:#cbd5e1}

  .tabs{display:flex;gap:8px;margin:12px 0;flex-wrap:wrap}
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

  .grid2{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}
</style>
</head>
<body class="theme-dark">
<div class="container">
  <div id="err" style="display:none;background:#7f1d1d;color:#fff;padding:10px 12px;border:1px solid #fecaca;border-radius:8px;margin-bottom:8px"></div>

  <div class="header">
    <div class="title">SYAI-Rank</div>
    <div class="row">
      <button class="toggle" id="themeToggle">🌙 Dark</button>
    </div>
  </div>

  <div class="tabs">
    <button class="tab active" id="tabRunCompare">Run Multi-Method Comparison</button>
  </div>

  <div id="viewRunCompare">
    <div class="grid">
      <div>
        <div class="card dark">
          <div class="section-title">Step A: Upload CSV</div>
          <label for="cmpCsvFile" class="btn">📤 Choose CSV</label>
          <input id="cmpCsvFile" type="file" accept=".csv" style="display:none"/>
          <button class="btn mt2" id="cmpDemoBtn">📄 Load Demo CSV</button>
          <p class="hint mt2">First column is <b>Alternative</b>. Others are criteria.</p>
        </div>

        <div id="cmpTypesCard" class="card dark" style="display:none">
          <div class="section-title">Step B: Criteria Types</div>
          <div id="cmpTypesGrid" class="grid2"></div>
        </div>

        <div id="cmpWeightsCard" class="card dark" style="display:none">
          <div class="section-title">Step C: Weights</div>
          <div class="row mb2" style="gap:16px">
            <label><input type="radio" name="cmp_wmode" id="cmp_wEqual" checked> Equal (1/m)</label>
            <label><input type="radio" name="cmp_wmode" id="cmp_wCustom"> Custom (raw; normalized)</label>
          </div>
          <div id="cmpWeightsGrid" class="grid2" style="display:none"></div>
        </div>

        <div class="card dark">
          <div class="section-title">Step D: Run</div>
          <button class="btn" id="cmpRunBtn">▶️ Run Comparison</button>
        </div>
      </div>

      <div>
        <div id="cmpMatrixCard" class="card" style="display:none">
          <div class="section-title">Decision Matrix (first 10 rows)</div>
          <div class="table-wrap"><table id="cmpMatrixTable"></table></div>
        </div>

        <div id="cmpResultCard" class="card" style="display:none">
          <div class="section-title">Scores & Ranks</div>
          <div class="table-wrap"><table id="mmc_table"></table></div>

          <div class="mt6">
            <div class="row" style="gap:12px;align-items:center">
              <div class="hint">Scatter X:</div>
              <select id="mmc_x">
                <option>SYAI</option><option>TOPSIS</option><option>VIKOR</option>
                <option>SAW</option><option>COBRA</option><option>WASPAS</option><option>MOORA</option>
              </select>
              <div class="hint">Scatter Y:</div>
              <select id="mmc_y">
                <option>TOPSIS</option><option>SYAI</option><option>VIKOR</option>
                <option>SAW</option><option>COBRA</option><option>WASPAS</option><option>MOORA</option>
              </select>
            </div>

            <div class="mt4">
              <div class="hint mb2">Grouped Bar — <b>rank only</b></div>
              <div class="chart2"><svg id="mmc_bar" width="100%" height="100%"></svg></div>
            </div>

            <div class="mt6">
              <div class="hint mb2">Method vs Method — Scatter with correlation</div>
              <div class="chart2"><svg id="mmc_scatter" width="100%" height="100%"></svg></div>
            </div>

            <div class="mt6">
              <div class="hint mb2">Correlation Heatmap — Pearson r and p-values</div>
              <div class="chart2" style="height:460px"><svg id="mmc_heat" width="100%" height="100%"></svg></div>
              <div class="hint mt2">Darker = stronger | p shown below r (two-tailed).</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

<script>
(function(){
  const $ = (id)=> document.getElementById(id);
  const show = (el, on=true)=> { el.style.display = on ? "" : "none"; };
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

  // static images (not used here but kept wired)
  const SCATTER_URI = "SCATTER_DATA_URI";
  const CORR_URI    = "CORR_DATA_URI";
  const HAS_SCATTER = "HAS_SCATTER_FLAG" === "1";
  const HAS_CORR    = "HAS_CORR_FLAG" === "1";

  // CSV helpers
  function parseCSVText(text){
    const rows = []; let i=0, cur="", inQuotes=false, row=[];
    const pushCell=()=>{ row.push(cur); cur=""; };
    const pushRow=()=>{ rows.push(row); row=[]; };
    while(i<text.length){
      const ch=text[i];
      if(inQuotes){
        if(ch==='\"'){ if(text[i+1]==='\"'){ cur+='\"'; i++; } else { inQuotes=false; } }
        else { cur+=ch; }
      }else{
        if(ch==='\"') inQuotes=true;
        else if(ch===',') pushCell();
        else if(ch==='\n'){ pushCell(); pushRow(); }
        else if(ch==='\r'){ }
        else cur+=ch;
      }
      i++;
    }
    pushCell(); if(row.length>1 || row[0] !== "") pushRow();
    return rows;
  }
  const toNum=(v)=>{ const x=parseFloat(String(v).replace(/,/g,"")); return isFinite(x)?x:NaN; };

  // state
  let cmp_columns=[], cmp_rows=[], cmp_crits=[];
  let cmp_types={}, cmp_ideals={}, cmp_weights={}, cmp_wmode='equal';

  function cmp_initFromCSV(txt){
    const arr=parseCSVText(txt); if(!arr.length) return;
    cmp_columns = arr[0].map(x=> String(x??"").trim());
    if(cmp_columns[0] !== "Alternative"){
      const idx = cmp_columns.indexOf("Alternative");
      if(idx>0){ const nm=cmp_columns.splice(idx,1)[0]; cmp_columns.unshift(nm); }
      else { cmp_columns[0]="Alternative"; }
    }
    cmp_crits=cmp_columns.slice(1);
    cmp_rows = arr.slice(1).filter(r=>r.length>=cmp_columns.length).map(r=>{
      const o={}; cmp_columns.forEach((c,i)=> o[c]=r[i]); return o;
    });

    cmp_types  = Object.fromEntries(cmp_crits.map(c=>[c,"Benefit"]));
    cmp_ideals = Object.fromEntries(cmp_crits.map(c=>[c,""]));
    cmp_weights= Object.fromEntries(cmp_crits.map(c=>[c,1]));

    cmp_renderMatrix(); cmp_renderTypes(); cmp_renderWeights();
    show($("cmpMatrixCard"), true);
    show($("cmpTypesCard"), true);
    show($("cmpWeightsCard"), true);
    show($("cmpResultCard"), false);
  }

  function cmp_renderMatrix(){
    const tb = $("cmpMatrixTable"); tb.innerHTML="";
    const thead = document.createElement("thead"); const trh = document.createElement("tr");
    cmp_columns.forEach(c=>{ const th=document.createElement("th"); th.textContent=c; trh.appendChild(th); });
    thead.appendChild(trh); tb.appendChild(thead);
    const tbody = document.createElement("tbody");
    cmp_rows.slice(0,10).forEach(r=>{
      const tr=document.createElement("tr");
      cmp_columns.forEach(c=>{ const td=document.createElement("td"); td.textContent=String(r[c]??""); tr.appendChild(td); });
      tbody.appendChild(tr);
    });
    tb.appendChild(tbody);
  }

  function cmp_renderTypes(){
    const wrap=$("cmpTypesGrid"); wrap.innerHTML="";
    cmp_crits.forEach(c=>{
      const box=document.createElement("div");
      const lab=document.createElement("div"); lab.className="label"; lab.textContent=c; box.appendChild(lab);
      const sel=document.createElement("select");
      ["Benefit","Cost","Ideal (Goal)"].forEach(v=>{ const o=document.createElement("option"); o.textContent=v; sel.appendChild(o); });
      sel.value = cmp_types[c]||"Benefit";
      sel.onchange = ()=>{ cmp_types[c]=sel.value; cmp_renderTypes(); };
      box.appendChild(sel);
      if((cmp_types[c]||"")==="Ideal (Goal)"){
        const inp=document.createElement("input"); inp.className="mt2"; inp.type="number"; inp.step="any"; inp.placeholder="Goal";
        inp.value=cmp_ideals[c]||""; inp.oninput=()=> cmp_ideals[c]=inp.value; box.appendChild(inp);
      }else{ delete cmp_ideals[c]; }
      wrap.appendChild(box);
    });
  }

  function cmp_renderWeights(){
    const wrap=$("cmpWeightsGrid"); wrap.innerHTML="";
    cmp_crits.forEach(c=>{
      const box=document.createElement("div");
      const lab=document.createElement("div"); lab.className="label"; lab.textContent=`w(${c})`; box.appendChild(lab);
      const inp=document.createElement("input"); inp.type="number"; inp.step="0.001"; inp.min="0"; inp.value=cmp_weights[c]??0;
      inp.oninput=()=> cmp_weights[c]=inp.value; box.appendChild(inp);
      wrap.appendChild(box);
    });
  }
  $("cmp_wEqual").onchange = ()=>{ cmp_wmode='equal'; $("cmpWeightsGrid").style.display="none"; };
  $("cmp_wCustom").onchange = ()=>{ cmp_wmode='custom'; $("cmpWeightsGrid").style.display=""; };

  $("cmpCsvFile").onchange = (e)=>{
    const f = e.target.files[0]; if(!f) return;
    const r = new FileReader();
    r.onload = ()=> cmp_initFromCSV(String(r.result));
    r.readAsText(f);
  };
  const demoCSV = `Alternative,Cost,Quality,Delivery
A1,200,8,4
A2,250,7,5
A3,300,9,6
A4,220,8,4
A5,180,6,7`;
  $("cmpDemoBtn").onclick = ()=> cmp_initFromCSV(demoCSV);

  // math helpers
  function vec(vals){ return vals.map(x=> (isFinite(x)? x : 0)); }
  function vectorNorm(vals){ const d=Math.sqrt(vals.reduce((s,v)=>s+(v*v),0))||1; return vals.map(v=>v/d); }

  // SAW-style normalization (paper): benefit = x/max; cost = min/x; goal = distance-to-goal utility in [0,1]
  function sawUnit(vals, type="Benefit", goal=null){
    const max=Math.max(...vals), min=Math.min(...vals);
    if(type==="Benefit"){ const M=max||1; return vals.map(x=> x/(M)); }
    if(type==="Cost"){ const m=min||1; return vals.map(x=> (m)/(x||1)); }
    // Ideal(Goal)
    const R=(max-min)||1; const g = isFinite(parseFloat(goal))? parseFloat(goal):(min+max)/2;
    return vals.map(x=> Math.max(0,1-Math.abs(x-g)/R));
  }

  // ============ CORE COMPUTE ============
  function computeAll(){
    if(!cmp_rows.length) return null;
    const X = cmp_rows.map(r=> Object.fromEntries(cmp_crits.map(c=>[c, toNum(r[c])])) );

    // weights
    const w={};
    if(cmp_wmode==='equal'){ cmp_crits.forEach(c=> w[c]=1/cmp_crits.length); }
    else {
      let sum=0; cmp_crits.forEach(c=>{ const v=Math.max(0,parseFloat(cmp_weights[c]||0)); w[c]=isFinite(v)?v:0; sum+=w[c]; });
      if(sum<=0) cmp_crits.forEach(c=> w[c]=1/cmp_crits.length); else cmp_crits.forEach(c=> w[c]/=sum);
    }

    // SAW utilities (unitized as defined above)
    const U = {};
    cmp_crits.forEach(c=>{
      const vals = vec(X.map(r=>r[c]));
      U[c] = sawUnit(vals, cmp_types[c], cmp_ideals[c]);
    });

    // ---------- SAW ----------
    const SAW = X.map((_,i)=> cmp_crits.reduce((s,c)=> s + w[c]*U[c][i], 0));

    // ---------- WASPAS (WSM + WPM, both from SAW unitization) ----------
    const WSM = SAW.slice();
    const WPM = X.map((_,i)=> cmp_crits.reduce((p,c)=> p * Math.pow(Math.max(U[c][i],1e-12), w[c]), 1));
    const WASPAS = X.map((_,i)=> 0.5*WSM[i] + 0.5*WPM[i]);

    // ---------- MOORA (vector norm; benefit-cost difference; goal treated as [0,1] utility) ----------
    const N_vec = {};
    cmp_crits.forEach(c=>{
      const vals = vec(X.map(r=>r[c]));
      if((cmp_types[c]||"Benefit")==="Ideal (Goal)") {
        N_vec[c] = sawUnit(vals, "Ideal (Goal)", cmp_ideals[c]); // [0,1]
      } else {
        N_vec[c] = vectorNorm(vals);
      }
    });
    const MOORA = X.map((_,i)=>{
      let sumB=0, sumC=0;
      cmp_crits.forEach(c=>{
        if((cmp_types[c]||"Benefit")==="Cost") sumC += w[c]*N_vec[c][i];
        else sumB += w[c]*N_vec[c][i];
      });
      return sumB - sumC; // may be negative
    });

    // ---------- TOPSIS ----------
    const N_t = {};
    cmp_crits.forEach(c=>{ N_t[c] = vectorNorm(vec(X.map(r=>r[c]))); });
    const W_t = X.map((_,i)=> Object.fromEntries(cmp_crits.map(c=>[c, N_t[c][i]*w[c]])) );
    const Aplus={}, Aminus={};
    cmp_crits.forEach(c=>{
      const arr=W_t.map(r=>r[c]);
      if ((cmp_types[c]||"Benefit")==="Cost"){ Aplus[c]=Math.min(...arr); Aminus[c]=Math.max(...arr); }
      else { Aplus[c]=Math.max(...arr); Aminus[c]=Math.min(...arr); }
    });
    const TOPSIS = X.map((_,i)=>{
      let dp=0, dm=0;
      cmp_crits.forEach(c=>{ const v=W_t[i][c]; dp+=(v-Aplus[c])**2; dm+=(v-Aminus[c])**2; });
      dp=Math.sqrt(dp); dm=Math.sqrt(dm);
      return dm/(dp+dm); // higher better
    });

    // ---------- SYAI (beta=0.5 on SAW-unit space) ----------
    const W_sy = X.map((_,i)=> Object.fromEntries(cmp_crits.map(c=>[c, U[c][i]*w[c]])) );
    const Aplus_sy={}, Aminus_sy={};
    cmp_crits.forEach(c=>{
      const arr=W_sy.map(r=>r[c]); Aplus_sy[c]=Math.max(...arr); Aminus_sy[c]=Math.min(...arr);
    });
    const betaSY=0.5;
    const SYAI = X.map((_,i)=>{
      let Dp=0, Dm=0;
      cmp_crits.forEach(c=>{ const v=W_sy[i][c]; Dp+=Math.abs(v-Aplus_sy[c]); Dm+=Math.abs(v-Aminus_sy[c]); });
      const denom = betaSY*Dp + (1-betaSY)*Dm || Number.EPSILON;
      return ((1-betaSY)*Dm)/denom;
    });

    // ---------- VIKOR (raw Q, lower better) ----------
    const fStar={}, fMin={};
    cmp_crits.forEach(c=>{
      const vals=X.map(r=>r[c]);
      if ((cmp_types[c]||"Benefit")==="Cost"){ fStar[c]=Math.min(...vals); fMin[c]=Math.max(...vals); }
      else { fStar[c]=Math.max(...vals); fMin[c]=Math.min(...vals); }
    });
    const S = X.map(r=> cmp_crits.reduce((s,c)=> {
      const denom = Math.abs(fStar[c]-fMin[c]) || 1;
      const term = ((cmp_types[c]||"Benefit")==="Cost") ?
        ((r[c]-fStar[c])/(fMin[c]-fStar[c] || 1)) :
        ((fStar[c]-r[c])/denom);
      return s + w[c]*term;
    }, 0));
    const R = X.map(r=> Math.max(...cmp_crits.map(c=>{
      const denom = Math.abs(fStar[c]-fMin[c]) || 1;
      const term = ((cmp_types[c]||"Benefit")==="Cost") ?
        ((r[c]-fStar[c])/(fMin[c]-fStar[c] || 1)) :
        ((fStar[c]-r[c])/denom);
      return w[c]*term;
    })));
    const Smin=Math.min(...S), Smax=Math.max(...S), Rmin=Math.min(...R), Rmax=Math.max(...R);
    const v=0.5;
    const VIKOR = X.map((_,i)=> v*((S[i]-Smin)/((Smax-Smin)||1)) + (1-v)*((R[i]-Rmin)/((Rmax-Rmin)||1)) ); // lower better

    // ---------- COBRA (distance to ideal in SAW-unit space; lower better) ----------
    const COBRA = X.map((_,i)=>{
      let diPlus=0;
      cmp_crits.forEach(c=>{
        const z=U[c][i]; // [0,1]
        diPlus  += w[c]*(1 - z)**2; // distance to ideal (1)
      });
      return Math.sqrt(diPlus); // lower is better
    });

    // ranks
    function ranksHigherBetter(arr){
      const idx=arr.map((v,i)=>({v,i})).sort((a,b)=> b.v-a.v);
      const rk=new Array(arr.length); idx.forEach((o,k)=> rk[o.i]=k+1); return rk;
    }
    function ranksLowerBetter(arr){
      const idx=arr.map((v,i)=>({v,i})).sort((a,b)=> a.v-b.v);
      const rk=new Array(arr.length); idx.forEach((o,k)=> rk[o.i]=k+1); return rk;
    }

    const ranks = {
      TOPSIS: ranksHigherBetter(TOPSIS),
      VIKOR:  ranksLowerBetter(VIKOR),
      SAW:    ranksHigherBetter(SAW),
      SYAI:   ranksHigherBetter(SYAI),
      COBRA:  ranksLowerBetter(COBRA),  // <-- as requested: less is better
      WASPAS: ranksHigherBetter(WASPAS),
      MOORA:  ranksHigherBetter(MOORA),
    };

    return { methods:{TOPSIS,VIKOR,SAW,SYAI,COBRA,WASPAS,MOORA}, ranks };
  }

  // ---------- UI RENDER ----------
  const COLORS=["#a5b4fc","#f9a8d4","#bae6fd","#bbf7d0","#fde68a","#c7d2fe","#fecdd3","#fbcfe8","#bfdbfe","#d1fae5","#ddd6fe","#fdba74"];
  const methodsOrder=["TOPSIS","VIKOR","SAW","SYAI","COBRA","WASPAS","MOORA"];

  function renderCmpTable(res){
    const tb=$("mmc_table"); tb.innerHTML="";
    const thead=document.createElement("thead"); const trh=document.createElement("tr");
    ["Alternative"].concat(methodsOrder).forEach(h=>{ const th=document.createElement("th"); th.textContent=h; trh.appendChild(th); });
    thead.appendChild(trh); tb.appendChild(thead);

    const tbody=document.createElement("tbody");
    cmp_rows.forEach((r,i)=>{
      const tr=document.createElement("tr");
      const t0=document.createElement("td"); t0.textContent=String(r["Alternative"]); tr.appendChild(t0);
      methodsOrder.forEach(m=>{
        const td=document.createElement("td");
        td.textContent = `${res.methods[m][i].toFixed(4)} (${res.ranks[m][i]})`;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    tb.appendChild(tbody);
  }

  // BAR: rank-only labels, black axes
  function drawCmpBars(res){
    const svg=$("mmc_bar"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const rect=svg.getBoundingClientRect(); const W=rect.width||900, H=rect.height||360;
    svg.setAttribute("viewBox",`0 0 ${W} ${H}`);
    const padL=70,padR=20,padT=20,padB=60;

    const data = cmp_rows.map((r,i)=> ({
      name:String(r["Alternative"]),
      vals:methodsOrder.map(m=> res.methods[m][i]),
      ranks:methodsOrder.map(m=> res.ranks[m][i])
    }));
    const allVals = data.flatMap(d=>d.vals);
    const max=Math.max(...allVals), min=Math.min(...allVals);
    const yMin=Math.min(min,0), yMax=Math.max(max,0), range=(yMax-yMin)||1;
    const cell=(W-padL-padR)/data.length; const barW = (cell*0.8)/methodsOrder.length;

    // axes
    const yAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    yAxis.setAttribute("x1",padL); yAxis.setAttribute("x2",padL); yAxis.setAttribute("y1",padT); yAxis.setAttribute("y2",H-padB); yAxis.setAttribute("stroke","#000");
    svg.appendChild(yAxis);
    const xAxis=document.createElementNS("http://www.w3.org/2000/svg","line");
    xAxis.setAttribute("x1",padL); xAxis.setAttribute("x2",W-padR); xAxis.setAttribute("y1",H-padB); xAxis.setAttribute("y2",H-padB); xAxis.setAttribute("stroke","#000");
    svg.appendChild(xAxis);

    for(let t=0;t<=5;t++){
      const val=yMin + range*t/5;
      const y=H-padB - (H-padT-padB)*((val-yMin)/range);
      const gl=document.createElementNS("http://www.w3.org/2000/svg","line");
      gl.setAttribute("x1",padL); gl.setAttribute("x2",W-padR); gl.setAttribute("y1",y); gl.setAttribute("y2",y);
      gl.setAttribute("stroke","#000"); gl.setAttribute("stroke-dasharray","3 3"); svg.appendChild(gl);
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x",padL-10); tx.setAttribute("y",y+4); tx.setAttribute("text-anchor","end"); tx.setAttribute("font-size","12"); tx.setAttribute("fill","#000");
      tx.textContent=val.toFixed(2); svg.appendChild(tx);
    }

    data.forEach((d,i)=>{
      const x0=padL + i*cell + (cell - barW*methodsOrder.length)/2;
      const lbl=document.createElementNS("http://www.w3.org/2000/svg","text");
      lbl.setAttribute("x",x0 + barW*methodsOrder.length/2); lbl.setAttribute("y",H-8);
      lbl.setAttribute("text-anchor","middle"); lbl.setAttribute("font-size","12"); lbl.setAttribute("fill","#000"); lbl.textContent=d.name; svg.appendChild(lbl);

      d.vals.forEach((v,k)=>{
        const x=x0 + k*barW;
        const y=H-padB - (H-padT-padB)*((v-yMin)/range);
        const h=H-padB - y;
        const rect=document.createElementNS("http://www.w3.org/2000/svg","rect");
        rect.setAttribute("x",x); rect.setAttribute("y", h>=0? y : H-padB);
        rect.setAttribute("width",barW-1.5); rect.setAttribute("height",Math.abs(h));
        rect.setAttribute("fill", COLORS[k%COLORS.length]);
        svg.appendChild(rect);

        // label: (rank) ONLY
        const tVal=document.createElementNS("http://www.w3.org/2000/svg","text");
        tVal.setAttribute("x",x+(barW-1.5)/2); tVal.setAttribute("y", (h>=0? y : H-padB)-4);
        tVal.setAttribute("text-anchor","middle"); tVal.setAttribute("font-size","11"); tVal.setAttribute("fill","#000");
        tVal.textContent = `(${d.ranks[k]})`;
        svg.appendChild(tVal);
      });
    });

    // legend
    methodsOrder.forEach((m,i)=>{
      const y=padT+14 + i*16, x=W-padR-140;
      const sw=document.createElementNS("http://www.w3.org/2000/svg","rect");
      sw.setAttribute("x",x); sw.setAttribute("y",y-10); sw.setAttribute("width",12); sw.setAttribute("height",12); sw.setAttribute("fill",COLORS[i%COLORS.length]);
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x",x+18); tx.setAttribute("y",y); tx.setAttribute("font-size","12"); tx.setAttribute("fill","#000"); tx.textContent=m;
      svg.appendChild(sw); svg.appendChild(tx);
    });
  }

  // Pearson r & p-value helpers (t-CDF via regularized incomplete beta)
  function betacf(a,b,x){
    const MAXIT=200, EPS=3e-7, FPMIN=1e-30;
    let qab=a+b, qap=a+1, qam=a-1;
    let c=1, d=1-(qab*x/qap);
    if (Math.abs(d)<FPMIN) d=FPMIN; d=1/d; let h=d;
    for(let m=1, m2=2; m<=MAXIT; m++, m2+=2){
      let aa = m*(b-m)*x/((qam+m2)*(a+m2));
      d = 1+aa*d; if(Math.abs(d)<FPMIN) d=FPMIN; c = 1+aa/c; if(Math.abs(c)<FPMIN) c=FPMIN; d=1/d; h*=d*c;
      aa = -(a+m)*(qab+m)*x/((a+m2)*(qap+m2));
      d = 1+aa*d; if(Math.abs(d)<FPMIN) d=FPMIN; c = 1+aa/c; if(Math.abs(c)<FPMIN) c=FPMIN; d=1/d; let del=d*c; h*=del;
      if(Math.abs(del-1) < EPS) break;
    }
    return h;
  }
  function betai(a,b,x){
    if (x<=0) return 0; if (x>=1) return 1;
    const bt = Math.exp( (a*Math.log(x)) + (b*Math.log(1-x)) - Math.logBeta(a,b) );
    let result;
    if (x < (a+1)/(a+b+2)) result = bt*betacf(a,b,x)/a;
    else result = 1 - bt*betacf(b,a,1-x)/b;
    return result;
  }
  Math.logGamma = function(z){ // Lanczos
    const g=7, p=[0.99999999999980993,676.5203681218851,-1259.1392167224028,771.32342877765313,-176.61502916214059,12.507343278686905,-0.13857109526572012,9.9843695780195716e-6,1.5056327351493116e-7];
    if(z<0.5) return Math.log(Math.PI) - Math.log(Math.sin(Math.PI*z)) - Math.logGamma(1-z);
    z-=1; let x=p[0]; for(let i=1;i<g+2;i++) x+=p[i]/(z+i);
    const t=z+g+0.5; return 0.5*Math.log(2*Math.PI)+(z+0.5)*Math.log(t)-t+Math.log(x)-Math.log(z+1);
  }
  Math.logBeta = function(a,b){ return Math.logGamma(a)+Math.logGamma(b)-Math.logGamma(a+b); }

  function tCDF(t, df){ // two-sided helper uses symmetry
    const x = df/(df + t*t);
    const a = df/2, b = 0.5;
    const ib = betai(a,b,x); // regularized incomplete beta
    return t>0 ? 1 - 0.5*ib : 0.5*ib;
  }
  function pearsonPval(r,n){
    const df=n-2; if(df<=0) return 1;
    const t = Math.abs(r)*Math.sqrt(df/(1-r*r+1e-12));
    const p = 2*(1 - tCDF(t, df));
    return Math.max(0, Math.min(1, p));
  }

  function drawHeatmap(res){
    const svg=$("mmc_heat"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const rect=svg.getBoundingClientRect(); const W=rect.width||900, H=rect.height||460;
    svg.setAttribute("viewBox",`0 0 ${W} ${H}`);
    const padL=110, padR=20, padT=40, padB=80;

    const methods = methodsOrder;
    const nA = cmp_rows.length;

    // build matrix r & p
    const mat = methods.map(m => res.methods[m]);
    function corr(i,j){
      const xi = mat[i], yj = mat[j];
      const n = xi.length;
      const mx = xi.reduce((s,v)=>s+v,0)/n, my = yj.reduce((s,v)=>s+v,0)/n;
      let num=0, dx=0, dy=0;
      for(let k=0;k<n;k++){ const a=xi[k]-mx, b=yj[k]-my; num+=a*b; dx+=a*a; dy+=b*b; }
      const r = num/Math.sqrt((dx||1)*(dy||1));
      return {r, p: pearsonPval(r, n)};
    }
    const RP = methods.map((_,i)=> methods.map((_,j)=> corr(i,j)));

    const m = methods.length;
    const cellW=(W-padL-padR)/m, cellH=(H-padT-padB)/m;

    // color scale (dark = strong)
    function colorFor(r){
      const v=Math.abs(r); // 0..1
      const x=Math.floor(255*(1-v));
      return `rgb(${x},${x},${255})`; // dark navy for |r|~1
    }

    // grid & labels
    for(let i=0;i<m;i++){
      const lx=document.createElementNS("http://www.w3.org/2000/svg","text");
      lx.setAttribute("x", padL + i*cellW + cellW/2);
      lx.setAttribute("y", padT-10);
      lx.setAttribute("transform", `rotate(-45 ${padL + i*cellW + cellW/2} ${padT-10})`);
      lx.setAttribute("text-anchor","end"); lx.setAttribute("font-size","12"); lx.setAttribute("fill","#000");
      lx.textContent=methods[i]; svg.appendChild(lx);

      const ly=document.createElementNS("http://www.w3.org/2000/svg","text");
      ly.setAttribute("x", padL-10); ly.setAttribute("y", padT + i*cellH + cellH/2 + 4);
      ly.setAttribute("text-anchor","end"); ly.setAttribute("font-size","12"); ly.setAttribute("fill","#000");
      ly.textContent=methods[i]; svg.appendChild(ly);
    }

    // cells
    for(let i=0;i<m;i++){
      for(let j=0;j<m;j++){
        const {r,p} = RP[i][j];
        const x=padL + j*cellW, y=padT + i*cellH;
        const rectEl=document.createElementNS("http://www.w3.org/2000/svg","rect");
        rectEl.setAttribute("x",x); rectEl.setAttribute("y",y); rectEl.setAttribute("width",cellW-1); rectEl.setAttribute("height",cellH-1);
        rectEl.setAttribute("fill", colorFor(r));
        rectEl.setAttribute("stroke","#000"); rectEl.setAttribute("stroke-width","0.3");
        svg.appendChild(rectEl);

        const t1=document.createElementNS("http://www.w3.org/2000/svg","text");
        t1.setAttribute("x",x+cellW/2); t1.setAttribute("y",y+cellH/2-2);
        t1.setAttribute("text-anchor","middle"); t1.setAttribute("font-size","12"); t1.setAttribute("fill","#000");
        t1.textContent=r.toFixed(3); svg.appendChild(t1);

        const t2=document.createElementNS("http://www.w3.org/2000/svg","text");
        t2.setAttribute("x",x+cellW/2); t2.setAttribute("y",y+cellH/2+14);
        t2.setAttribute("text-anchor","middle"); t2.setAttribute("font-size","11"); t2.setAttribute("fill","#000");
        t2.textContent=`p=${p.toExponential(2)}`; svg.appendChild(t2);
      }
    }
  }

  // scatter (unchanged, axes black + r line)
  function mean(a){ return a.reduce((s,v)=>s+v,0)/a.length; }
  function drawCmpScatter(res){
    const svg=$("mmc_scatter"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const rect=svg.getBoundingClientRect(); const W=rect.width||900, H=rect.height||360;
    svg.setAttribute("viewBox",`0 0 ${W} ${H}`);
    const padL=60,padR=20,padT=20,padB=50;

    const mx=$("mmc_x").value, my=$("mmc_y").value;
    const xs=res.methods[mx], ys=res.methods[my];

    const Xmin=Math.min(...xs), Xmax=Math.max(...xs), Ymin=Math.min(...ys), Ymax=Math.max(...ys);
    const sx=(x)=> padL + (W-padL-padR)*((x - Xmin)/((Xmax-Xmin)||1));
    const sy=(y)=> H-padB - (H-padT-padB)*((y - Ymin)/((Ymax-Ymin)||1));

    const ax=document.createElementNS("http://www.w3.org/2000/svg","line"); ax.setAttribute("x1",padL); ax.setAttribute("x2",padL); ax.setAttribute("y1",padT); ax.setAttribute("y2",H-padB); ax.setAttribute("stroke","#000");
    const ay=document.createElementNS("http://www.w3.org/2000/svg","line"); ay.setAttribute("x1",padL); ay.setAttribute("x2",W-padR); ay.setAttribute("y1",H-padB); ay.setAttribute("y2",H-padB); ay.setAttribute("stroke","#000");
    svg.appendChild(ax); svg.appendChild(ay);
    for(let t=0;t<=5;t++){
      const vx=Xmin+(Xmax-Xmin)*t/5, vy=Ymin+(Ymax-Ymin)*t/5;
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x",sx(vx)); tx.setAttribute("y",H-padB+16); tx.setAttribute("text-anchor","middle"); tx.setAttribute("font-size","12"); tx.setAttribute("fill","#000"); tx.textContent=vx.toFixed(2);
      const ty=document.createElementNS("http://www.w3.org/2000/svg","text");
      ty.setAttribute("x",padL-8); ty.setAttribute("y",sy(vy)+4); ty.setAttribute("text-anchor","end"); ty.setAttribute("font-size","12"); ty.setAttribute("fill","#000"); ty.textContent=vy.toFixed(2);
      svg.appendChild(tx); svg.appendChild(ty);
    }

    cmp_rows.forEach((r,i)=>{
      const cx=sx(xs[i]), cy=sy(ys[i]);
      const c=document.createElementNS("http://www.w3.org/2000/svg","circle");
      c.setAttribute("cx",cx); c.setAttribute("cy",cy); c.setAttribute("r","5"); c.setAttribute("fill",COLORS[i%COLORS.length]);
      svg.appendChild(c);
      const lb=document.createElementNS("http://www.w3.org/2000/svg","text");
      lb.setAttribute("x",cx+6); lb.setAttribute("y",cy-6); lb.setAttribute("font-size","12"); lb.setAttribute("fill","#000"); lb.textContent=String(r["Alternative"]);
      svg.appendChild(lb);
    });

    const mxv=mean(xs), myv=mean(ys);
    let num=0, dx=0, dy=0;
    for(let i=0;i<xs.length;i++){ const a=xs[i]-mxv, b=ys[i]-myv; num+=a*b; dx+=a*a; dy+=b*b; }
    const r = num/Math.sqrt((dx||1)*(dy||1));
    const b = num/(dx||1);
    const a = myv - b*mxv;
    const line=document.createElementNS("http://www.w3.org/2000/svg","line");
    line.setAttribute("x1",padL); line.setAttribute("y1",sy(a+b*Xmin));
    line.setAttribute("x2",W-padR); line.setAttribute("y2",sy(a+b*Xmax));
    line.setAttribute("stroke","#000"); line.setAttribute("stroke-width","2"); svg.appendChild(line);

    const cap=document.createElementNS("http://www.w3.org/2000/svg","text");
    cap.setAttribute("x", (padL+W-padR)/2 ); cap.setAttribute("y",padT+14);
    cap.setAttribute("text-anchor","middle"); cap.setAttribute("font-size","12"); cap.setAttribute("fill","#000");
    cap.textContent=`Pearson r = ${r.toFixed(3)}`;
    svg.appendChild(cap);
  }

  function runComparison(){
    const res=computeAll(); if(!res) return;
    renderCmpTable(res);
    drawCmpBars(res);
    drawCmpScatter(res);
    drawHeatmap(res);
    show($("cmpResultCard"), true);
  }

  $("cmpRunBtn").onclick = ()=> runComparison();
  $("mmc_x").onchange = ()=> { const res=computeAll(); if(res) drawCmpScatter(res); };
  $("mmc_y").onchange = ()=> { const res=computeAll(); if(res) drawCmpScatter(res); };

})();
</script>
</body>
</html>
"""

# Inject image URIs (in case you also use the static image tab later)
html = html.replace("SCATTER_DATA_URI", SCATTER_URI or "")
html = html.replace("CORR_DATA_URI", CORR_URI or "")
html = html.replace("HAS_SCATTER_FLAG", "1" if SCATTER_FOUND else "0")
html = html.replace("HAS_CORR_FLAG", "1" if CORR_FOUND else "0")

components.html(html, height=3600, scrolling=True)
