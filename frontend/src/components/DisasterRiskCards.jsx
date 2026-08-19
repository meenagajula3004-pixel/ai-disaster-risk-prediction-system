import React from 'react';
import { Waves, Mountain, Wind, Sun, AlertOctagon, ChevronRight, CheckCircle2, AlertCircle } from 'lucide-react';

const HAZARD_ICONS = {
  'Flood Risk': Waves,
  'Landslide Risk': Mountain,
  'Cyclone / Severe Storm': Wind,
  'Heatwave Risk': Sun,
  'Drought Risk': AlertOctagon
};

const HAZARD_EMOJIS = {
  'Flood Risk': '🌊',
  'Landslide Risk': '⛰️',
  'Cyclone / Severe Storm': '🌀',
  'Heatwave Risk': '☀️',
  'Drought Risk': '🏜️'
};

export default function DisasterRiskCards({ disasterRisks, selectedHazardKey, onSelectHazard }) {
  if (!disasterRisks) return null;

  const levelStyles = {
    LOW: { border: 'border-emerald-500/40', badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30', bar: 'bg-emerald-500' },
    MODERATE: { border: 'border-amber-500/40', badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30', bar: 'bg-amber-500' },
    HIGH: { border: 'border-red-500/50', badge: 'bg-red-500/20 text-red-300 border-red-500/30', bar: 'bg-red-500' },
    CRITICAL: { border: 'border-purple-500/60', badge: 'bg-purple-500/30 text-purple-300 border-purple-500/40', bar: 'bg-purple-500' }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          5-Hazard Risk Predictions
        </h3>
        <span className="text-xs text-slate-400">Click card to inspect SHAP explanation</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {Object.entries(disasterRisks).map(([key, item]) => {
          const isSelected = selectedHazardKey === key;
          const style = levelStyles[item.risk_level] || levelStyles.LOW;
          const Icon = HAZARD_ICONS[item.disaster_type] || Waves;
          const emoji = HAZARD_EMOJIS[item.disaster_type] || '⚠️';

          return (
            <div
              key={key}
              onClick={() => onSelectHazard(key)}
              className={`glass-panel p-4 rounded-2xl border cursor-pointer transition-all duration-300 relative overflow-hidden flex flex-col justify-between space-y-4 ${
                isSelected
                  ? `${style.border} bg-slate-800/90 ring-2 ring-cyan-500/50 shadow-xl scale-[1.02]`
                  : 'border-slate-800 hover:border-slate-700 hover:bg-slate-800/50'
              }`}
            >
              {/* Header: Hazard Title & Emoji */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-2xl">{emoji}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${style.badge}`}>
                    {item.risk_level}
                  </span>
                </div>

                <div className="font-bold text-slate-200 text-sm leading-snug">
                  {item.disaster_type}
                </div>

                {/* Experimental / Limited Validation Badge */}
                {item.validation_status.includes('Experimental') ? (
                  <div className="flex items-center space-x-1 text-[10px] text-amber-400/90 font-medium">
                    <AlertCircle className="h-3 w-3 flex-shrink-0" />
                    <span>Experimental / Limited validation</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-1 text-[10px] text-emerald-400/80 font-medium">
                    <CheckCircle2 className="h-3 w-3 flex-shrink-0" />
                    <span>Model Validated</span>
                  </div>
                )}
              </div>

              {/* Middle: Probability Score & Progress Bar */}
              <div className="space-y-2">
                <div className="flex items-baseline justify-between">
                  <span className="text-xs text-slate-400">Risk Probability</span>
                  <span className="text-2xl font-black font-mono text-white">
                    {item.risk_percentage.toFixed(1)}%
                  </span>
                </div>

                <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-800">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${style.bar}`}
                    style={{ width: `${Math.min(100, Math.max(5, item.risk_percentage))}%` }}
                  ></div>
                </div>
              </div>

              {/* Footer: Selection Indicator */}
              <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
                <span className="text-[11px] font-medium text-cyan-400">
                  {isSelected ? 'Selected' : 'View Factors'}
                </span>
                <ChevronRight className={`h-4 w-4 transition-transform ${isSelected ? 'rotate-90 text-cyan-400' : 'text-slate-500'}`} />
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
}
