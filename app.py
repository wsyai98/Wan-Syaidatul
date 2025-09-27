import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SYAI-Rank", layout="wide")

# ---------- Robust image loader ----------
APP_DIR = Path(__file__).resolve().parent

def img_data_uri_try(candidates: list[str]) -> tuple[str, bool]:
    """
    Try multiple candidate paths (relative to app.py unless absolute).
    Returns: (data_uri_or_empty, found_bool)
    """
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

# Try repo root first, then assets/
SCATTER_URI, SCATTER_FOUND = img_data_uri_try(
    ["scatter_matrix.png", "assets/scatter_matrix.png"]
)
CORR_URI, CORR_FOUND = img_data_uri_try(
    ["corr_matrix.png", "assets/corr_matrix.png"]
)

# Soft background polish
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #0b0b0f 0%, #0b0b0f 35%, #ffe4e6 120%) !important; }
[data-testid="stSidebar"] { background: rgba(255, 228, 230, 0.08) !important; backdrop-filter: blur(6px); }
</style>
""", unsafe_allow_html=True)

# ---------- Main embedded UI (YOUR ORIGINAL CODE; UNCHANGED) ----------
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

  /* Comparison view */
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

  <!-- ================== RANKING VIEW ================== -->
  <div id="viewRank">
    <div class="grid">
      <!-- LEFT -->
      <div>
        <div class="card dark">
          <div class="section-title step">Step 1: Upload Decision Matrix</div>
          <label for="csvFile" class="btn">📤 Choose CSV</label>
          <input id="csvFile" type="file" accept=".csv" style="display:none"/>
          <p class="hint mt2">First column is treated as <b>Alternative</b> automatically.</p>
        </div>

        <div id="typesCard" class="card dark" style="display:none">
          <div class="section-title step">Step 2: Define Criteria Types</div>
          <div id="typesGrid" class="row"></div>
        </div>

        <div id="weightsCard" class="card dark" style="display:none">
          <div class="section-title step">Step 3: Set Weights</div>
          <div class="row mb2" style="gap:16px">
            <label><input type="radio" name="wmode" id="wEqual" checked> Equal (1/m)</label>
            <label><input type="radio" name="wmode" id="wCustom"> Custom (raw; normalized on run)</label>
          </div>
          <div id="weightsGrid" class="row" style="display:none"></div>
        </div>

        <div id="betaCard" class="card dark" style="display:none">
          <div class="section-title step">Step 4: β (blend of D⁺ and D⁻)</div>
          <input id="beta" type="range" min="0" max="1" step="0.01" value="0.5" class="w100"/>
          <div class="hint mt2">β = <b id="betaVal">0.50</b></div>
          <button class="btn mt4" id="runBtn">Run SYAI</button>
        </div>
      </div>

      <!-- RIGHT -->
      <div>
        <div id="matrixCard" class="card" style="display:none">
          <div class="section-title">Decision Matrix (first 10 rows)</div>
          <div class="table-wrap"><table id="matrixTable"></table></div>
        </div>

        <div id="resultCard" class="card" style="display:none">
          <div class="section-title">Final Ranking (SYAI)</div>
          <div class="table-wrap"><table id="resultTable"></table></div>

          <div class="mt6">
            <div class="hint mb2">Ranking — Bar</div>
            <div class="chart"><svg id="barSVG" width="100%" height="100%"></svg></div>
          </div>

          <div class="mt6">
            <div class="hint mb2">Ranking — Line</div>
            <div class="linechart"><svg id="lineSVG" width="100%" height="100%"></svg></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== COMPARISON ==================== -->
  <div id="viewCompare" style="display:none">
    <!-- Scatter matrix -->
    <div class="cmp-row">
      <div class="cmp-panel">
        <div class="section-title">Scatter Matrix </div>
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
        <div class="section-title">Correlation Heatmap </div>
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
  $("tabRank").onclick=()=>{ $("tabRank").classList.add("active"); $("tabCompare").classList.remove("active"); show($("viewRank"),true); show($("viewCompare"),false); };
  $("tabCompare").onclick=()=>{ $("tabCompare").classList.add("active"); $("tabRank").classList.remove("active"); show($("viewRank"),false); show($("viewCompare"),true); };

  // Injected by Python for comparison images
  const SCATTER_URI = "SCATTER_DATA_URI";
  const CORR_URI    = "CORR_DATA_URI";
  const HAS_SCATTER = "HAS_SCATTER_FLAG" === "1";
  const HAS_CORR    = "HAS_CORR_FLAG" === "1";

  if (HAS_SCATTER) { $("bigScatter").src = SCATTER_URI; $("bigScatter").style.display = ""; }
  else { $("scatterMissing").style.display = ""; }
  if (HAS_CORR) { $("bigCorr").src = CORR_URI; $("bigCorr").style.display = ""; }
  else { $("corrMissing").style.display = ""; }

  // ========== CSV & SYAI ==========
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

  const sampleCSV = `Alternative,Cost,Quality,Delivery Time,Temperature
A1,200,8,4,30
A2,250,7,5,60
A3,300,9,6,85
`;
  $("downloadSample").href = "data:text/csv;charset=utf-8,"+encodeURIComponent(sampleCSV);
  $("downloadSample").download = "sample.csv";

  let columns=[], rows=[], crits=[], types={}, ideals={}, weights={}, beta=0.5, weightMode='equal';
  const C = 0.01;
  const toNum=(v)=>{ const x=parseFloat(String(v).replace(/,/g,"")); return isFinite(x)?x:NaN; };

  $("beta").oninput = ()=>{ beta = parseFloat($("beta").value); $("betaVal").textContent = beta.toFixed(2); };
  $("wEqual").onchange = ()=>{ weightMode='equal'; $("weightsGrid").style.display="none"; };
  $("wCustom").onchange = ()=>{ weightMode='custom'; $("weightsGrid").style.display=""; };

  $("csvFile").onchange = (e)=>{
    const f = e.target.files[0]; if(!f) return;
    const r = new FileReader();
    r.onload = ()=>{ try{ initFromCSV(String(r.result)); }catch(ex){ err(ex.message||String(ex)); } };
    r.readAsText(f);
  };

  function initFromCSV(txt){
    const arr = parseCSVText(txt);
    if(!arr.length) throw new Error("Empty CSV");
    columns = arr[0].map(c => String(c ?? "").trim());

    // Ensure first col is Alternative
    if (columns.includes("Alternative")){
      const idx = columns.indexOf("Alternative");
      if (idx !== 0){ const nm = columns.splice(idx,1)[0]; columns.unshift(nm); }
    } else {
      columns[0] = "Alternative";
    }

    crits = columns.slice(1);
    rows = arr.slice(1).filter(r=>r.length>=columns.length).map(r=>{
      const obj={}; columns.forEach((c,i)=> obj[c]=r[i] ?? ""); return obj;
    });

    types  = Object.fromEntries(crits.map(c=>[c,"Benefit"]));
    ideals = Object.fromEntries(crits.map(c=>[c,""]));
    weights= Object.fromEntries(crits.map(c=>[c,1]));

    renderMatrix(); renderTypes(); renderWeights();
    show($("matrixCard"), true);
    show($("typesCard"), true);
    show($("weightsCard"), true);
    show($("betaCard"), true);
    show($("resultCard"), false);
  }

  // Paper example
  $("loadPaperBtn").onclick = ()=>{
    const csv = `Alternative,Cost,Quality,Delivery Time,Temperature
A1,200,8,4,30
A2,250,7,5,60
A3,300,9,6,85
`;
    initFromCSV(csv);
    types = { "Cost":"Cost", "Quality":"Benefit", "Delivery Time":"Cost", "Temperature":"Ideal (Goal)" };
    ideals["Temperature"] = "60";
    weightMode = 'equal';
    $("wEqual").checked = true; $("wCustom").checked = false;
    $("weightsGrid").style.display="none";
    beta = 0.5; $("beta").value="0.5"; $("betaVal").textContent="0.50";
    renderTypes(); renderWeights();
    runSYAI();
  };

  function renderMatrix(){
    const tb = $("matrixTable"); tb.innerHTML="";
    const thead = document.createElement("thead"); const trh = document.createElement("tr");
    columns.forEach(c=>{ const th=document.createElement("th"); th.textContent=c; trh.appendChild(th); });
    thead.appendChild(trh); tb.appendChild(thead);
    const tbody = document.createElement("tbody");
    rows.slice(0,10).forEach(r=>{
      const tr=document.createElement("tr");
      columns.forEach(c=>{ const td=document.createElement("td"); td.textContent=String(r[c]??""); tr.appendChild(td); });
      tbody.appendChild(tr);
    });
    tb.appendChild(tbody);
  }

  function renderTypes(){
    const wrap=$("typesGrid"); wrap.innerHTML="";
    crits.forEach(c=>{
      const box=document.createElement("div"); box.style.minWidth="240px";
      const lab=document.createElement("div"); lab.className="label"; lab.textContent=c; box.appendChild(lab);
      const sel=document.createElement("select");
      ["Benefit","Cost","Ideal (Goal)"].forEach(v=>{ const o=document.createElement("option"); o.textContent=v; sel.appendChild(o); });
      sel.value = types[c]||"Benefit";
      sel.onchange = ()=>{ types[c]=sel.value; renderTypes(); };
      box.appendChild(sel);
      if((types[c]||"")==="Ideal (Goal)"){
        const inp=document.createElement("input"); inp.className="mt2"; inp.type="number"; inp.step="any"; inp.placeholder="Goal value";
        inp.value=ideals[c]||""; inp.oninput=()=> ideals[c]=inp.value; box.appendChild(inp);
      }else{ delete ideals[c]; }
      wrap.appendChild(box);
    });
  }

  function renderWeights(){
    const wrap=$("weightsGrid"); wrap.innerHTML="";
    crits.forEach(c=>{
      const box=document.createElement("div"); box.style.minWidth="160px";
      const lab=document.createElement("div"); lab.className="label"; lab.textContent=`w(${c})`; box.appendChild(lab);
      const inp=document.createElement("input"); inp.type="number"; inp.step="0.001"; inp.min="0"; inp.value=weights[c]??0;
      inp.oninput=()=> weights[c]=inp.value; box.appendChild(inp);
      wrap.appendChild(box);
    });
  }

  function normalizeColumn(vals, ctype, goal){
    const max=Math.max(...vals), min=Math.min(...vals), R=max-min;
    let xStar;
    if(ctype==="Benefit") xStar=max;
    else if(ctype==="Cost") xStar=min;
    else { const g=parseFloat(goal); xStar=isFinite(g)?g:(vals.reduce((s,v)=>s+(isFinite(v)?v:0),0)/vals.length); }
    if(Math.abs(R)<1e-12) return vals.map(_=>1.0);
    return vals.map(x=> Math.max(0.01, Math.min(1, 0.01 + (1-0.01)*(1-Math.abs(x-xStar)/R))));
  }

  function compute(){
    if(!columns.length||!rows.length){ err("No data"); return null; }
    const X=rows.map(r=> Object.fromEntries(crits.map(c=>[c,toNum(r[c])])) );
    const N={};
    crits.forEach(c=>{
      const series=X.map(row=>row[c]);
      N[c]=normalizeColumn(series, types[c]||"Benefit", ideals[c]);
    });

    const w={};
    if(weightMode==='equal'){ crits.forEach(c=> w[c]=1/crits.length); }
    else {
      let sum=0; crits.forEach(c=>{ const v=Math.max(0,parseFloat(weights[c]||0)); w[c]=isFinite(v)?v:0; sum+=w[c]; });
      if(sum<=0) crits.forEach(c=> w[c]=1/crits.length); else crits.forEach(c=> w[c]/=sum);
    }

    const W=rows.map((_,i)=> Object.fromEntries(crits.map(c=>[c,N[c][i]*w[c]])) );
    const Aplus={}, Aminus={};
    crits.forEach(c=>{
      let mx=-Infinity, mn=Infinity;
      W.forEach(row=>{ if(row[c]>mx) mx=row[c]; if(row[c]<mn) mn=row[c]; });
      Aplus[c]=mx; Aminus[c]=mn;
    });

    const res=rows.map((r,i)=>{
      let Dp=0, Dm=0;
      crits.forEach(c=>{ Dp+=Math.abs(W[i][c]-Aplus[c]); Dm+=Math.abs(W[i][c]-Aminus[c]); });
      const denom = beta*Dp + (1-beta)*Dm || Number.EPSILON;
      const Close = ((1-beta)*Dm)/denom;
      return { Alternative:String(r["Alternative"]), Dp, Dm, Close };
    });
    res.sort((a,b)=> b.Close-a.Close);
    res.forEach((r,i,arr)=> r.Rank = arr.slice(0,i).filter(x=>x.Close>r.Close).length + 1);
    return res;
  }

  $("runBtn").onclick = ()=> runSYAI();
  function runSYAI(){
    const result=compute(); if(!result) return;

    const tb=$("resultTable"); tb.innerHTML="";
    const thead=document.createElement("thead"); const trh=document.createElement("tr");
    ["Alternative","D+","D-","Closeness","Rank"].forEach(h=>{ const th=document.createElement("th"); th.textContent=h; trh.appendChild(th); });
    thead.appendChild(trh); tb.appendChild(thead);
    const tbody=document.createElement("tbody");
    result.forEach(r=>{
      const tr=document.createElement("tr");
      [r.Alternative, r.Dp.toFixed(6), r.Dm.toFixed(6), r.Close.toFixed(6), r.Rank].forEach(v=>{
        const td=document.createElement("td"); td.textContent=String(v); tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    tb.appendChild(tbody);
    show($("resultCard"), true);

    drawBar(result.map(r=>({name:r.Alternative, value:r.Close})));
    drawLine(result.map(r=>({rank:r.Rank, value:r.Close, name:r.Alternative})));
  }

  // charts + tooltips
  const PASTELS=["#a5b4fc","#f9a8d4","#bae6fd","#bbf7d0","#fde68a","#c7d2fe","#fecdd3","#fbcfe8","#bfdbfe","#d1fae5"];
  let barRects=[], linePoints=[];

  function showTip(html,x,y){
    let tt=document.getElementById("tt");
    if(!tt){
      tt=document.createElement("div");
      tt.id="tt";
      tt.style.position="fixed"; tt.style.display="none"; tt.style.padding="6px 8px";
      tt.style.borderRadius="8px"; tt.style.background="#fff"; tt.style.color="#111";
      tt.style.border="1px solid #e5e7eb"; tt.style.boxShadow="0 12px 24px rgba(0,0,0,.18)";
      tt.style.fontSize="12px"; tt.style.pointerEvents="none"; tt.style.zIndex="99999";
      document.body.appendChild(tt);
    }
    tt.innerHTML=html; tt.style.left=(x+12)+"px"; tt.style.top=(y+12)+"px"; tt.style.display="block";
  }
  function hideTip(){ const tt=document.getElementById("tt"); if(tt) tt.style.display="none"; }

  function drawBar(data){
    const svg=$("barSVG"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    barRects.length=0; hideTip();
    const rect=svg.getBoundingClientRect();
    const W=rect.width||800, H=rect.height||360, padL=50,padR=20,padT=18,padB=44;
    const max=Math.max(...data.map(d=>d.value))||1;
    const cell=(W-padL-padR)/data.length; const barW=cell*0.8;

    for(let t=0;t<=5;t++){
      const val=max*t/5, y=H-padB-(H-padT-padB)*(val/max);
      const line=document.createElementNS("http://www.w3.org/2000/svg","line");
      line.setAttribute("x1",padL-6); line.setAttribute("x2",W-padR); line.setAttribute("y1",y); line.setAttribute("y2",y);
      line.setAttribute("stroke","#374151"); line.setAttribute("stroke-dasharray","3 3"); svg.appendChild(line);
      const tEl=document.createElementNS("http://www.w3.org/2000/svg","text");
      tEl.setAttribute("x",padL-10); tEl.setAttribute("y",y+4); tEl.setAttribute("text-anchor","end"); tEl.setAttribute("font-size","12"); tEl.setAttribute("fill","#000");
      tEl.textContent=val.toFixed(2); svg.appendChild(tEl);
    }

    data.forEach((d,i)=>{
      const x=padL+i*cell+(cell-barW)/2; const h=(H-padT-padB)*(d.value/max); const y=H-padB-h;
      const r=document.createElementNS("http://www.w3.org/2000/svg","rect");
      r.setAttribute("x",x); r.setAttribute("y",y); r.setAttribute("width",barW); r.setAttribute("height",h); r.setAttribute("fill",PASTELS[i%PASTELS.length]); svg.appendChild(r);
      const v=document.createElementNS("http://www.w3.org/2000/svg","text");
      v.setAttribute("x",x+barW/2); v.setAttribute("y",Math.max(y+14,padT+12)); v.setAttribute("text-anchor","middle"); v.setAttribute("font-size","12"); v.setAttribute("fill","#000");
      v.textContent=d.value.toFixed(3); svg.appendChild(v);
      const lbl=document.createElementNS("http://www.w3.org/2000/svg","text");
      lbl.setAttribute("x",x+barW/2); lbl.setAttribute("y",H-12); lbl.setAttribute("text-anchor","middle"); lbl.setAttribute("font-size","12"); lbl.setAttribute("fill","#000"); lbl.textContent=d.name; svg.appendChild(lbl);
      barRects.push({x,y,w:barW,h,d});
    });

    svg.onmousemove=(e)=>{
      const b=svg.getBoundingClientRect(), mx=e.clientX-b.left, my=e.clientY-b.top;
      const hit=barRects.find(r=> mx>=r.x && mx<=r.x+r.w && my>=r.y && my<=r.y+r.h );
      if(hit) showTip(`${hit.d.name} — <b>${hit.d.value.toFixed(6)}</b>`, e.clientX, e.clientY); else hideTip();
    };
    svg.onmouseleave=hideTip;
  }

  function drawLine(data){
    const svg=$("lineSVG"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    linePoints.length=0; hideTip();

    const rect=svg.getBoundingClientRect();
    const W=rect.width||800, H=rect.height||300, padL=50,padR=20,padT=14,padB=30;
    const maxY=Math.max(...data.map(d=>d.value))||1, minX=1, maxX=Math.max(...data.map(d=>d.rank))||1;

    const sx=(r)=> padL+(W-padL-padR)*((r-minX)/(maxX-minX||1));
    const sy=(v)=> H-padB-(H-padT-padB)*(v/maxY);

    for(let t=0;t<=5;t++){
      const val=maxY*t/5, y=H-padB-(H-padT-padB)*(val/maxY);
      const gl=document.createElementNS("http://www.w3.org/2000/svg","line");
      gl.setAttribute("x1",padL-6); gl.setAttribute("x2",W-padR); gl.setAttribute("y1",y); gl.setAttribute("y2",y);
      gl.setAttribute("stroke","#374151"); gl.setAttribute("stroke-dasharray","3 3"); svg.appendChild(gl);
      const lbl=document.createElementNS("http://www.w3.org/2000/svg","text");
      lbl.setAttribute("x",padL-10); lbl.setAttribute("y",y+4); lbl.setAttribute("text-anchor","end"); lbl.setAttribute("font-size","12"); lbl.setAttribute("fill","#000");
      lbl.textContent=val.toFixed(2); svg.appendChild(lbl);
    }

    const p=document.createElementNS("http://www.w3.org/2000/svg","path");
    let dstr="";
    data.sort((a,b)=> a.rank-b.rank).forEach((pt,i)=>{
      const x=sx(pt.rank), y=sy(pt.value);
      dstr += (i===0? "M":"L") + x + " " + y + " ";
      linePoints.push({x,y,info:pt});
    });
    p.setAttribute("d", dstr.trim());
    p.setAttribute("fill","none"); p.setAttribute("stroke","#64748b"); p.setAttribute("stroke-width","2");
    svg.appendChild(p);

    linePoints.forEach(lp=>{
      const c=document.createElementNS("http://www.w3.org/2000/svg","circle");
      c.setAttribute("cx",lp.x); c.setAttribute("cy",lp.y); c.setAttribute("r","4"); c.setAttribute("fill","#94a3b8");
      svg.appendChild(c);
      const t=document.createElementNS("http://www.w3.org/2000/svg","text");
      t.setAttribute("x",lp.x+6); t.setAttribute("y",lp.y-6); t.setAttribute("font-size","12"); t.setAttribute("fill","#000");
      t.textContent=lp.info.value.toFixed(3); svg.appendChild(t);
    });

    for(let r=1;r<=maxX;r++){
      const x=sx(r);
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x",x); tx.setAttribute("y",H-8); tx.setAttribute("text-anchor","middle"); tx.setAttribute("font-size","12"); tx.setAttribute("fill","#000");
      tx.textContent=r; svg.appendChild(tx);
    }

    svg.onmousemove=(e)=>{
      const b=svg.getBoundingClientRect(), mx=e.clientX-b.left, my=e.clientY-b.top;
      let best=null, dist=1e9;
      linePoints.forEach(lp=>{
        const d=Math.hypot(lp.x-mx, lp.y-my);
        if(d<dist){ dist=d; best=lp; }
      });
      if(best && dist<12){
        const i=best.info;
        showTip(`${i.name||"Alt"} — <b>${i.value.toFixed(6)}</b> (Rank ${i.rank})`, e.clientX, e.clientY);
      } else hideTip();
    };
    svg.onmouseleave=hideTip;
  }
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

components.html(html, height=3000, scrolling=True)

# =========================
# NEW: Multi-Method Comparison (SYAI, TOPSIS, VIKOR, SAW, COBRA, WASPAS, MOORA)
# =========================
components.html(r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>SYAI-Rank — Multi-Method Comparison</title>
<style>
  :root{
    --bg:#0b0b0f; --ink:#f5f5f5; --muted:#94a3b8;
    --card:#0f1115cc; --border:#262b35;
    --accent:#ec4899; --accent-700:#db2777;
  }
  *{box-sizing:border-box} html,body{height:100%;margin:0}
  body{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto}
  body{background:linear-gradient(180deg,#0b0b0f 0%,#0b0b0f 35%,#ffe4e6 120%); color:var(--ink)}
  .wrap{max-width:1200px;margin:24px auto;padding:0 16px}
  .head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:8px}
  .h1{font-size:24px;font-weight:800}
  .row{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
  .btn{display:inline-flex;align-items:center;gap:8px;padding:10px 14px;border-radius:12px;border:1px solid var(--accent-700);background:var(--accent);color:#fff;cursor:pointer}
  .btn:hover{background:var(--accent-700)}
  .label{font-size:12px;opacity:.9;margin-bottom:4px;display:block}
  input[type="file"]{display:none}
  select,input[type="number"],input[type="range"]{padding:8px 10px;border-radius:10px;border:1px solid #374151;background:#0b0b0f;color:#e5e7eb}
  .card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:16px}
  .title{font-size:16px;font-weight:700;color:#f9a8d4;margin-bottom:10px}
  .hint{font-size:12px;color:#fbcfe8}
  .grid{display:grid;gap:16px;grid-template-columns:1fr}
  @media (min-width:1024px){.grid{grid-template-columns:1fr 2fr}}
  .table-wrap{overflow:auto;max-height:400px;border-radius:12px;border:1px solid #27303b}
  table{width:100%;border-collapse:collapse;font-size:14px;background:transparent}
  th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #27303b; white-space:nowrap}
  th{position:sticky;top:0;background:#0b0b0f}
  .chart{width:100%;height:360px;border:1px dashed #2a2f38;border-radius:12px;padding:8px;margin-top:12px}
  .chart2{width:100%;height:360px;border:1px dashed #2a2f38;border-radius:12px;padding:8px;margin-top:12px}
</style>
</head>
<body>
<div class="wrap" id="mmc">
  <div class="head">
    <div class="h1">Multi-Method Comparison</div>
    <div class="row">
      <label class="btn" for="mmc_file">📤 Upload CSV</label>
      <input id="mmc_file" type="file" accept=".csv"/>
      <button class="btn" id="mmc_demo">📄 Load Demo</button>
      <span class="hint">Format: first column = <b>Alternative</b>, other columns = numeric criteria</span>
    </div>
  </div>

  <div class="grid">
    <!-- LEFT controls -->
    <div>
      <div class="card">
        <div class="title">Criteria Types</div>
        <div id="mmc_types" class="row"></div>
      </div>

      <div class="card" style="margin-top:12px">
        <div class="title">Weights & Parameters</div>
        <div class="row" style="gap:16px">
          <label><input type="radio" name="mmc_wmode" id="mmc_weq" checked> Equal (1/m)</label>
          <label><input type="radio" name="mmc_wmode" id="mmc_wcustom"> Custom</label>
        </div>
        <div id="mmc_wgrid" class="row" style="display:none;margin-top:8px"></div>

        <div style="margin-top:12px">
          <span class="label">SYAI β (blend of D⁺ and D⁻)</span>
          <input id="mmc_beta" type="range" min="0" max="1" step="0.01" value="0.5" style="width:100%">
          <div class="hint">β = <b id="mmc_beta_val">0.50</b></div>
        </div>

        <div style="margin-top:12px">
          <span class="label">VIKOR v (strategy weight)</span>
          <input id="mmc_vikor_v" type="range" min="0" max="1" step="0.01" value="0.5" style="width:100%">
          <div class="hint">v = <b id="mmc_vikor_v_val">0.50</b></div>
        </div>

        <div style="margin-top:12px">
          <span class="label">WASPAS λ (mix WSM/WPM)</span>
          <input id="mmc_waspas_l" type="range" min="0" max="1" step="0.01" value="0.5" style="width:100%">
          <div class="hint">λ = <b id="mmc_waspas_l_val">0.50</b></div>
        </div>

        <button class="btn" id="mmc_run" style="margin-top:12px">▶️ Run Comparison</button>
      </div>
    </div>

    <!-- RIGHT outputs -->
    <div>
      <div class="card">
        <div class="title">Combined Results — Scores and Ranks</div>
        <div class="table-wrap"><table id="mmc_table"></table></div>
      </div>

      <div class="card" style="margin-top:12px">
        <div class="title">Scores — Grouped Bar</div>
        <div class="chart"><svg id="mmc_bar" width="100%" height="100%"></svg></div>

        <div class="title">Method vs Method — Scatter</div>
        <div class="row" style="gap:12px;align-items:center">
          <div>
            <div class="label">X-Axis</div>
            <select id="mmc_x">
              <option>SYAI</option><option>TOPSIS</option><option>VIKOR</option><option>SAW</option><option>COBRA</option><option>WASPAS</option><option>MOORA</option>
            </select>
          </div>
          <div>
            <div class="label">Y-Axis</div>
            <select id="mmc_y">
              <option>TOPSIS</option><option>SYAI</option><option>VIKOR</option><option>SAW</option><option>COBRA</option><option>WASPAS</option><option>MOORA</option>
            </select>
          </div>
          <button class="btn" id="mmc_redraw">🔁 Redraw</button>
        </div>
        <div class="chart2"><svg id="mmc_scatter" width="100%" height="100%"></svg></div>
      </div>
    </div>
  </div>
</div>

<script>
(function(){
  const $ = (id)=> document.getElementById(id);
  const PASTELS=["#a5b4fc","#f9a8d4","#bae6fd","#bbf7d0","#fde68a","#c7d2fe","#fecdd3","#fbcfe8","#bfdbfe","#d1fae5","#ddd6fe","#fdba74"];
  const toNum=(v)=>{ const x=parseFloat(String(v).replace(/,/g,"")); return isFinite(x)?x:NaN; };

  let columns=[], crits=[], rows=[];
  let types={}, ideals={}, weights={}, weightMode='equal', beta=0.5, vikor_v=0.5, waspas_l=0.5;

  $("mmc_weq").onchange=()=>{ weightMode='equal'; $("mmc_wgrid").style.display="none"; };
  $("mmc_wcustom").onchange=()=>{ weightMode='custom'; $("mmc_wgrid").style.display=""; };
  $("mmc_beta").oninput=()=>{ beta=parseFloat($("mmc_beta").value); $("mmc_beta_val").textContent=beta.toFixed(2); };
  $("mmc_vikor_v").oninput=()=>{ vikor_v=parseFloat($("mmc_vikor_v").value); $("mmc_vikor_v_val").textContent=vikor_v.toFixed(2); };
  $("mmc_waspas_l").oninput=()=>{ waspas_l=parseFloat($("mmc_waspas_l").value); $("mmc_waspas_l_val").textContent=waspas_l.toFixed(2); };

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

  const demoCSV = `Alternative,Cost,Quality,Delivery Time,Temperature
A1,200,8,4,30
A2,250,7,5,60
A3,300,9,6,85
A4,220,8,4,50
A5,180,6,7,40
`;
  $("mmc_demo").onclick = ()=> initFromCSV(demoCSV);
  $("mmc_file").onchange = (e)=>{
    const f=e.target.files[0]; if(!f) return;
    const r=new FileReader(); r.onload=()=> initFromCSV(String(r.result)); r.readAsText(f);
  };

  function initFromCSV(txt){
    const arr=parseCSVText(txt); if(!arr.length) return;
    columns = arr[0].map(c => String(c ?? "").trim());
    if(columns.includes("Alternative")){
      const idx=columns.indexOf("Alternative");
      if(idx!==0){ const nm=columns.splice(idx,1)[0]; columns.unshift(nm); }
    } else { columns[0]="Alternative"; }
    crits = columns.slice(1);
    rows = arr.slice(1).filter(r=>r.length>=columns.length).map(r=>{
      const o={}; columns.forEach((c,i)=> o[c]=r[i] ?? ""; ); return o;
    });

    types  = Object.fromEntries(crits.map(c=>[c,"Benefit"]));
    ideals = Object.fromEntries(crits.map(c=>[c,""]));
    weights= Object.fromEntries(crits.map(c=>[c,1]));

    renderTypes(); renderWeights();
  }

  function renderTypes(){
    const wrap=$("mmc_types"); wrap.innerHTML="";
    crits.forEach(c=>{
      const box=document.createElement("div"); box.style.minWidth="220px";
      const lab=document.createElement("div"); lab.className="label"; lab.textContent=c; box.appendChild(lab);
      const sel=document.createElement("select");
      ["Benefit","Cost","Ideal (Goal)"].forEach(v=>{ const o=document.createElement("option"); o.textContent=v; sel.appendChild(o); });
      sel.value = types[c]||"Benefit";
      sel.onchange = ()=>{ types[c]=sel.value; renderTypes(); };
      box.appendChild(sel);
      if((types[c]||"")==="Ideal (Goal)"){
        const inp=document.createElement("input"); inp.className="mt2"; inp.type="number"; inp.step="any"; inp.placeholder="Goal value";
        inp.value=ideals[c]||""; inp.oninput=()=> ideals[c]=inp.value; box.appendChild(inp);
      }else{ delete ideals[c]; }
      wrap.appendChild(box);
    });
  }

  function renderWeights(){
    const wrap=$("mmc_wgrid"); wrap.innerHTML="";
    crits.forEach(c=>{
      const box=document.createElement("div"); box.style.minWidth="140px";
      const lab=document.createElement("div"); lab.className="label"; lab.textContent=`w(${c})`; box.appendChild(lab);
      const inp=document.createElement("input"); inp.type="number"; inp.step="0.001"; inp.min="0"; inp.value=weights[c]??0;
      inp.oninput=()=> weights[c]=inp.value; box.appendChild(inp);
      wrap.appendChild(box);
    });
  }

  // ---------- Normalization helpers ----------
  function normSAW(vals, ctype, goal){
    const max=Math.max(...vals), min=Math.min(...vals), R=max-min || 1;
    if(ctype==="Benefit"){ return vals.map(x=> (x-min)/R); }
    if(ctype==="Cost"){    return vals.map(x=> (max-x)/R); }
    const g=parseFloat(goal); const gStar = isFinite(g)?g : (min+max)/2;
    const L=Math.max(gStar-min, max-gStar)||1;
    return vals.map(x=> 1 - (Math.abs(x-gStar)/L) );
  }
  function normSYAI(vals, ctype, goal){
    const max=Math.max(...vals), min=Math.min(...vals), R=max-min;
    let xStar;
    if(ctype==="Benefit") xStar=max;
    else if(ctype==="Cost") xStar=min;
    else { const g=parseFloat(goal); xStar=isFinite(g)?g:(min+max)/2; }
    if(Math.abs(R)<1e-12) return vals.map(_=>1.0);
    return vals.map(x=> Math.max(0.01, Math.min(1, 0.01 + (1-0.01)*(1-Math.abs(x-xStar)/R))));
  }
  function normVector(vals){
    const denom=Math.sqrt(vals.reduce((s,v)=>s+(isFinite(v)?v*v:0),0))||1;
    return vals.map(v=> (isFinite(v)?v:0)/denom);
  }
  function toBenefit(vals, ctype, goal){
    const max=Math.max(...vals), min=Math.min(...vals), R=max-min || 1;
    if(ctype==="Benefit") return vals.map(x=> (x-min)/R);
    if(ctype==="Cost")    return vals.map(x=> (max-x)/R);
    const g=parseFloat(goal); const gStar = isFinite(g)?g : (min+max)/2;
    const L=Math.max(gStar-min, max-gStar)||1;
    return vals.map(x=> 1 - (Math.abs(x-gStar)/L) );
  }

  // ---------- Compute all methods ----------
  function computeAll(){
    if(!columns.length||!rows.length) return null;

    const X = rows.map(r => Object.fromEntries(crits.map(c=>[c,toNum(r[c])])) );

    // weights
    const w={};
    if(weightMode==='equal'){ crits.forEach(c=> w[c]=1/crits.length); }
    else {
      let s=0; crits.forEach(c=>{ const v=Math.max(0,parseFloat(weights[c]||0)); w[c]=isFinite(v)?v:0; s+=w[c]; });
      if(s<=0) crits.forEach(c=> w[c]=1/crits.length); else crits.forEach(c=> w[c]/=s);
    }

    const series = Object.fromEntries(crits.map(c=>[c, X.map(r=>r[c])]));

    // SAW
    const N_saw={};
    crits.forEach(c=> N_saw[c]=normSAW(series[c], types[c]||"Benefit", ideals[c]) );
    const SAW = rows.map((_,i)=> crits.reduce((sum,c)=> sum + w[c]*N_saw[c][i], 0));

    // SYAI
    const N_sy={};
    crits.forEach(c=> N_sy[c]=normSYAI(series[c], types[c]||"Benefit", ideals[c]) );
    const W_sy = rows.map((_,i)=> Object.fromEntries(crits.map(c=>[c,N_sy[c][i]*w[c]])) );
    const Aplus_sy={}, Aminus_sy={};
    crits.forEach(c=>{
      let mx=-Infinity, mn=Infinity;
      W_sy.forEach(r=>{ if(r[c]>mx) mx=r[c]; if(r[c]<mn) mn=r[c]; });
      Aplus_sy[c]=mx; Aminus_sy[c]=mn;
    });
    const SYAI = rows.map((r,i)=>{
      let Dp=0, Dm=0;
      crits.forEach(c=>{ Dp+=Math.abs(W_sy[i][c]-Aplus_sy[c]); Dm+=Math.abs(W_sy[i][c]-Aminus_sy[c]); });
      const denom = beta*Dp + (1-beta)*Dm || Number.EPSILON;
      return ((1-beta)*Dm)/denom;
    });

    // TOPSIS
    const N_tp={}, W_tp_rows=[];
    crits.forEach(c=> N_tp[c]=normVector(series[c]) );
    rows.forEach((_,i)=> W_tp_rows.push(Object.fromEntries(crits.map(c=>[c,N_tp[c][i]*w[c]]))) );
    const Aplus_tp={}, Aminus_tp={};
    crits.forEach(c=>{
      const ctype=types[c]||"Benefit";
      const arr=W_tp_rows.map(r=>r[c]);
      const mx=Math.max(...arr), mn=Math.min(...arr);
      if(ctype==="Benefit"){ Aplus_tp[c]=mx; Aminus_tp[c]=mn; }
      else if(ctype==="Cost"){ Aplus_tp[c]=mn; Aminus_tp[c]=mx; }
      else {
        const g=parseFloat(ideals[c]); const goal = isFinite(g)?g : (series[c].reduce((s,v)=>s+v,0)/series[c].length);
        const best = arr.reduce((b,v)=> (Math.abs(v-goal)<Math.abs(b-goal)?v:b), arr[0]);
        const worst= arr.reduce((b,v)=> (Math.abs(v-goal)>Math.abs(b-goal)?v:b), arr[0]);
        Aplus_tp[c]=best; Aminus_tp[c]=worst;
      }
    });
    const TOPSIS = rows.map((r,i)=>{
      let Dp=0, Dm=0;
      crits.forEach(c=>{ const d=W_tp_rows[i][c]; Dp+= (d-Aplus_tp[c])**2; Dm+= (d-Aminus_tp[c])**2; });
      Dp=Math.sqrt(Dp); Dm=Math.sqrt(Dm);
      return Dm/(Dp+Dm);
    });

    // VIKOR (lower better)
    const U={};
    crits.forEach(c=> U[c]=toBenefit(series[c], types[c]||"Benefit", ideals[c]));
    const S = rows.map((_,i)=> crits.reduce((sum,c)=> sum + w[c]*(1-U[c][i]), 0));
    const R = rows.map((_,i)=> Math.max(...crits.map(c=> w[c]*(1-U[c][i]) )));
    const Smin=Math.min(...S), Smax=Math.max(...S), Rmin=Math.min(...R), Rmax=Math.max(...R);
    const VIKOR = rows.map((_,i)=>{
      const sN=(S[i]-Smin)/((Smax-Smin)||1);
      const rN=(R[i]-Rmin)/((Rmax-Rmin)||1);
      return vikor_v*sN + (1-vikor_v)*rN;
    });

    // COBRA (distance diff on U)
    const COBRA = rows.map((_,i)=>{
      let diPlus=0, diMinus=0;
      crits.forEach(c=>{
        const z=U[c][i];
        diPlus  += w[c]*(1 - z)**2;
        diMinus += w[c]*(z - 0)**2;
      });
      diPlus=Math.sqrt(diPlus); diMinus=Math.sqrt(diMinus);
      return diMinus - diPlus; // higher better
    });

    // WASPAS
    const WSM = rows.map((_,i)=> crits.reduce((sum,c)=> sum + w[c]*U[c][i], 0));
    const WPM = rows.map((_,i)=> crits.reduce((prod,c)=> prod * Math.pow(Math.max(U[c][i],1e-12), w[c]), 1));
    const WASPAS = rows.map((_,i)=> waspas_l*WSM[i] + (1-waspas_l)*WPM[i]);

    // MOORA
    const normPerC = Object.fromEntries(crits.map(c=>{
      const v=series[c]; const denom=Math.sqrt(v.reduce((s,x)=>s+(isFinite(x)?x*x:0),0))||1;
      return [c, v.map(x=> (isFinite(x)?x:0)/denom)];
    }));
    const MOORA = rows.map((_,i)=>{
      let pos=0, neg=0;
      crits.forEach(c=>{
        if((types[c]||"Benefit")==="Cost") neg += w[c]*normPerC[c][i];
        else if((types[c]||"Benefit")==="Ideal (Goal)"){
          // treat goal as benefit proximity (simple)
          const g=parseFloat(ideals[c]); const goal = isFinite(g)?g : 0;
          pos += w[c]*(1 - Math.abs(normPerC[c][i]-goal)); 
        } else pos += w[c]*normPerC[c][i];
      });
      return pos - neg;
    });

    // Ranks
    function ranksHigherBetter(arr){
      const idx=arr.map((v,i)=>({v,i})).sort((a,b)=> b.v-a.v);
      const rank=new Array(arr.length).fill(0);
      idx.forEach((o,k)=>{ rank[o.i]=k+1; });
      return rank;
    }
    function ranksLowerBetter(arr){
      const idx=arr.map((v,i)=>({v,i})).sort((a,b)=> a.v-b.v);
      const rank=new Array(arr.length).fill(0);
      idx.forEach((o,k)=>{ rank[o.i]=k+1; });
      return rank;
    }

    const rk = {
      SYAI:   ranksHigherBetter(SYAI),
      TOPSIS: ranksHigherBetter(TOPSIS),
      VIKOR:  ranksLowerBetter(VIKOR),
      SAW:    ranksHigherBetter(SAW),
      COBRA:  ranksHigherBetter(COBRA),
      WASPAS: ranksHigherBetter(WASPAS),
      MOORA:  ranksHigherBetter(MOORA)
    };

    return {
      methods: {SYAI, TOPSIS, VIKOR, SAW, COBRA, WASPAS, MOORA},
      ranks: rk
    };
  }

  // Render table score (rank)
  function renderTable(res){
    const tb=$("mmc_table"); tb.innerHTML="";
    const head=["Alternative","TOPSIS","VIKOR","SAW","SYAI","COBRA","WASPAS","MOORA"];
    const thead=document.createElement("thead"); const trh=document.createElement("tr");
    head.forEach(h=>{ const th=document.createElement("th"); th.textContent=h; trh.appendChild(th); });
    thead.appendChild(trh); tb.appendChild(thead);

    const tbody=document.createElement("tbody");
    rows.forEach((r,i)=>{
      const tr=document.createElement("tr");
      const td0=document.createElement("td"); td0.textContent=String(r["Alternative"]); tr.appendChild(td0);

      function cell(name, decimals=4){
        const val=res.methods[name][i];
        const rank=res.ranks[name][i];
        const td=document.createElement("td");
        td.textContent = `${val.toFixed(decimals)} (${rank})`;
        tr.appendChild(td);
      }
      // column order to match the screenshot
      cell("TOPSIS"); cell("VIKOR"); cell("SAW");
      cell("SYAI");   cell("COBRA",4); cell("WASPAS",4); cell("MOORA",4);

      tbody.appendChild(tr);
    });
    tb.appendChild(tbody);
  }

  // Charts
  function drawGroupedBar(res){
    const svg=$("mmc_bar"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const rect=svg.getBoundingClientRect();
    const W=rect.width||900, H=rect.height||360, padL=70,padR=20,padT=18,padB=60;

    const methods=["TOPSIS","VIKOR","SAW","SYAI","COBRA","WASPAS","MOORA"];
    const data = rows.map((r,i)=>({
      name:String(r["Alternative"]),
      vals: methods.map(m=> res.methods[m][i])
    }));

    const max = Math.max(...data.flatMap(d=>d.vals));
    const min = Math.min(...data.flatMap(d=>d.vals));
    const yMax = Math.max(max, 0);
    const yMin = Math.min(min, 0);
    const range = yMax - yMin || 1;

    const cell=(W-padL-padR)/data.length;
    const barW=cell*0.75/methods.length;

    for(let t=0;t<=5;t++){
      const val=yMin + range*t/5;
      const y=H-padB-(H-padT-padB)*((val - yMin)/range);
      const ln=document.createElementNS("http://www.w3.org/2000/svg","line");
      ln.setAttribute("x1",padL-6); ln.setAttribute("x2",W-padR); ln.setAttribute("y1",y); ln.setAttribute("y2",y);
      ln.setAttribute("stroke","#374151"); ln.setAttribute("stroke-dasharray","3 3"); svg.appendChild(ln);
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x",padL-10); tx.setAttribute("y",y+4); tx.setAttribute("text-anchor","end"); tx.setAttribute("font-size","12"); tx.setAttribute("fill","#f5f5f5");
      tx.textContent=val.toFixed(2); svg.appendChild(tx);
    }

    data.forEach((d,i)=>{
      const x0=padL+i*cell + (cell - barW*methods.length)/2;
      const lbl=document.createElementNS("http://www.w3.org/2000/svg","text");
      lbl.setAttribute("x",x0 + (barW*methods.length)/2);
      lbl.setAttribute("y",H-8); lbl.setAttribute("text-anchor","middle"); lbl.setAttribute("font-size","12"); lbl.setAttribute("fill","#f5f5f5");
      lbl.textContent=d.name; svg.appendChild(lbl);

      d.vals.forEach((v,k)=>{
        const x=x0 + k*barW;
        const y=H-padB-(H-padT-padB)*((v - yMin)/range);
        const h=H-padB - y;
        const r=document.createElementNS("http://www.w3.org/2000/svg","rect");
        r.setAttribute("x",x); r.setAttribute("y", h>=0? y : H-padB);
        r.setAttribute("width",barW-2); r.setAttribute("height",Math.abs(h));
        r.setAttribute("fill",PASTELS[k%PASTELS.length]); svg.appendChild(r);
      });
    });

    methods.forEach((m,i)=>{
      const y=padT+12 + i*16, x=W-padR-160;
      const sw=document.createElementNS("http://www.w3.org/2000/svg","rect");
      sw.setAttribute("x",x); sw.setAttribute("y",y-10); sw.setAttribute("width",12); sw.setAttribute("height",12); sw.setAttribute("fill",PASTELS[i%PASTELS.length]);
      const tt=document.createElementNS("http://www.w3.org/2000/svg","text");
      tt.setAttribute("x",x+18); tt.setAttribute("y",y); tt.setAttribute("font-size","12"); tt.setAttribute("fill","#f5f5f5"); tt.textContent=m;
      svg.appendChild(sw); svg.appendChild(tt);
    });
  }

  function drawScatter(res){
    const svg=$("mmc_scatter"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    const rect=svg.getBoundingClientRect();
    const W=rect.width||900, H=rect.height||360, padL=60,padR=20,padT=20,padB=50;

    const mx=$("mmc_x").value, my=$("mmc_y").value;
    const xs = res.methods[mx], ys=res.methods[my];
    const Xmin=Math.min(...xs), Xmax=Math.max(...xs), Ymin=Math.min(...ys), Ymax=Math.max(...ys);
    const sx=(x)=> padL+(W-padL-padR)*((x-Xmin)/((Xmax-Xmin)||1));
    const sy=(y)=> H-padB-(H-padT-padB)*((y-Ymin)/((Ymax-Ymin)||1));

    const ax=document.createElementNS("http://www.w3.org/2000/svg","line");
    ax.setAttribute("x1",padL); ax.setAttribute("x2",padL); ax.setAttribute("y1",padT); ax.setAttribute("y2",H-padB); ax.setAttribute("stroke","#374151");
    const ay=document.createElementNS("http://www.w3.org/2000/svg","line");
    ay.setAttribute("x1",padL); ay.setAttribute("x2",W-padR); ay.setAttribute("y1",H-padB); ay.setAttribute("y2",H-padB); ay.setAttribute("stroke","#374151");
    svg.appendChild(ax); svg.appendChild(ay);

    for(let t=0;t<=5;t++){
      const vx=Xmin+(Xmax-Xmin)*t/5, vy=Ymin+(Ymax-Ymin)*t/5;
      const tx=document.createElementNS("http://www.w3.org/2000/svg","text");
      tx.setAttribute("x",padL-8); tx.setAttribute("y",sy(vy)+4); tx.setAttribute("text-anchor","end"); tx.setAttribute("font-size","12"); tx.setAttribute("fill","#f5f5f5"); tx.textContent=vy.toFixed(2);
      const ty=document.createElementNS("http://www.w3.org/2000/svg","text");
      ty.setAttribute("x",sx(vx)); ty.setAttribute("y",H-padB+16); ty.setAttribute("text-anchor","middle"); ty.setAttribute("font-size","12"); ty.setAttribute("fill","#f5f5f5"); ty.textContent=vx.toFixed(2);
      svg.appendChild(tx); svg.appendChild(ty);
    }

    rows.forEach((r,i)=>{
      const cx=sx(xs[i]), cy=sy(ys[i]);
      const c=document.createElementNS("http://www.w3.org/2000/svg","circle");
      c.setAttribute("cx",cx); c.setAttribute("cy",cy); c.setAttribute("r","5"); c.setAttribute("fill",PASTELS[i%PASTELS.length]);
      svg.appendChild(c);
      const lb=document.createElementNS("http://www.w3.org/2000/svg","text");
      lb.setAttribute("x",cx+6); lb.setAttribute("y",cy-6); lb.setAttribute("font-size","12"); lb.setAttribute("fill","#f5f5f5"); lb.textContent=String(r["Alternative"]);
      svg.appendChild(lb);
    });

    const lx=document.createElementNS("http://www.w3.org/2000/svg","text");
    lx.setAttribute("x",(padL+W-padR)/2); lx.setAttribute("y",H-8); lx.setAttribute("text-anchor","middle"); lx.setAttribute("font-size","12"); lx.setAttribute("fill","#f5f5f5"); lx.textContent=mx;
    const ly=document.createElementNS("http://www.w3.org/2000/svg","text");
    ly.setAttribute("x",18); ly.setAttribute("y",(padT+H-padB)/2); ly.setAttribute("transform","rotate(-90 18 "+((padT+H-padB)/2)+")"); ly.setAttribute("font-size","12"); ly.setAttribute("fill","#f5f5f5"); ly.textContent=my;
    svg.appendChild(lx); svg.appendChild(ly);
  }

  $("mmc_redraw").onclick = ()=>{ const res=computeAll(); if(res){ drawScatter(res); } };
  $("mmc_run").onclick = ()=>{
    const res=computeAll(); if(!res) return;
    renderTable(res);
    drawGroupedBar(res);
    drawScatter(res);
  };
})();
</script>
</body>
</html>
""", height=1800, scrolling=True)
