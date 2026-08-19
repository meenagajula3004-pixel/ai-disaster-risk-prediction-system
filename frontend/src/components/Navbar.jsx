import React from 'react';
import { ShieldAlert, MapPin, Compass, BarChart3, Sliders, Info, ShieldCheck } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, onDetectLocation, isLocating }) {
  const tabs = [
    { id: 'dashboard', label: 'Multi-Hazard Risk', icon: ShieldAlert },
    { id: 'whatif', label: 'What-If Simulator', icon: Sliders },
    { id: 'admin', label: 'Admin Analytics', icon: BarChart3 },
    { id: 'modelinfo', label: 'Model Provenance', icon: Info },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800 bg-[#090D16]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* Brand Logo & Title */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="h-11 w-11 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <ShieldCheck className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                AegisAI
              </h1>
              <span className="text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                Multi-Hazard Early Warning
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">AI Environmental Risk Decision-Support System</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Quick Detect Location Button */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onDetectLocation}
            disabled={isLocating}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all duration-200 hover:border-cyan-500/50"
          >
            <Compass className={`h-4 w-4 text-cyan-400 ${isLocating ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">{isLocating ? 'Locating...' : 'Detect My Location'}</span>
          </button>
        </div>

      </div>
    </header>
  );
}
