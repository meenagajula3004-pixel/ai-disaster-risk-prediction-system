import React from 'react';
import { AlertTriangle, ShieldCheck, Zap, Activity } from 'lucide-react';

export default function PrimaryRiskBanner({ primaryRisk, locationName }) {
  if (!primaryRisk) return null;

  const levelColors = {
    LOW: { bg: 'from-emerald-950/80 to-slate-900', border: 'border-emerald-500/40', text: 'text-emerald-400', badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' },
    MODERATE: { bg: 'from-amber-950/80 to-slate-900', border: 'border-amber-500/40', text: 'text-amber-400', badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40' },
    HIGH: { bg: 'from-red-950/90 to-slate-900', border: 'border-red-500/50', text: 'text-red-400', badge: 'bg-red-500/20 text-red-300 border-red-500/40' },
    CRITICAL: { bg: 'from-purple-950/90 to-slate-900', border: 'border-purple-500/60', text: 'text-purple-400', badge: 'bg-purple-500/30 text-purple-300 border-purple-500/50' }
  };

  const style = levelColors[primaryRisk.risk_level] || levelColors.LOW;

  return (
    <div className={`w-full glass-panel rounded-2xl border ${style.border} bg-gradient-to-r ${style.bg} p-6 shadow-2xl relative overflow-hidden`}>
      
      {/* Background Subtle Pulse Glow for High/Critical Risk */}
      {(primaryRisk.risk_level === 'HIGH' || primaryRisk.risk_level === 'CRITICAL') && (
        <div className="absolute -right-10 -top-10 w-40 h-40 rounded-full bg-red-500/10 blur-3xl pointer-events-none animate-pulse-slow"></div>
      )}

      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
        
        {/* Left Side: Hazard Details */}
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-bold flex items-center space-x-1">
              <Activity className="h-4 w-4 text-cyan-400" />
              <span>Primary Risk Highlight</span>
            </span>
            <span className="text-slate-500">•</span>
            <span className="text-xs font-semibold text-slate-300">{locationName}</span>
          </div>

          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-700">
              <AlertTriangle className={`h-7 w-7 ${style.text}`} />
            </div>
            <div>
              <h2 className="text-2xl font-extrabold text-white tracking-tight">
                {primaryRisk.primary_hazard}
              </h2>
              <p className="text-xs text-slate-400 font-medium mt-0.5">{primaryRisk.warning_advice}</p>
            </div>
          </div>
        </div>

        {/* Right Side: Risk Metric Badge & Percentage */}
        <div className="flex items-center space-x-4 bg-slate-900/80 p-4 rounded-xl border border-slate-800 self-stretch md:self-auto justify-between md:justify-end">
          <div className="text-right">
            <div className="text-xs font-medium text-slate-400">Estimated Probability</div>
            <div className={`text-3xl font-black ${style.text} font-mono tracking-tight`}>
              {primaryRisk.risk_percentage.toFixed(1)}%
            </div>
          </div>

          <div className={`px-4 py-2.5 rounded-xl border font-black tracking-wider text-sm ${style.badge} shadow-lg`}>
            {primaryRisk.risk_level}
          </div>
        </div>

      </div>
    </div>
  );
}
