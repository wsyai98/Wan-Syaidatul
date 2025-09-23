import React, { useMemo, useState } from "react";
import Papa from "papaparse";
import { Download, Upload, Image as ImageIcon, BarChart3, LineChart as LineChartIcon } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, LabelList, Cell } from "recharts";

// --- Styling helpers ---
const card = "rounded-2xl shadow p-5 bg-white/70 dark:bg-neutral-900/70 backdrop-blur";
const sectionTitle = "text-xl font-semibold mb-3";

// Core constants
const C = 0.01; // normalization floor

// Utility: parse CSV text to {columns, rows}
function parseCSV(file, onDone) {
  Papa.parse(file, {
    header: true,
    skipEmptyLines: true,
    complete: (results) => {
      const rows = results.data;
      const columns = results.meta.fields || [];
      onDone({ columns, rows });
    },
  });
}

// Core math in JS (mirrors your Python)
function computeSYAI({ rows, columns, types, ideals, rawWeights, beta }) {
  const crits = columns.filter((c) => c !== "Alternative");
  const m = crits.length;

  // Build numeric matrix X[alt][col]
  const alts = rows.map((r) => String(r["Alternative"]))
    .filter((v, i, a) => v && a.indexOf(v) === i);

  const X = {};
  alts.forEach((a) => (X[a] = {}));
  rows.forEach((r) => {
    const a = String(r["Alternative"]);
    crits.forEach((c) => {
      const v = parseFloat(String(r[c]).replace(/,/g, ""));
      X[a][c] = isFinite(v) ? v : NaN;
    });
  });

  // Normalize per column
  const N = {}; // normalized
  alts.forEach((a) => (N[a] = {}));

  crits.forEach((c, j) => {
    const colVals = alts.map((a) => X[a][c]);
    const max = Math.max(...colVals);
    const min = Math.min(...colVals);
    const R = max - min;

    let x_star;
    if (types[c] === "Benefit") x_star = max;
    else if (types[c] === "Cost") x_star = min;
    else {
      const g = parseFloat(ideals[c]);
      x_star = isFinite(g) ? g : colVals.reduce((s, v) => s + (isFinite(v) ? v : 0), 0) / colVals.length;
    }

    if (Math.abs(R) < 1e-12) {
      alts.forEach((a) => (N[a][c] = 1.0));
    } else {
      alts.forEach((a) => {
        const x = X[a][c];
        const norm = C + (1 - C) * (1 - Math.abs(x - x_star) / R);
        N[a][c] = Math.max(C, Math.min(1.0, norm));
      });
    }
  });

  // Weights: normalize raw to sum=1 (fallback to equal)
  let w = {};
  let sumw = 0;
  crits.forEach((c) => {
    const v = parseFloat(rawWeights[c]);
    const safe = isFinite(v) ? Math.max(0, v) : 0;
    w[c] = safe;
    sumw += safe;
  });
  if (sumw <= 0) {
    crits.forEach((c) => (w[c] = 1 / m));
  } else {
    crits.forEach((c) => (w[c] = w[c] / sumw));
  }

  // Weighted matrix + A+/A-
  const W = {};
  alts.forEach((a) => (W[a] = {}));
  const A_plus = {}, A_minus = {};
  crits.forEach((c) => {
    let max = -Infinity, min = Infinity;
    alts.forEach((a) => {
      W[a][c] = N[a][c] * w[c];
      if (W[a][c] > max) max = W[a][c];
      if (W[a][c] < min) min = W[a][c];
    });
    A_plus[c] = max;
    A_minus[c] = min;
  });

  // Distances and closeness
  const resRows = alts.map((a) => {
    let Dp = 0, Dm = 0;
    crits.forEach((c) => {
      Dp += Math.abs(W[a][c] - A_plus[c]);
      Dm += Math.abs(W[a][c] - A_minus[c]);
    });
    const denom = beta * Dp + (1 - beta) * Dm || Number.EPSILON;
    const closeness = ((1 - beta) * Dm) / denom;
    return { Alternative: a, Dp, Dm, Closeness: closeness };
  });

  resRows.sort((a, b) => b.Closeness - a.Closeness);
  resRows.forEach((r, i, arr) => {
    // Rank with ties: method "min"
    if (i === 0) r.Rank = 1;
    else r.Rank = (arr.slice(0, i + 1).filter(x => x.Closeness > r.Closeness).length) + 1;
  });

  return { alts, crits, X, N, W, A_plus, A_minus, w, resRows };
}

// Sample CSV string
export default function App() {
  const sampleCSV = `Alternative,Cost,Quality,Delivery Time,Temperature\nA1,200,8,4,30\nA2,250,7,5,60\nA3,300,9,6,85\n`;

  const [data, setData] = useState({ columns: [], rows: [] });
  const [types, setTypes] = useState({});
  const [ideals, setIdeals] = useState({});
  const [weights, setWeights] = useState({});
  const [beta, setBeta] = useState(0.5);
  const [activeTab, setActiveTab] = useState("rank");
  const [urlScatter, setUrlScatter] = useState("");
  const [urlCorr, setUrlCorr] = useState("");

  // When CSV changes, init type/weight defaults
  const onCSVLoaded = ({ columns, rows }) => {
    if (!columns?.length) return;
    // Ensure first column is Alternative
    if (columns[0] !== "Alternative") {
      // try to coerce
      columns = ["Alternative", ...columns.filter((c) => c !== "Alternative")];
    }
    const crits = columns.filter((c) => c !== "Alternative");
    const t = { ...types }, w = { ...weights }, g = { ...ideals };
    crits.forEach((c) => {
      if (!t[c]) t[c] = "Benefit";
      if (!(c in w)) w[c] = 1;
      if (!(c in g)) g[c] = "";
    });
    setTypes(t);
    setWeights(w);
    setIdeals(g);
    setData({ columns, rows });
  };

  // Compute
  const result = useMemo(() => {
    if (!data.columns.length || !data.rows.length) return null;
    const crits = data.columns.filter((c) => c !== "Alternative");
    if (!crits.length) return null;
    return computeSYAI({ rows: data.rows, columns: data.columns, types, ideals, rawWeights: weights, beta });
  }, [data, types, ideals, weights, beta]);

  const resultTable = useMemo(() => {
    if (!result) return null;
    return result.resRows.map((r) => ({ Alternative: r.Alternative, "D+": r.Dp, "D-": r.Dm, Closeness: r.Closeness, Rank: r.Rank }));
  }, [result]);

  const colorPalette = [
    "#4C78A8","#F58518","#E45756","#72B7B2","#54A24B","#EECA3B","#B279A2","#FF9DA6","#9D755D","#BAB0AC"
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl md:text-3xl font-bold">SYAI‑Rank — Web Interface</h1>
        <a
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 text-white shadow hover:bg-blue-700"
          href={`data:text/csv;charset=utf-8,${encodeURIComponent(sampleCSV)}`}
          download="sample.csv"
        >
          <Download size={18}/> Sample CSV
        </a>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        <button onClick={() => setActiveTab("rank")} className={`px-4 py-2 rounded-xl ${activeTab==='rank' ? 'bg-blue-600 text-white' : 'bg-neutral-200 dark:bg-neutral-800'}`}>SYAI Ranking</button>
        <button onClick={() => setActiveTab("compare")} className={`px-4 py-2 rounded-xl ${activeTab==='compare' ? 'bg-blue-600 text-white' : 'bg-neutral-200 dark:bg-neutral-800'}`}>Comparison with Other Methods</button>
      </div>

      {activeTab === "rank" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column: inputs */}
          <div className="space-y-6 col-span-1">
            <div className={card}>
              <div className={sectionTitle}>Step 1: Upload Decision Matrix</div>
              <div className="flex items-center gap-3">
                <label className="inline-flex items-center px-3 py-2 rounded-lg bg-neutral-200 dark:bg-neutral-800 cursor-pointer">
                  <Upload size={18} className="mr-2"/> Choose CSV
                  <input type="file" accept=".csv" className="hidden" onChange={(e)=>{
                    const f = e.target.files?.[0];
                    if (f) parseCSV(f, onCSVLoaded);
                  }}/>
                </label>
              </div>
              <p className="text-sm opacity-70 mt-2">First column must be <b>Alternative</b>.</p>
            </div>

            {!!data.columns.length && (
              <div className={card}>
                <div className={sectionTitle}>Step 2: Define Criteria Types</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {data.columns.filter((c)=>c!=="Alternative").map((c)=> (
                    <div key={c} className="border rounded-xl p-3">
                      <div className="font-medium mb-2">{c}</div>
                      <select
                        className="w-full rounded-lg bg-neutral-100 dark:bg-neutral-800 p-2"
                        value={types[c]||"Benefit"}
                        onChange={(e)=> setTypes({...types, [c]: e.target.value})}
                      >
                        <option>Benefit</option>
                        <option>Cost</option>
                        <option>Ideal (Goal)</option>
                      </select>
                      {types[c]==="Ideal (Goal)" && (
                        <input
                          type="number"
                          step="any"
                          className="mt-2 w-full rounded-lg bg-neutral-100 dark:bg-neutral-800 p-2"
                          placeholder="Goal value"
                          value={ideals[c] ?? ""}
                          onChange={(e)=> setIdeals({...ideals, [c]: e.target.value})}
                        />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!!data.columns.length && (
              <div className={card}>
                <div className={sectionTitle}>Step 3: Set Weights (raw; auto‑normalized on run)</div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {data.columns.filter((c)=>c!=="Alternative").map((c, idx)=> (
                    <div key={c} className="flex flex-col">
                      <label className="text-sm mb-1">w({c})</label>
                      <input
                        type="number"
                        step="0.001"
                        min="0"
                        className="rounded-lg bg-neutral-100 dark:bg-neutral-800 p-2"
                        value={weights[c] ?? 0}
                        onChange={(e)=> setWeights({...weights, [c]: e.target.value})}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!!data.columns.length && (
              <div className={card}>
                <div className={sectionTitle}>Step 4: β (blend of D⁺ and D⁻)</div>
                <input type="range" min={0} max={1} step={0.01} value={beta} onChange={(e)=> setBeta(parseFloat(e.target.value))} className="w-full"/>
                <div className="mt-2 text-sm">β = <b>{beta.toFixed(2)}</b></div>
              </div>
            )}
          </div>

          {/* Right column: data + results */}
          <div className="space-y-6 col-span-2">
            {!!data.columns.length && (
              <div className={card}>
                <div className="flex items-center justify-between">
                  <div className={sectionTitle}>Decision Matrix (first 10 rows)</div>
                </div>
                <div className="overflow-auto max-h-[360px]">
                  <table className="min-w-full text-sm">
                    <thead className="sticky top-0 bg-white dark:bg-neutral-900">
                      <tr>
                        {data.columns.map((c)=> <th key={c} className="text-left p-2 border-b">{c}</th>)}
                      </tr>
                    </thead>
                    <tbody>
                      {data.rows.slice(0,10).map((r, idx)=> (
                        <tr key={idx} className="border-b hover:bg-neutral-50/50 dark:hover:bg-neutral-800/50">
                          {data.columns.map((c)=> <td key={c} className="p-2">{String(r[c] ?? "")}</td>)}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {result && (
              <div className={card}>
                <div className="flex items-center gap-2 mb-2"><BarChart3 size={18}/><div className={sectionTitle}>Final Ranking (SYAI)</div></div>
                <div className="overflow-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr>
                        {Object.keys(resultTable[0]||{Alternative:1}).map((c)=> <th key={c} className="text-left p-2 border-b">{c}</th>)}
                      </tr>
                    </thead>
                    <tbody>
                      {resultTable.map((r)=> (
                        <tr key={r.Alternative} className="border-b">
                          <td className="p-2 font-medium">{r.Alternative}</td>
                          <td className="p-2">{r["D+"]?.toFixed(6)}</td>
                          <td className="p-2">{r["D-"]?.toFixed(6)}</td>
                          <td className="p-2">{r["Closeness"]?.toFixed(6)}</td>
                          <td className="p-2">{r["Rank"]}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Bar Chart */}
                <div className="mt-6">
                  <div className="flex items-center gap-2 mb-1 text-sm opacity-80"><BarChart3 size={16}/> Ranking — Bar</div>
                  <div style={{ width: "100%", height: 340 }}>
                    <ResponsiveContainer>
                      <BarChart data={result.resRows.map(r=>({ name: r.Alternative, value: r.Closeness }))} margin={{ top: 10, right: 20, left: 0, bottom: 30 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" angle={-25} textAnchor="end" interval={0} height={50} />
                        <YAxis />
                        <Tooltip formatter={(v)=> Number(v).toFixed(6)} />
                        <Bar dataKey="value">
                          {result.resRows.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={colorPalette[index % colorPalette.length]} />
                          ))}
                          <LabelList dataKey="value" position="top" formatter={(v)=>Number(v).toFixed(3)} />
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Line Chart */}
                <div className="mt-6">
                  <div className="flex items-center gap-2 mb-1 text-sm opacity-80"><LineChartIcon size={16}/> Ranking — Line</div>
                  <div style={{ width: "100%", height: 300 }}>
                    <ResponsiveContainer>
                      <LineChart data={result.resRows.map(r=>({ rank: r.Rank, value: r.Closeness, name: r.Alternative }))} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="rank" label={{ value: "Rank (1 = best)", position: "insideBottom", offset: -5 }} />
                        <YAxis />
                        <Tooltip formatter={(v)=> Number(v).toFixed(6)} labelFormatter={(l)=>`Rank ${l}`} />
                        <Line type="monotone" dataKey="value" stroke="#4C78A8" dot />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "compare" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className={card}>
            <div className={sectionTitle}>Load Images (URLs or Upload)</div>
            <div className="space-y-3">
              <input className="w-full rounded-lg bg-neutral-100 dark:bg-neutral-800 p-2" placeholder="Scatter matrix image URL (raw GitHub)" value={urlScatter} onChange={(e)=> setUrlScatter(e.target.value)} />
              {urlScatter && (
                <img src={urlScatter} alt="scatter" className="w-full rounded-xl border" />
              )}
              <input className="w-full rounded-lg bg-neutral-100 dark:bg-neutral-800 p-2" placeholder="Correlation heatmap image URL (raw GitHub)" value={urlCorr} onChange={(e)=> setUrlCorr(e.target.value)} />
              {urlCorr && (
                <img src={urlCorr} alt="corr" className="w-full rounded-xl border" />
              )}
              <p className="text-sm opacity-70 flex items-center gap-2"><ImageIcon size={16}/> Use raw GitHub links ending with .png/.jpg. Or serve from public hosting.</p>
            </div>
          </div>

          <div className={card}>
            <div className={sectionTitle}>How to read the figures</div>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              <li><b>Scatter matrix</b> shows pairwise score relationships (each dot = one alternative).</li>
              <li><b>Correlation heatmap</b> highlights similarity of scores/rankings across methods (darker = stronger agreement).</li>
              <li>Use these to validate whether SYAI trends align with or diverge from other methods.</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

