# app.py
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SYAI-Rank (Web UI inside Streamlit)", layout="wide")

# Optional shell styling
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #0b0b0f 0%, #0b0b0f 35%, #ffe4e6 120%) !important; }
[data-testid="stSidebar"] { background: rgba(255, 228, 230, 0.08) !important; backdrop-filter: blur(6px); }
</style>
""", unsafe_allow_html=True)

html = r"""
<!doctype html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>SYAI-Rank</title>

  <!-- React + ReactDOM (UMD) from jsDelivr (stable) -->
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18/umd/react-dom.production.min.js"></script>

  <!-- PapaParse -->
  <script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>

  <!-- Recharts UMD -->
  <script src="https://cdn.jsdelivr.net/npm/recharts@2.10.4/umd/Recharts.min.js"></script>

  <!-- Basic CSS (grey + pink) -->
  <style>
    :root {
      --bg-dark: #0b0b0f;
      --card-dark: #0f1115;
      --card-light: #ffffffcc;
      --text-light: #f5f5f5;
      --text-dark: #1f2937;
      --pink: #ec4899;
      --pink-700: #db2777;
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; margin: 0; }
    body {
      color: var(--text-light);
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial;
      background: linear-gradient(180deg, var(--bg-dark) 0%, var(--bg-dark) 35%, #ffe4e6 120%);
    }
    .container { max-width: 1200px; margin: 24px auto; padding: 0 16px; }
    .header { display:flex; align-items:center; justify-content:space-between; margin-bottom: 16px; }
    .title { font-weight: 800; font-size: 28px; color: #fce7f3; }
    .btn { display:inline-flex; align-items:center; gap:8px; padding:10px 14px; border-radius: 12px; border:1px solid var(--pink-700); background:var(--pink); color:white; cursor:pointer; }
    .btn:hover { background: var(--pink-700); }
    .toggle { padding:8px 12px; border-radius: 12px; border:1px solid #333; background:#111; color:#eee; cursor:pointer; }
    .tabs { display:flex; gap:8px; margin: 12px 0; }
    .tab { padding:10px 14px; border-radius: 12px; border:1px solid #333; background:#202329; color:#ddd; cursor:pointer; }
    .tab.active { background: var(--pink); border-color: var(--pink-700); color:#fff; }
    .grid { display:grid; gap:16px; grid-template-columns: 1fr; }
    @media (min-width: 1024px) { .grid { grid-template-columns: 1fr 2fr; } }
    .card { background: linear-gradient(180deg, #ffffffb3 0%, #ffffffcc 100%); color: var(--text-dark); border-radius: 16px; padding: 18px; border: 1px solid #fbcfe8; backdrop-filter: blur(6px); }
    .card.dark { background: #0f1115b3; color: #e5e7eb; border-color: #262b35; }
    .section-title { font-weight: 700; font-size: 18px; margin-bottom: 12px; color:#f9a8d4; }
    .label { display:block; font-size: 12px; opacity:.8; margin-bottom: 4px; }
    input[type="text"], input[type="number"], select {
      width: 100%; padding:10px 12px; border-radius:10px; border:1px solid #ddd; background:#f8fafc; color:#111;
    }
    .dark input[type="text"], .dark input[type="number"], .dark select {
      background:#1f2937; border-color:#374151; color:#e5e7eb;
    }
    .table-wrap { overflow:auto; max-height: 360px; }
    table { width:100%; border-collapse: collapse; font-size: 14px; }
    th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #e5e7eb; }
    .dark th, .dark td { border-bottom-color: #2a2f38; }
    .hint { font-size: 12px; opacity:.8; }
    .row { display:flex; gap:12px; align-items:center; flex-wrap: wrap; }
    .mt6 { margin-top: 24px; } .mb6 { margin-bottom: 24px; } .mt2 { margin-top: 8px; }
    .w100 { width: 100%; }

    /* error banner inside the iframe */
    #err {
      position: sticky; top: 0; z-index: 9999;
      display: none; background: #7f1d1d; color: #fff; padding: 10px 12px; border-radius: 8px; margin: 8px 16px;
      border: 1px solid #fecaca;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      white-space: pre-wrap;
    }
  </style>
</head>
<body>
  <div id="err"></div>
  <div id="root"></div>

  <script>
    // Small helper: show JS errors visibly rather than a blank page
    function showError(msg) {
      try {
        const el = document.getElementById('err');
        el.textContent = "Error: " + msg;
        el.style.display = 'block';
      } catch(_) {}
      console.error(msg);
    }

    // Wait for libs to be available
    function waitForLibs(tries=80) {
      return new Promise((resolve, reject) => {
        (function check() {
          if (window.React && window.ReactDOM && window.Papa && window.Recharts) return resolve();
          if (--tries <= 0) return reject(new Error("Libraries failed to load. (React/Papa/Recharts)"));
          setTimeout(check, 100);
        })();
      });
    }

    (async function boot() {
      try {
        await waitForLibs();

        const { useState, useMemo, useEffect } = React;
        const {
          ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid,
          Tooltip, LabelList, LineChart, Line, Cell
        } = Recharts;

        const C = 0.01;
        const sampleCSV =
`Alternative,Cost,Quality,Delivery Time,Temperature
A1,200,8,4,30
A2,250,7,5,60
A3,300,9,6,85
`;

        function parseCSV(file, onDone) {
          Papa.parse(file, {
            header: true, skipEmptyLines: true,
            complete: (res) => onDone({ columns: res.meta.fields || [], rows: res.data || [] }),
          });
        }

        function computeSYAI({ rows, columns, types, ideals, rawWeights, beta }) {
          const crits = columns.filter(c => c !== "Alternative");
          const m = crits.length;

          const alts = Array.from(new Set(rows.map(r => String(r["Alternative"])).filter(Boolean)));

          const X = {}; alts.forEach(a => X[a] = {});
          rows.forEach(r => {
            const a = String(r["Alternative"]);
            crits.forEach(c => {
              const v = parseFloat(String(r[c]).replace(/,/g, ""));
              X[a][c] = Number.isFinite(v) ? v : NaN;
            });
          });

          const N = {}; alts.forEach(a => N[a] = {});
          crits.forEach(c => {
            const colVals = alts.map(a => X[a][c]);
            const max = Math.max(...colVals);
            const min = Math.min(...colVals);
            const R = max - min;
            let xStar;
            if (types[c] === "Benefit") xStar = max;
            else if (types[c] === "Cost") xStar = min;
            else {
              const g = parseFloat(ideals[c]);
              xStar = Number.isFinite(g) ? g : colVals.reduce((s,v)=>s+(Number.isFinite(v)?v:0),0)/colVals.length;
            }
            if (Math.abs(R) < 1e-12) {
              alts.forEach(a => N[a][c] = 1.0);
            } else {
              alts.forEach(a => {
                const x = X[a][c];
                const norm = C + (1 - C) * (1 - Math.abs(x - xStar)/R);
                N[a][c] = Math.max(C, Math.min(1, norm));
              });
            }
          });

          const w = {}; let sumw = 0;
          crits.forEach(c => {
            const v = parseFloat(String(rawWeights[c] ?? 0));
            const safe = Number.isFinite(v) ? Math.max(0, v) : 0;
            w[c] = safe; sumw += safe;
          });
          if (sumw <= 0) crits.forEach(c => w[c] = 1/m); else crits.forEach(c => w[c] = w[c]/sumw);

          const W = {}; alts.forEach(a => W[a] = {});
          const A_plus = {}, A_minus = {};
          crits.forEach(c => {
            let max = -Infinity, min = Infinity;
            alts.forEach(a => {
              W[a][c] = N[a][c] * w[c];
              if (W[a][c] > max) max = W[a][c];
              if (W[a][c] < min) min = W[a][c];
            });
            A_plus[c] = max; A_minus[c] = min;
          });

          const rowsOut = alts.map(a => {
            let Dp = 0, Dm = 0;
            crits.forEach(c => { Dp += Math.abs(W[a][c] - A_plus[c]); Dm += Math.abs(W[a][c] - A_minus[c]); });
            const denom = beta*Dp + (1-beta)*Dm || Number.EPSILON;
            const closeness = ((1-beta) * Dm) / denom;
            return { Alternative: a, Dp, Dm, Closeness: closeness };
          });

          rowsOut.sort((a,b) => b.Closeness - a.Closeness);
          rowsOut.forEach((r,i,arr) => {
            r.Rank = arr.slice(0,i).filter(x => x.Closeness > r.Closeness).length + 1;
          });

          return { resRows: rowsOut };
        }

        function App() {
          const [isDark, setIsDark] = useState(true);
          useEffect(() => { document.documentElement.classList.toggle('dark', isDark); }, [isDark]);

          const [tab, setTab] = useState("rank");
          const [data, setData] = useState({ columns: [], rows: [] });
          const [types, setTypes] = useState({});
          const [ideals, setIdeals] = useState({});
          const [weights, setWeights] = useState({});
          const [beta, setBeta] = useState(0.5);

          const [urlScatter, setUrlScatter] = useState("");
          const [urlCorr, setUrlCorr] = useState("");

          const onCSVLoaded = ({ columns, rows }) => {
            if (!columns?.length) return;
            let cols = columns;
            if (cols[0] !== "Alternative") {
              cols = ["Alternative", ...cols.filter(c => c !== "Alternative")];
            }
            const crits = cols.filter(c => c !== "Alternative");
            const t = {...types}, w = {...weights}, g = {...ideals};
            crits.forEach(c => {
              if (!t[c]) t[c] = "Benefit";
              if (!(c in w)) w[c] = 1;
              if (!(c in g)) g[c] = "";
            });
            setTypes(t); setWeights(w); setIdeals(g);
            setData({ columns: cols, rows });
          };

          const result = useMemo(() => {
            if (!data.columns.length || !data.rows.length) return null;
            const crits = data.columns.filter(c=>c!=="Alternative");
            if (!crits.length) return null;
            return computeSYAI({ rows: data.rows, columns: data.columns, types, ideals, rawWeights: weights, beta });
          }, [data, types, ideals, weights, beta]);

          const neutral = ["#64748b","#94a3b8","#cbd5e1","#475569","#334155","#1f2937","#9ca3af","#6b7280","#a3a3a3","#737373"];

          return React.createElement("div", { className:"container" },
            React.createElement("div", { className:"header" },
              React.createElement("div", { className:"title" }, "SYAI-Rank"),
              React.createElement("div", { className:"row" },
                React.createElement("a", {
                  className: "btn",
                  href: "data:text/csv;charset=utf-8," + encodeURIComponent(
                    "Alternative,Cost,Quality,Delivery Time,Temperature\nA1,200,8,4,30\nA2,250,7,5,60\nA3,300,9,6,85\n"
                  ),
                  download: "sample.csv"
                }, "⬇️ Sample CSV"),
                React.createElement("button", { className:"toggle", onClick:()=>setIsDark(!isDark) },
                  isDark ? "🌙 Dark" : "☀️ Light"
                )
              )
            ),

            React.createElement("div", { className:"tabs" },
              React.createElement("button", { className: "tab " + (tab==="rank"?"active":""), onClick:()=>setTab("rank") }, "SYAI Ranking"),
              React.createElement("button", { className: "tab " + (tab==="compare"?"active":""), onClick:()=>setTab("compare") }, "Comparison with Other Methods"),
            ),

            tab === "rank" && React.createElement("div", { className:"grid" },
              // Left
              React.createElement("div", null,
                React.createElement("div", { className:"card dark" },
                  React.createElement("div", { className:"section-title" }, "Step 1: Upload Decision Matrix"),
                  React.createElement("label", { className:"btn", htmlFor:"csvFile" }, "📤 Choose CSV"),
                  React.createElement("input", { id:"csvFile", type:"file", accept:".csv", style:{display:"none"},
                    onChange:(e)=>{ const f = e.target.files?.[0]; if (f) parseCSV(f, onCSVLoaded); } }),
                  React.createElement("p", { className:"hint mt2" }, "First column must be ", React.createElement("b", null, "Alternative"), ".")
                ),

                !!data.columns.length && React.createElement("div", { className:"card dark" },
                  React.createElement("div", { className:"section-title" }, "Step 2: Define Criteria Types"),
                  React.createElement("div", { className:"row" },
                    data.columns.filter(c=>c!=="Alternative").map((c)=>
                      React.createElement("div", { key:c, style:{minWidth:240}},
                        React.createElement("div", { className:"label" }, c),
                        React.createElement("select", {
                          value: types[c] || "Benefit",
                          onChange:(e)=> setTypes({...types, [c]: e.target.value})
                        },
                          React.createElement("option", null, "Benefit"),
                          React.createElement("option", null, "Cost"),
                          React.createElement("option", null, "Ideal (Goal)")
                        ),
                        (types[c]==="Ideal (Goal)") && React.createElement("input", {
                          className:"mt2", type:"number", step:"any", placeholder:"Goal value",
                          value: String(ideals[c] ?? ""),
                          onChange:(e)=> setIdeals({...ideals, [c]: e.target.value})
                        })
                      )
                    )
                  )
                ),

                !!data.columns.length && React.createElement("div", { className:"card dark" },
                  React.createElement("div", { className:"section-title" }, "Step 3: Set Weights (raw; normalized on run)"),
                  React.createElement("div", { className:"row" },
                    data.columns.filter(c=>c!=="Alternative").map((c)=>
                      React.createElement("div", { key:c, style:{minWidth:160}},
                        React.createElement("div", { className:"label" }, "w(", c, ")"),
                        React.createElement("input", {
                          type:"number", step:"0.001", min:"0",
                          value: String(weights[c] ?? 0),
                          onChange:(e)=> setWeights({...weights, [c]: e.target.value})
                        })
                      )
                    )
                  )
                ),

                !!data.columns.length && React.createElement("div", { className:"card dark" },
                  React.createElement("div", { className:"section-title" }, "Step 4: β (blend of D⁺ and D⁻)"),
                  React.createElement("input", { type:"range", min:0, max:1, step:0.01, value:beta,
                    onChange:(e)=> setBeta(parseFloat(e.target.value)), className:"w100" }),
                  React.createElement("div", { className:"hint mt2" }, "β = ", React.createElement("b", null, beta.toFixed(2)))
                )
              ),

              // Right
              React.createElement("div", null,
                !!data.columns.length && React.createElement("div", { className:"card" },
                  React.createElement("div", { className:"section-title" }, "Decision Matrix (first 10 rows)"),
                  React.createElement("div", { className:"table-wrap" },
                    React.createElement("table", null,
                      React.createElement("thead", null,
                        React.createElement("tr", null,
                          data.columns.map(c => React.createElement("th", { key:c }, c))
                        )
                      ),
                      React.createElement("tbody", null,
                        (data.rows || []).slice(0,10).map((r, i) =>
                          React.createElement("tr", { key:i },
                            data.columns.map(c => React.createElement("td", { key:c }, String(r[c] ?? "")))
                          )
                        )
                      )
                    )
                  )
                ),

                !!result && React.createElement("div", { className:"card" },
                  React.createElement("div", { className:"section-title" }, "Final Ranking (SYAI)"),
                  React.createElement("div", { className:"table-wrap" },
                    React.createElement("table", null,
                      React.createElement("thead", null,
                        React.createElement("tr", null,
                          React.createElement("th", null, "Alternative"),
                          React.createElement("th", null, "D+"),
                          React.createElement("th", null, "D-"),
                          React.createElement("th", null, "Closeness"),
                          React.createElement("th", null, "Rank")
                        )
                      ),
                      React.createElement("tbody", null,
                        result.resRows.map(r =>
                          React.createElement("tr", { key:r.Alternative },
                            React.createElement("td", null, r.Alternative),
                            React.createElement("td", null, r.Dp.toFixed(6)),
                            React.createElement("td", null, r.Dm.toFixed(6)),
                            React.createElement("td", null, r.Closeness.toFixed(6)),
                            React.createElement("td", null, r.Rank)
                          )
                        )
                      )
                    )
                  ),

                  React.createElement("div", { className:"mt6" },
                    React.createElement("div", { className:"hint mb6" }, "Ranking — Bar"),
                    React.createElement("div", { style:{ width:"100%", height:"340px" } },
                      React.createElement(ResponsiveContainer, null,
                        React.createElement(BarChart, { data: result.resRows.map(r=>({ name:r.Alternative, value:r.Closeness })) , margin:{ top:10, right:20, left:0, bottom:30 } },
                          React.createElement(CartesianGrid, { strokeDasharray:"3 3" }),
                          React.createElement(XAxis, { dataKey:"name", angle:-25, textAnchor:"end", interval:0, height:50 }),
                          React.createElement(YAxis, null),
                          React.createElement(Tooltip, { formatter: (v)=> Number(v).toFixed(6) }),
                          React.createElement(Bar, { dataKey:"value" },
                            result.resRows.map((_, i) =>
                              React.createElement(Cell, { key:i, fill: ["#64748b","#94a3b8","#cbd5e1","#475569","#334155","#1f2937","#9ca3af","#6b7280","#a3a3a3","#737373"][i%10] })
                            ),
                            React.createElement(LabelList, { dataKey:"value", position:"top", formatter:(v)=> Number(v).toFixed(3) })
                          )
                        )
                      )
                    )
                  ),

                  React.createElement("div", { className:"mt6" },
                    React.createElement("div", { className:"hint mb6" }, "Ranking — Line"),
                    React.createElement("div", { style:{ width:"100%", height:"300px" } },
                      React.createElement(ResponsiveContainer, null,
                        React.createElement(LineChart, { data: result.resRows.map(r=>({ rank:r.Rank, value:r.Closeness, name:r.Alternative })) , margin:{ top:10, right:20, left:0, bottom:10 } },
                          React.createElement(CartesianGrid, { strokeDasharray:"3 3" }),
                          React.createElement(XAxis, { dataKey:"rank" }),
                          React.createElement(YAxis, null),
                          React.createElement(Tooltip, { formatter: (v)=> Number(v).toFixed(6), labelFormatter:(l)=> "Rank " + l }),
                          React.createElement(Line, { type:"monotone", dataKey:"value", stroke:"#64748b", dot:true })
                        )
                      )
                    )
                  )
                )
              )
            ),

            tab === "compare" && React.createElement("div", { className:"grid" },
              React.createElement("div", { className:"card dark" },
                React.createElement("div", { className:"section-title" }, "Load Images (URLs)"),
                React.createElement("div", { className:"label" }, "Scatter matrix image URL (raw GitHub/public)"),
                React.createElement("input", { type:"text", value: urlScatter, onChange:(e)=> setUrlScatter(e.target.value) }),
                urlScatter && React.createElement("img", { src:urlScatter, alt:"scatter", style:{width:"100%", borderRadius:12, border:"1px solid #2a2f38", marginTop:8} }),
                React.createElement("div", { className:"label mt2" }, "Correlation heatmap image URL (raw GitHub/public)"),
                React.createElement("input", { type:"text", value: urlCorr, onChange:(e)=> setUrlCorr(e.target.value) }),
                urlCorr && React.createElement("img", { src:urlCorr, alt:"corr", style:{width:"100%", borderRadius:12, border:"1px solid #2a2f38", marginTop:8} }),
                React.createElement("p", { className:"hint mt2" }, "Use direct links that end with .png/.jpg (GitHub: click “Download raw file”).")
              ),

              React.createElement("div", { className:"card" },
                React.createElement("div", { className:"section-title" }, "How to read the figures"),
                React.createElement("ul", null,
                  React.createElement("li", null, React.createElement("b", null, "Scatter matrix"), " shows pairwise score relationships (each dot = one alternative)."),
                  React.createElement("li", null, React.createElement("b", null, "Correlation heatmap"), " highlights similarity of scores/rankings across methods (darker = stronger agreement)."),
                  React.createElement("li", null, "Use these to validate whether SYAI trends align with or diverge from other methods.")
                )
              )
            )
          );
        }

        const root = ReactDOM.createRoot(document.getElementById("root"));
        root.render(React.createElement(App));
      } catch (err) {
        showError(err && err.message ? err.message : String(err));
      }
    })();
  </script>
</body>
</html>
"""

# Render the embedded React app inside Streamlit
components.html(html, height=2000, scrolling=True)
