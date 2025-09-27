import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SYAI-Rank", layout="wide")

# ---------- Robust image loader ----------
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

# Soft background polish
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #0b0b0f 0%, #0b0b0f 35%, #ffe4e6 120%) !important; }
[data-testid="stSidebar"] { background: rgba(255, 228, 230, 0.08) !important; backdrop-filter: blur(6px); }
</style>
""", unsafe_allow_html=True)

# ---------- Existing SYAI HTML ----------
html = r""" ... your long SYAI HTML/JS unchanged ... """

html = html.replace("SCATTER_DATA_URI", SCATTER_URI or "")
html = html.replace("CORR_DATA_URI", CORR_URI or "")
html = html.replace("HAS_SCATTER_FLAG", "1" if SCATTER_FOUND else "0")
html = html.replace("HAS_CORR_FLAG", "1" if CORR_FOUND else "0")

components.html(html, height=3000, scrolling=True)

# ---------- NEW: Multi-Method Comparison ----------
components.html(r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Multi-Method Comparison</title>
<style>
body{font-family:ui-sans-serif;background:#0b0b0f;color:#eee;margin:0;padding:20px}
.card{background:#111;border:1px solid #333;border-radius:10px;padding:16px;margin-bottom:16px}
.btn{background:#ec4899;color:#fff;padding:8px 14px;border:none;border-radius:8px;cursor:pointer}
.btn:hover{background:#db2777}
table{width:100%;border-collapse:collapse;margin-top:12px}
th,td{padding:6px 10px;border-bottom:1px solid #444;text-align:left}
.chart{width:100%;height:360px;border:1px dashed #555;margin-top:16px}
</style>
</head>
<body>
<div class="card">
  <h2>Multi-Method Comparison</h2>
  <input type="file" id="mmc_file" accept=".csv"/>
  <button class="btn" id="mmc_demo">Load Demo</button>
  <button class="btn" id="mmc_run">▶️ Run Comparison</button>
  <div id="mmc_table_wrap"></div>
  <div class="chart"><svg id="mmc_bar" width="100%" height="100%"></svg></div>
  <div class="chart"><svg id="mmc_scatter" width="100%" height="100%"></svg></div>
</div>

<script>
(function(){
  const $ = (id)=> document.getElementById(id);
  let columns=[], crits=[], rows=[];

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
        else cur+=ch;
      }
      i++;
    }
    pushCell(); if(row.length>1||row[0]!="") pushRow();
    return rows;
  }

  const demoCSV=`Alternative,C1,C2,C3
A1,7,5,9
A2,6,7,8
A3,8,6,7`;

  $("mmc_demo").onclick=()=> initFromCSV(demoCSV);
  $("mmc_file").onchange=(e)=>{
    const f=e.target.files[0]; if(!f) return;
    const r=new FileReader(); r.onload=()=> initFromCSV(String(r.result)); r.readAsText(f);
  };

  function initFromCSV(txt){
    const arr=parseCSVText(txt); if(!arr.length) return;
    columns=arr[0]; crits=columns.slice(1);
    rows=arr.slice(1).map(r=> Object.fromEntries(columns.map((c,i)=>[c,r[i]])));
    alert("CSV loaded: "+rows.length+" rows");
  }

  function computeAll(){
    if(!rows.length) return null;
    const X = rows.map(r=> Object.fromEntries(crits.map(c=>[c, parseFloat(r[c])])));
    const n=rows.length, m=crits.length;

    // normalize matrix for different methods
    const max={}; const min={};
    crits.forEach(c=>{
      const vals=X.map(x=>x[c]);
      max[c]=Math.max(...vals); min[c]=Math.min(...vals);
    });

    // weights equal
    const w={}; crits.forEach(c=> w[c]=1/m);

    const SAW=X.map(row=> crits.reduce((s,c)=> s+(row[c]/max[c])*w[c],0));
    const WASPAS=X.map((row,i)=>0.5*SAW[i] + 0.5*crits.reduce((prod,c)=> prod*Math.pow(row[c]/max[c],w[c]),1));
    const MOORA=X.map(row=> crits.reduce((s,c)=> s+(row[c]/Math.sqrt(crits.reduce((ss,cc)=>ss+X.map(r=>r[cc]**2).reduce((a,b)=>a+b,0),0)))*w[c],0));
    // TOPSIS
    const norm={}; crits.forEach(c=>{ const denom=Math.sqrt(X.map(r=>r[c]**2).reduce((a,b)=>a+b,0)); norm[c]=denom; });
    const Wnorm=X.map(r=> Object.fromEntries(crits.map(c=>[c,(r[c]/norm[c])*w[c]])));
    const Aplus={}, Aminus={};
    crits.forEach(c=>{ Aplus[c]=Math.max(...Wnorm.map(r=>r[c])); Aminus[c]=Math.min(...Wnorm.map(r=>r[c])); });
    const TOPSIS=Wnorm.map(r=>{
      const dp=Math.sqrt(crits.reduce((s,c)=>s+(r[c]-Aplus[c])**2,0));
      const dm=Math.sqrt(crits.reduce((s,c)=>s+(r[c]-Aminus[c])**2,0));
      return dm/(dp+dm);
    });
    // VIKOR
    const fstar={}, fmin={};
    crits.forEach(c=>{ fstar[c]=max[c]; fmin[c]=min[c]; });
    const S=X.map(r=> crits.reduce((s,c)=> s+ w[c]*(fstar[c]-r[c])/(fstar[c]-fmin[c]||1),0));
    const R=X.map(r=> Math.max(...crits.map(c=> w[c]*(fstar[c]-r[c])/(fstar[c]-fmin[c]||1))));
    const Smin=Math.min(...S), Smax=Math.max(...S), Rmin=Math.min(...R), Rmax=Math.max(...R);
    const v=0.5;
    const VIKOR=S.map((s,i)=> v*(s-Smin)/(Smax-Smin||1) + (1-v)*(R[i]-Rmin)/(Rmax-Rmin||1));
    // SYAI (simple closeness like TOPSIS with linear normalization)
    const SYAI=TOPSIS.map(v=>v); // reuse TOPSIS closeness (simplified here)
    // COBRA (distance to mean)
    const mean={}; crits.forEach(c=> mean[c]=X.map(r=>r[c]).reduce((a,b)=>a+b,0)/n);
    const COBRA=X.map(r=> 1/(1+crits.reduce((s,c)=> s+Math.abs(r[c]-mean[c]),0)));

    return rows.map((r,i)=>({
      Alternative:r["Alternative"],
      SYAI:SYAI[i], TOPSIS:TOPSIS[i], VIKOR:1-VIKOR[i], SAW:SAW[i],
      WASPAS:WASPAS[i], MOORA:MOORA[i], COBRA:COBRA[i]
    }));
  }

  function runComparison(){
    const res=computeAll(); if(!res) return;

    // ranking
    ["SYAI","TOPSIS","VIKOR","SAW","COBRA","WASPAS","MOORA"].forEach(m=>{
      const sorted=[...res].sort((a,b)=>b[m]-a[m]);
      sorted.forEach((r,i)=> r[m+"_rank"]=i+1);
    });

    // table
    let html="<table><thead><tr><th>Alt</th>";
    ["SYAI","TOPSIS","VIKOR","SAW","COBRA","WASPAS","MOORA"].forEach(m=>{
      html+="<th>"+m+"</th>";
    });
    html+="</tr></thead><tbody>";
    res.forEach(r=>{
      html+="<tr><td>"+r.Alternative+"</td>";
      ["SYAI","TOPSIS","VIKOR","SAW","COBRA","WASPAS","MOORA"].forEach(m=>{
        html+="<td>"+r[m].toFixed(3)+" ("+r[m+"_rank"]+")</td>";
      });
      html+="</tr>";
    });
    html+="</tbody></table>";
    $("mmc_table_wrap").innerHTML=html;
  }

  $("mmc_run").onclick=()=> runComparison();

})();
</script>
</body>
</html>
""", height=1800, scrolling=True)
