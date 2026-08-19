import React from 'react';
import { ShieldAlert, ExternalLink, Database } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="mt-20 border-t border-slate-800 bg-[#060911] py-12 text-slate-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          
          {/* Column 1: System Disclaimer */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-slate-200 font-semibold">
              <ShieldAlert className="h-5 w-5 text-amber-500" />
              <span>Official Safety Disclaimer</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              This application provides AI-based multi-disaster risk estimation for educational, portfolio, and decision-support purposes. It does not replace official government weather, disaster management, or emergency warnings.
            </p>
          </div>

          {/* Column 2: Data Sources & Provenance */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-slate-200 font-semibold">
              <Database className="h-5 w-5 text-cyan-400" />
              <span>Data Sourcing & Provenance</span>
            </div>
            <ul className="text-xs space-y-1.5 text-slate-400">
              <li className="flex items-center space-x-1">
                <span>• Live Weather & Elevation:</span>
                <span className="text-cyan-400 font-medium">Open-Meteo API</span>
              </li>
              <li className="flex items-center space-x-1">
                <span>• Flood Benchmark:</span>
                <span className="text-slate-300">NOAA NCEI & ERA5 Reanalysis</span>
              </li>
              <li className="flex items-center space-x-1">
                <span>• Landslide Benchmark:</span>
                <span className="text-slate-300">NASA Global Landslide Catalog</span>
              </li>
              <li className="flex items-center space-x-1">
                <span>• Cyclone & Storm Benchmark:</span>
                <span className="text-slate-300">NOAA IBTrACS Archives</span>
              </li>
            </ul>
          </div>

          {/* Column 3: Tech Stack & Architecture */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-slate-200 font-semibold">
              <ExternalLink className="h-5 w-5 text-indigo-400" />
              <span>Technology Architecture</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Built with React 18, Vite, Tailwind CSS, Recharts, Leaflet, Python FastAPI, Scikit-learn, XGBoost, SHAP Explainable AI, PostgreSQL, and Docker containerization.
            </p>
          </div>

        </div>

        <div className="border-t border-slate-800/80 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
          <p>© 2026 AI Multi-Disaster Risk Prediction System. All rights reserved.</p>
          <div className="flex items-center space-x-4 mt-3 sm:mt-0">
            <span className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-400 font-mono">
              v1.0.0 Production Release
            </span>
          </div>
        </div>

      </div>
    </footer>
  );
}
