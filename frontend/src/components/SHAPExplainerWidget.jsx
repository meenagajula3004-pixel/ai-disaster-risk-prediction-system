import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Cpu, ArrowUpRight, ArrowDownRight, Info } from 'lucide-react';

export default function SHAPExplainerWidget({ selectedHazardData, hazardName }) {
  if (!selectedHazardData || !selectedHazardData.top_factors) {
    return null;
  }

  const factors = selectedHazardData.top_factors;

  const chartData = factors.map((f) => ({
    name: f.feature.replace('_', ' ').toUpperCase(),
    value: f.shap_value,
    absImportance: f.importance_score,
    direction: f.direction,
    input_value: f.input_value
  }));

  return (
    <div className="glass-panel rounded-2xl border border-slate-800 p-6 space-y-4 shadow-xl">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-4 gap-2">
        <div>
          <div className="flex items-center space-x-2">
            <Cpu className="h-5 w-5 text-cyan-400" />
            <h3 className="text-base font-bold text-slate-100">
              Explainable AI (SHAP) Feature Attribution
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Analyzing why model predicted <span className="text-cyan-300 font-semibold">{selectedHazardData.risk_percentage}% {selectedHazardData.risk_level}</span> risk for <span className="text-slate-200 font-semibold">{hazardName}</span>.
          </p>
        </div>

        <div className="text-[11px] font-mono bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 text-slate-400 self-start sm:self-auto">
          SHAP TreeExplainer v0.43
        </div>
      </div>

      {/* Recharts Horizontal Bar Chart */}
      <div className="h-[220px] w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
            <XAxis type="number" tick={{ fill: '#94A3B8', fontSize: 11 }} domain={['auto', 'auto']} />
            <YAxis dataKey="name" type="category" tick={{ fill: '#E2E8F0', fontSize: 11 }} width={120} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="glass-panel p-3 rounded-xl border border-slate-700 bg-slate-900 text-xs space-y-1 shadow-2xl">
                      <div className="font-bold text-slate-100">{data.name}</div>
                      <div className="text-slate-400">SHAP Impact Value: <span className="font-mono text-cyan-400">{data.value}</span></div>
                      <div className="text-slate-400">Measured Input Value: <span className="font-mono text-amber-400">{data.input_value}</span></div>
                      <div className="text-slate-400">Effect: <span className={data.value > 0 ? 'text-red-400 font-semibold' : 'text-emerald-400 font-semibold'}>{data.direction}</span></div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="value" radius={[0, 6, 6, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.value > 0 ? '#EF4444' : '#10B981'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Factor Breakdown Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
        {factors.map((f, idx) => {
          const isRiskIncr = f.direction === 'increases_risk' || f.shap_value > 0;
          return (
            <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 flex items-center justify-between text-xs">
              <div className="space-y-0.5">
                <div className="font-semibold text-slate-200 capitalize">
                  {f.feature.replace('_', ' ')}
                </div>
                <div className="text-[10px] text-slate-500">
                  Input Value: <span className="font-mono text-slate-300">{f.input_value}</span>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <span className={`text-[11px] font-mono font-bold ${isRiskIncr ? 'text-red-400' : 'text-emerald-400'}`}>
                  {f.shap_value > 0 ? `+${f.shap_value.toFixed(3)}` : f.shap_value.toFixed(3)}
                </span>
                {isRiskIncr ? (
                  <ArrowUpRight className="h-4 w-4 text-red-400" />
                ) : (
                  <ArrowDownRight className="h-4 w-4 text-emerald-400" />
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex items-center space-x-1.5 text-[11px] text-slate-400 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/60">
        <Info className="h-3.5 w-3.5 text-cyan-400 flex-shrink-0" />
        <span>SHAP values indicate local feature importance contribution towards the prediction, not direct causality.</span>
      </div>

    </div>
  );
}
