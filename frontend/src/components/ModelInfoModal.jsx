import React from 'react';
import { Database, ShieldCheck, Cpu, Clock, CheckCircle2, AlertTriangle, FileText } from 'lucide-react';

export default function ModelInfoModal() {
  return (
    <div className="space-y-8 glass-panel p-8 rounded-2xl border border-slate-800 shadow-2xl">
      
      {/* Header */}
      <div className="border-b border-slate-800 pb-4 space-y-1">
        <div className="flex items-center space-x-2 text-cyan-400 font-bold uppercase tracking-wider text-xs">
          <Cpu className="h-4 w-4" />
          <span>Scientific & Model Provenance Documentation</span>
        </div>
        <h2 className="text-2xl font-bold text-white">5-Hazard ML Architecture & Dataset Provenance</h2>
        <p className="text-xs text-slate-400">Documentation of public datasets, time-aware cross-validation, and explainable AI metrics.</p>
      </div>

      {/* Grid of 5 Disaster Dataset Profiles */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Flood */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-bold text-slate-100 flex items-center space-x-2">
              <span>🌊 Flood Risk Module</span>
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Validated Model
            </span>
          </div>
          <div className="text-xs space-y-1 text-slate-300">
            <div><span className="text-slate-400">Selected Model:</span> <span className="font-mono text-cyan-400">GradientBoosting Classifier</span></div>
            <div><span className="text-slate-400">Dataset Source:</span> NOAA NCEI & ERA5 Reanalysis</div>
            <div><span className="text-slate-400">License:</span> CC BY 4.0 (Open Data)</div>
            <div><span className="text-slate-400">Key Features:</span> 1h-7d Rainfall Windows, Elevation, Soil Moisture, Humidity</div>
            <div><span className="text-slate-400">Validation Split:</span> Time-Aware Split (2000-2018 Train, 2019-2021 Val, 2022-2024 Test)</div>
          </div>
        </div>

        {/* Landslide */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-bold text-slate-100 flex items-center space-x-2">
              <span>⛰️ Landslide Risk Module</span>
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Validated Model
            </span>
          </div>
          <div className="text-xs space-y-1 text-slate-300">
            <div><span className="text-slate-400">Selected Model:</span> <span className="font-mono text-cyan-400">Logistic Regression</span></div>
            <div><span className="text-slate-400">Dataset Source:</span> NASA Global Landslide Catalog & USGS Topography</div>
            <div><span className="text-slate-400">License:</span> NASA Open Data Policy</div>
            <div><span className="text-slate-400">Key Features:</span> 3d/7d Antecedent Rain, Slope Degree, Soil Saturation</div>
            <div><span className="text-slate-400">Validation Split:</span> Chronological Time-Aware Validation</div>
          </div>
        </div>

        {/* Cyclone */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-bold text-slate-100 flex items-center space-x-2">
              <span>🌀 Cyclone / Severe Storm Module</span>
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/30">
              Experimental / Limited validation
            </span>
          </div>
          <div className="text-xs space-y-1 text-slate-300">
            <div><span className="text-slate-400">Selected Model:</span> <span className="font-mono text-cyan-400">Logistic Regression</span></div>
            <div><span className="text-slate-400">Dataset Source:</span> NOAA IBTrACS Archives</div>
            <div><span className="text-slate-400">License:</span> Public Domain</div>
            <div><span className="text-slate-400">Key Features:</span> Wind Speed 10m, Surface Pressure Drop, 6h Rain</div>
            <div><span className="text-slate-400">Validation Status:</span> Tagged as Experimental in inland non-coastal locations</div>
          </div>
        </div>

        {/* Heatwave & Drought */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-bold text-slate-100 flex items-center space-x-2">
              <span>☀️ Heatwave & 🏜️ Drought Modules</span>
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Validated Models
            </span>
          </div>
          <div className="text-xs space-y-1 text-slate-300">
            <div><span className="text-slate-400">Selected Models:</span> <span className="font-mono text-cyan-400">LogisticRegression & GradientBoosting</span></div>
            <div><span className="text-slate-400">Dataset Source:</span> NOAA GHCN-D & US Drought Monitor</div>
            <div><span className="text-slate-400">License:</span> Public Domain / CC BY 4.0</div>
            <div><span className="text-slate-400">Key Features:</span> Max Temp, Humidity, Hot Streak Days, Rain Deficit</div>
            <div><span className="text-slate-400">Validation Split:</span> Chronological Time-Aware Split</div>
          </div>
        </div>

      </div>

      {/* Safety & Ethics Guidelines Box */}
      <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-xs space-y-2">
        <div className="font-bold text-slate-200 flex items-center space-x-2">
          <ShieldCheck className="h-4 w-4 text-cyan-400" />
          <span>Scientific Integrity & Data Ethics Policy</span>
        </div>
        <p className="text-slate-400 leading-relaxed">
          The system strictly enforces no-fabrication guidelines: live API failures return explicit <span className="text-cyan-300">"Data unavailable"</span> statuses rather than dummy values. Models are evaluated using High-Risk Recall and ROC-AUC rather than raw accuracy alone.
        </p>
      </div>

    </div>
  );
}
