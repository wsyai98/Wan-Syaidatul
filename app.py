import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SYAI-Rank (Web UI)", layout="wide")

# Soft shell behind the embed
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
    --text-light:#f5f5f5; --text-dark:#1f2937;
    --pink:#ec4899; --pink-700:#db2777;
    --border-dark:#262b35; --border-light:#fbcfe8;
  }
  *{box-sizing:border-box} html,body{height:100%;margin:0}
  body{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Ubuntu,Cantarell,"Noto Sans","Helvetica Neue",Arial}
  body.theme-dark{
    color:var(--text-light);
    background:linear-gradient(180deg,var(--bg-dark) 0%,var(--bg-dark) 35%,var(--grad-light) 120%);
  }
  body.theme-light{
    color:#111;
    background:linear-gradient(180deg,var(--bg-light) 0%,var(--bg-light) 40%,var(--grad-light) 120%);
  }

  .container{max-width:1200px;margin:24px auto;padding:0 16px}
  .header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
  .title{font-weight:800;font-size:28px;color:#fce7f3}
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

  input[type="text"],input[type="number"],select{
    width:100%;padding:10px 12px;border-radius:10px;border:1px solid #ddd;background:#f8fafc;color:#111
  }
  .hint{font-size:12px;opacity:.8}

  .table-wrap{overflow:auto;max-height:360px}
  table{width:100%;border-collapse:collapse;font-size:14px;color:#000} /* force black inside tables */
  th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #e5e7eb}

  .mt2{margin-top:8px}.mt4{margin-top:16px}.mt6{margin-top:24px}.mb2{margin-bottom:8px}
  .w100{width:100%}

  .chart,.linechart{width:100%;border:1px dashed #2a2f38;border-radius:12px;padding:8px;background:transparent}
  .chart{height:360px}
  .linechart{height:300px}

  #tooltip{
    position:fixed;display:none;padding:6px 8px;border-radius:8px;background:#fff;color:#111;
    border:1px solid #e5e7eb;box-shadow:0 12px 24px rgba(0,0,0,.18);font-size:12px;pointer-events:none;z-index:99999
  }

  #err{display:none;background:#7f1d1d;color:#fff;padding:10px 12px;border:1px solid #fecaca;border-radius:8px;margin-bottom:8px;white-space:pre-wrap}
</style>
</head>
<body class="theme-dark">
<div class="container">
  <div id="tooltip"></div>
  <div id="err"></div>

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
    <div class="grid">
      <!-- LEFT -->
      <div>
        <div class="card dark">
          <div class="section-title">Step 1: Upload Decision Matrix</div>
          <label for="csvFile" class="btn">📤 Choose CSV</label>
          <input id="csvFile" type="file" accept=".csv" style="display:none"/>
          <p class="hint mt2">First column is treated as <b>Alternative</b> automatically.</p>
        </div>

        <div id="typesCard" class="card dark" style="display:none">
          <div class="section-title">Step 2: Define Criteria Types</div>
          <div id="typesGrid" class="row"></div>
        </div>

        <div id="weightsCard" class="card dark" style="display:none">
          <div class="section-title">Step 3: Set Weights</div>
          <div class="row mb2" style="gap:16px">
            <label><input type="radio" name="wmode" id="wEqual" checked> Equal (1/m)</label>
            <label><input type="radio" name="wmode" id="wCustom"> Custom (raw; normalized on run)</label>
          </div>
          <div id="weightsGrid" class="row" style="display:none"></div>
        </div>

        <div id="betaCard" class="card dark" style="display:none">
          <div class="section-title">Step 4: β (blend of D⁺ and D⁻)</div>
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

  <!-- COMPARISON -->
  <div id="viewCompare" style="display:none">
    <div class="grid">
      <div class="card dark">
        <div class="section-title">Load Images (URLs or Upload)</div>
        <div class="label">Scatter matrix image URL (raw GitHub/public)</div>
        <input id="urlScatter" type="text" placeholder="https://..." />
        <img id="imgScatter" class="mt2" style="display:none;width:100%;border-radius:12px;border:1px solid #2a2f38"/>
        <div class="label mt2">Correlation heatmap image URL (raw GitHub/public)</div>
        <input id="urlCorr" type="text" placeholder="https://..." />
        <img id="imgCorr" class="mt2" style="display:none;width:100%;border-radius:12px;border:1px solid #2a2f38"/>
        <p class="hint mt2">Use direct links that end with .png/.jpg (GitHub: “Download raw file”).</p>
        <div class="mt4">
          <div class="label">Or upload images</div>
          <input id="upScatter" type="file" accept=".png,.jpg,.jpeg"/>
          <input id="upCorr" class="mt2" type="file" accept=".png,.jpg,.jpeg"/>
        </div>
      </div>

      <div class="card">
        <div class="section-title">How to read the figures</div>
        <ul>
          <li><b>Scatter matrix</b> shows pairwise score relationships (each dot = one alternative).</li>
          <li><b>Correlation heatmap</b> highlights similarity of scores/rankings across methods (darker = stronger agreement).</li>
          <li>Use these to validate whether SYAI trends align with or diverge from other methods.</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div id="tooltip"></div>

<script>
(function(){
  const $ = (id)=> document.getElementById(id);
  const show = (el, on=true)=> { el.style.display = on ? "" : "none"; };
  const err = (msg)=>{ const e=$("err"); e.textContent="Error: "+msg; e.style.display="block"; };

  // THEME
  let dark=true;
  const applyTheme = ()=> {
    document.body.classList.toggle('theme-dark', dark);
    document.body.classList.toggle('theme-light', !dark);
    $("themeToggle").textContent = dark ? "🌙 Dark" : "☀️ Light";
  };
  $("themeToggle").onclick=()=>{ dark=!dark; applyTheme(); };
  applyTheme();

  // TOOLTIP
  const tooltip = $("tooltip");
  function showTip(html, x, y){
    tooltip.innerHTML = html;
    tooltip.style.left = (x + 12) + "px";
    tooltip.style.top  = (y + 12) + "px";
    tooltip.style.display = "block";
  }
  function hideTip(){ tooltip.style.display = "none"; }

  // CSV PARSER
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

  // SAMPLE CSV
  const sampleCSV = `Alternative,Cost,Quality,Delivery Time,Temperature
A1,200,8,4,30
A2,250,7,5,60
A3,300,9,6,85
`;
  $("downloadSample").href = "data:text/csv;charset=utf-8,"+encodeURIComponent(sampleCSV);
  $("downloadSample").download = "sample.csv";

  // TABS
  $("tabRank").onclick=()=>{ $("tabRank").classList.add("active"); $("tabCompare").classList.remove("active"); show($("viewRank"),true); show($("viewCompare"),false); };
  $("tabCompare").onclick=()=>{ $("tabCompare").classList.add("active"); $("tabRank").classList.remove("active"); show($("viewRank"),false); show($("viewCompare"),true); };

  // COMPARISON images
  $("urlScatter").oninput = ()=>{ const v=$("urlScatter").value.trim(); if(v){ $("imgScatter").src=v; show($("imgScatter"),true);} else show($("imgScatter"),false); };
  $("urlCorr").oninput = ()=>{ const v=$("urlCorr").value.trim(); if(v){ $("imgCorr").src=v; show($("imgCorr"),true);} else show($("imgCorr"),false); };
  $("upScatter").onchange = (e)=>{ const f=e.target.files[0]; if(!f) return; const r=new FileReader(); r.onload=()=>{ $("imgScatter").src=r.result; show($("imgScatter"),true); }; r.readAsDataURL(f); };
  $("upCorr").onchange = (e)=>{ const f=e.target.files[0]; if(!f) return; const r=new FileReader(); r.onload=()=>{ $("imgCorr").src=r.result; show($("imgCorr"),true); }; r.readAsDataURL(f); };

  // STATE
  let columns=[], rows=[], crits=[], types={}, ideals={}, weights={}, beta=0.5, weightMode='equal';
  $("beta").oninput = ()=>{ beta = parseFloat($("beta").value); $("betaVal").textContent = beta.toFixed(2); };
  $("wEqual").onchange = ()=>{ weightMode='equal'; show($("weightsGrid"),false); };
  $("wCustom").onchange = ()=>{ weightMode='custom'; show($("weightsGrid"),true); };

  // UPLOAD
  $("csvFile").onchange = (e)=>{
    const f = e.target.files[0]; if(!f) return;
    const reader = new FileReader();
    reader.onload = ()=>{ try{ initFromCSV(String(reader.result)); }catch(ex){ err(ex.message || String(ex)); } };
    reader.readAsText(f);
  };

  // ALWAYS TREAT FIRST COLUMN AS ALTERNATIVE
  function initFromCSV(txt){
    const arr = parseCSVText(txt);
    if(!arr.length) throw new Error("Empty CSV");

    // sanitize headers to strings
    columns = arr[0].map(c => String(c ?? "").trim());

    // if any column is literally 'Alternative', move it to index 0;
    // else rename the first column to 'Alternative' (so it’s excluded from criteria/weights)
    if (columns.includes("Alternative")) {
      const idx = columns.indexOf("Alternative");
      if (idx !== 0) { const name = columns.splice(idx,1)[0]; columns.unshift(name); } // keep label but move to front
    } else {
      columns[0] = "Alternative";
    }

    // criteria = everything AFTER column 0
    crits = columns.slice(1);

    rows = arr.slice(1).filter(r=>r.length>=columns.length).map(r=>{
      const obj={}; columns.forEach((c,i)=> obj[c]=r[i] ?? ""); return obj;
    });

    // defaults
    types  = Object.fromEntries(crits.map(c=>[c,"Benefit"]));
    ideals = Object.fromEntries(crits.map(c=>[c,""]));
    weights= Object.fromEntries(crits.map(c=>[c,1]));

    renderMatrix();
    renderTypes();
    renderWeights();
    show($("matrixCard"),true);
    show($("typesCard"),true);
    show($("weightsCard"),true);
    show($("weightsGrid"), weightMode==='custom');
    show($("betaCard"),true);
    show($("resultCard"),false);
  }

  // PAPER EXAMPLE
  $("loadPaperBtn").onclick = ()=>{
    const paper = `Alternative,Cost,Quality,Delivery Time,Temperature
A1,200,8,4,30
A2,250,7,5,60
A3,300,9,6,85
`;
    initFromCSV(paper);
    types = { "Cost":"Cost", "Quality":"Benefit", "Delivery Time":"Cost", "Temperature":"Ideal (Goal)" };
    ideals["Temperature"] = "60";
    weightMode = 'equal'; $("wEqual").checked = true; $("wCustom").checked = false; show($("weightsGrid"), false);
    beta = 0.5; $("beta").value = "0.5"; $("betaVal").textContent = "0.50";
    renderTypes(); renderWeights();
    runSYAI();
  };

  // UI BUILDERS
  function renderMatrix(){
    const tb = $("matrixTable"); tb.innerHTML = "";
    const thead = document.createElement("thead"); const trh = document.createElement("tr");
    columns.forEach(c=>{ const th=document.createElement("th"); th.textContent=c; trh.appendChild(th); });
    thead.appendChild(trh); tb.appendChild(thead);
    const tbody = document.createElement("tbody");
    rows.slice(0,10).forEach(r=>{
      const tr=document.createElement("tr");
      columns.forEach(c=>{ const td=document.createElement("td"); td.textContent=String(r[c] ?? ""); tr.appendChild(td); });
      tbody.appendChild(tr);
    });
    tb.appendChild(tbody);
  }

  function renderTypes(){
    const wrap = $("typesGrid"); wrap.innerHTML="";
    crits.forEach(c=>{
      const box = document.createElement("div"); box.style.minWidth="240px";
      const lab = document.createElement("div"); lab.className="label"; lab.textContent=c; box.appendChild(lab);

      const sel = document.createElement("select");
      ["Benefit","Cost","Ideal (Goal)"].forEach(v=>{ const o=document.createElement("option"); o.textContent=v; sel.appendChild(o); });
      sel.value = types[c] || "Benefit";
      sel.onchange = ()=>{ types[c]=sel.value; renderTypes(); };
      box.appendChild(sel);

      if((types[c]||"") === "Ideal (Goal)"){
        const inp=document.createElement("input"); inp.className="mt2"; inp.type="number"; inp.step="any"; inp.placeholder="Goal value";
        inp.value = ideals[c] || "";
        inp.oninput = ()=> ideals[c] = inp.value;
        box.appendChild(inp);
      } else {
        delete ideals[c];
      }
      wrap.appendChild(box);
    });
  }

  function renderWeights(){
    const wrap = $("weightsGrid"); wrap.innerHTML="";
    crits.forEach(c=>{
      const box = document.createElement("div"); box.style.minWidth="160px";
      const lab = document.createElement("div"); lab.className="label"; lab.textContent = `w(${c})`; box.appendChild(lab);
      const inp=document.createElement("input"); inp.type="number"; inp.step="0.001"; inp.min="0"; inp.value = weights[c] ?? 0;
      inp.oninput = ()=> weights[c] = inp.value;
      box.appendChild(inp);
      wrap.appendChild(box);
    });
  }

  // SYAI core
  const C = 0.01;
  function toNum(v){ const x=parseFloat(String(v).replace(/,/g,"")); return isFinite(x)?x:NaN; }

  function normalizeColumn(vals, ctype, goal){
    const max = Math.max(...vals); const min = Math.min(...vals); const R = max - min;
    let xStar;
    if(ctype==="Benefit") xStar = max;
    else if(ctype==="Cost") xStar = min;
    else { const g=parseFloat(goal); xStar=isFinite(g)?g:(vals.reduce((s,v)=>s+(isFinite(v)?v:0),0)/vals.length); }
    if(Math.abs(R)<1e-12) return vals.map(_=>1.0);
    return vals.map(x=> Math.max(C, Math.min(1, C + (1-C)*(1-Math.abs(x-xStar)/R))));
  }

  function compute(){
    if(!columns.length || !rows.length){ err("No data"); return null; }
    const X = rows.map(r=> Object.fromEntries(crits.map(c=>[c,toNum(r[c])])) );
    const N = {};
    crits.forEach(c=>{
      const series = X.map(row=>row[c]);
      N[c] = normalizeColumn(series, types[c] || "Benefit", ideals[c]);
    });

    const w={};
    if(weightMode==='equal'){
      crits.forEach(c=> w[c]=1/crits.length);
    } else {
      let sumw = 0;
      crits.forEach(c=>{ const v=Math.max(0, parseFloat(weights[c]||0)); w[c]= isFinite(v)?v:0; sumw += w[c]; });
      if(sumw<=0) crits.forEach(c=> w[c]=1/crits.length); else crits.forEach(c=> w[c]/=sumw);
    }

    const W = rows.map((_,i)=> Object.fromEntries(crits.map(c=>[c, N[c][i]*w[c]])) );
    const Aplus={}, Aminus={};
    crits.forEach(c=>{
      let mx=-Infinity, mn=Infinity;
      W.forEach(row=>{ if(row[c]>mx) mx=row[c]; if(row[c]<mn) mn=row[c]; });
      Aplus[c]=mx; Aminus[c]=mn;
    });

    const res = rows.map((r,i)=>{
      let Dp=0, Dm=0;
      crits.forEach(c=>{ Dp += Math.abs(W[i][c]-Aplus[c]); Dm += Math.abs(W[i][c]-Aminus[c]); });
      const denom = beta*Dp + (1-beta)*Dm || Number.EPSILON;
      const Close = ((1-beta)*Dm)/denom;
      return { Alternative: String(r["Alternative"]), Dp, Dm, Close };
    });
    res.sort((a,b)=> b.Close - a.Close);
    res.forEach((r,i,arr)=> r.Rank = arr.slice(0,i).filter(x=>x.Close>r.Close).length + 1);
    return res;
  }

  $("runBtn").onclick = ()=>runSYAI();
  function runSYAI(){
    const result = compute(); if(!result) return;

    // table (black text)
    const tb = $("resultTable"); tb.innerHTML="";
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
    show($("resultCard"),true);

    drawBar(result.map(r=>({name:r.Alternative, value:r.Close})));
    drawLine(result.map(r=>({rank:r.Rank, value:r.Close, name:r.Alternative})));
  }

  // Charts + tooltips
  const PASTELS = ["#a5b4fc","#f9a8d4","#bae6fd","#bbf7d0","#fde68a","#c7d2fe","#fecdd3","#fbcfe8","#bfdbfe","#d1fae5"];
  let barRects=[], linePoints=[];

  function drawBar(data){
    const svg = $("barSVG"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    barRects.length = 0; hideTip();
    const rect = svg.getBoundingClientRect();
    const W = rect.width||800, H = rect.height||360, padL=50,padR=20,padT=18,padB=44;
    const max = Math.max(...data.map(d=>d.value)) || 1;
    const barW = (W - padL - padR) / data.length * 0.8;

    for(let t=0;t<=5;t++){
      const val = max*t/5;
      const y = H - padB - (H - padT - padB)*(val/max);
      const line = document.createElementNS("http://www.w3.org/2000/svg","line");
      line.setAttribute("x1", padL-6); line.setAttribute("x2", W-padR);
      line.setAttribute("y1", y); line.setAttribute("y2", y);
      line.setAttribute("stroke", "#374151"); line.setAttribute("stroke-dasharray","3 3");
      svg.appendChild(line);
      const tEl = document.createElementNS("http://www.w3.org/2000/svg","text");
      tEl.setAttribute("x", padL-10); tEl.setAttribute("y", y+4);
      tEl.setAttribute("text-anchor","end"); tEl.setAttribute("font-size","12");
      tEl.setAttribute("fill","#000"); tEl.textContent = val.toFixed(2);
      svg.appendChild(tEl);
    }

    data.forEach((d,i)=>{
      const x = padL + i*(W - padL - padR)/data.length + ((W - padL - padR)/data.length - barW)/2;
      const h = (H - padT - padB) * (d.value/max);
      const y = H - padB - h;

      const rectEl = document.createElementNS("http://www.w3.org/2000/svg","rect");
      rectEl.setAttribute("x", x); rectEl.setAttribute("y", y);
      rectEl.setAttribute("width", barW); rectEl.setAttribute("height", h);
      rectEl.setAttribute("fill", PASTELS[i%PASTELS.length]);
      svg.appendChild(rectEl);

      // value label (black)
      const txt = document.createElementNS("http://www.w3.org/2000/svg","text");
      txt.setAttribute("x", x + barW/2); txt.setAttribute("y", Math.max(y + 14, padT + 12));
      txt.setAttribute("text-anchor","middle"); txt.setAttribute("font-size","12"); txt.setAttribute("fill","#000");
      txt.textContent = (d.value).toFixed(3);
      svg.appendChild(txt);

      // x labels (black)
      const lbl = document.createElementNS("http://www.w3.org/2000/svg","text");
      lbl.setAttribute("x", x + barW/2); lbl.setAttribute("y", H - 12);
      lbl.setAttribute("text-anchor","middle"); lbl.setAttribute("font-size","12");
      lbl.setAttribute("fill","#000"); lbl.textContent = d.name;
      svg.appendChild(lbl);

      barRects.push({x, y, w:barW, h, d});
    });

    svg.onmousemove = (ev)=>{
      const b = svg.getBoundingClientRect(), mx = ev.clientX - b.left, my = ev.clientY - b.top;
      const hit = barRects.find(r => mx>=r.x && mx<=r.x+r.w && my>=r.y && my<=r.y+r.h);
      if(hit){
        showTip(`${hit.d.name} — <b>${hit.d.value.toFixed(6)}</b>`, ev.clientX, ev.clientY);
      }else hideTip();
    };
    svg.onmouseleave = hideTip;
  }

  function drawLine(data){
    const svg = $("lineSVG"); while(svg.firstChild) svg.removeChild(svg.firstChild);
    linePoints.length = 0; hideTip();

    const rect = svg.getBoundingClientRect();
    const W = rect.width||800, H = rect.height||300, padL=50,padR=20,padT=14,padB=30;
    const maxY = Math.max(...data.map(d=>d.value))||1, minX = 1, maxX = Math.max(...data.map(d=>d.rank))||1;

    const scaleX = (r)=> padL + (W-padL-padR) * ( (r-minX) / (maxX-minX||1) );
    const scaleY = (v)=> H - padB - (H-padT-padB) * (v/maxY);

    for(let t=0;t<=5;t++){
      const val = maxY*t/5;
      const y = H - padB - (H - padT - padB)*(val/maxY);
      const line = document.createElementNS("http://www.w3.org/2000/svg","line");
      line.setAttribute("x1", padL-6); line.setAttribute("x2", W-padR);
      line.setAttribute("y1", y); line.setAttribute("y2", y);
      line.setAttribute("stroke", "#374151"); line.setAttribute("stroke-dasharray","3 3");
      svg.appendChild(line);
      const tEl = document.createElementNS("http://www.w3.org/2000/svg","text");
      tEl.setAttribute("x", padL-10); tEl.setAttribute("y", y+4);
      tEl.setAttribute("text-anchor","end"); tEl.setAttribute("font-size","12");
      tEl.setAttribute("fill","#000"); tEl.textContent = val.toFixed(2);
      svg.appendChild(tEl);
    }

    const p = document.createElementNS("http://www.w3.org/2000/svg","path");
    let dstr = "";
    data.sort((a,b)=> a.rank - b.rank).forEach((pnt,idx)=>{
      const x=scaleX(pnt.rank), y=scaleY(pnt.value);
      dstr += (idx===0? "M":"L") + x + " " + y + " ";
      linePoints.push({x,y,info:pnt});
    });
    p.setAttribute("d", dstr.trim());
    p.setAttribute("fill","none"); p.setAttribute("stroke","#64748b"); p.setAttribute("stroke-width","2");
    svg.appendChild(p);

    linePoints.forEach(lp=>{
      const c = document.createElementNS("http://www.w3.org/2000/svg","circle");
      c.setAttribute("cx",lp.x); c.setAttribute("cy",lp.y); c.setAttribute("r","4"); c.setAttribute("fill","#94a3b8");
      svg.appendChild(c);
      const t = document.createElementNS("http://www.w3.org/2000/svg","text");
      t.setAttribute("x",lp.x+6); t.setAttribute("y",lp.y-6); t.setAttribute("font-size","12"); t.setAttribute("fill","#000");
      t.textContent = lp.info.value.toFixed(3); svg.appendChild(t);
    });

    for(let r=1;r<=maxX;r++){
      const x=scaleX(r);
      const t = document.createElementNS("http://www.w3.org/2000/svg","text");
      t.setAttribute("x",x); t.setAttribute("y",H-8); t.setAttribute("text-anchor","middle"); t.setAttribute("font-size","12"); t.setAttribute("fill","#000");
      t.textContent = r; svg.appendChild(t);
    }

    svg.onmousemove = (ev)=>{
      const b = svg.getBoundingClientRect(), mx = ev.clientX - b.left, my = ev.clientY - b.top;
      let best=null, dist=1e9;
      linePoints.forEach(lp=>{
        const d = Math.hypot(lp.x-mx, lp.y-my);
        if(d<dist){ dist=d; best=lp; }
      });
      if(best && dist<12){
        const i = best.info;
        showTip(`${i.name || "Alt"} — <b>${i.value.toFixed(6)}</b> (Rank ${i.rank})`, ev.clientX, ev.clientY);
      } else hideTip();
    };
    svg.onmouseleave = hideTip;
  }
})();
</script>
</body>
</html>
"""

components.html(html, height=2200, scrolling=True)
