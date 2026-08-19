import React, { useState } from 'react';
import { Sliders, RefreshCw, AlertCircle, Waves, Mountain, Wind, Sun, AlertOctagon, Sparkles } from 'lucide-react';
import { simulateWhatIfAPI } from '../services/api';

export default function WhatIfSimulator({ latitude, longitude, locationName, initialDisasterRisks }) {
  const [rainModifier, setRainModifier] = useState(0); // -50% to +100%
  const [tempModifier, setTempModifier] = useState(0); // -5°C to +10°C
  const [humModifier, setHumModifier] = useState(0);  // -30% to +50%
  const [windModifier, setWindModifier] = useState(0); // -20% to +100%

  const [simulationResult, setSimulationResult] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);

  const handleSimulate = async () => {
    setIsSimulating(true);
    try {
      const res = await simulateWhatIfAPI({
        latitude: latitude || 16.5449,
        longitude: longitude || 81.5212,
        location_name: locationName || 'Selected Location',
        simulated_rainfall_change_pct: rainModifier,
        simulated_temp_change_celsius: tempModifier,
        simulated_humidity_change_pct: humModifier,
        simulated_wind_change_pct: windModifier
      });
      setSimulationResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleReset = () => {
    setRainModifier(0);
    setTempModifier(0);
    setHumModifier(0);
    setWindModifier(0);
    setSimulationResult(null);
  };

  const displayRisks = simulationResult ? simulationResult.disaster_risks : initialDisasterRisks;

  return (
    <div className="glass-panel rounded-2xl border border-slate-800 p-6 space-y-6 shadow-2xl">
      
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-4 gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-cyan-950/80 border border-cyan-800 text-cyan-400">
            <Sliders className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
              <span>What-If Environmental Risk Simulator</span>
              <Sparkles className="h-4 w-4 text-cyan-400" />
            </h2>
            <p className="text-xs text-slate-400">Simulate hypothetical climate variations and observe real-time risk shifts.</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 bg-amber-950/60 border border-amber-800/60 px-3 py-1.5 rounded-xl text-amber-300 text-xs font-bold self-start sm:self-auto">
          <AlertCircle className="h-4 w-4 text-amber-400 flex-shrink-0" />
          <span>SIMULATION ONLY — NOT A LIVE FORECAST</span>
        </div>
      </div>

      {/* Slider Controls */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Rainfall Slider */}
        <div className="space-y-2 glass-panel p-4 rounded-xl border border-slate-800">
          <div className="flex justify-between text-xs font-semibold text-slate-300">
            <span>Precipitation Variation</span>
            <span className="font-mono text-cyan-400 font-bold">{rainModifier > 0 ? `+${rainModifier}%` : `${rainModifier}%`}</span>
          </div>
          <input
            type="range"
            min="-50"
            max="150"
            step="10"
            value={rainModifier}
            onChange={(e) => setRainModifier(Number(e.target.value))}
            className="w-full h-2 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-400"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>-50% Drought</span>
            <span>+150% Heavy Storm</span>
          </div>
        </div>

        {/* Temperature Slider */}
        <div className="space-y-2 glass-panel p-4 rounded-xl border border-slate-800">
          <div className="flex justify-between text-xs font-semibold text-slate-300">
            <span>Temperature Shift</span>
            <span className="font-mono text-amber-400 font-bold">{tempModifier > 0 ? `+${tempModifier}°C` : `${tempModifier}°C`}</span>
          </div>
          <input
            type="range"
            min="-5"
            max="12"
            step="1"
            value={tempModifier}
            onChange={(e) => setTempModifier(Number(e.target.value))}
            className="w-full h-2 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-amber-400"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>-5°C Cooler</span>
            <span>+12°C Extreme Heat</span>
          </div>
        </div>

        {/* Humidity Slider */}
        <div className="space-y-2 glass-panel p-4 rounded-xl border border-slate-800">
          <div className="flex justify-between text-xs font-semibold text-slate-300">
            <span>Humidity Adjustment</span>
            <span className="font-mono text-blue-400 font-bold">{humModifier > 0 ? `+${humModifier}%` : `${humModifier}%`}</span>
          </div>
          <input
            type="range"
            min="-30"
            max="50"
            step="5"
            value={humModifier}
            onChange={(e) => setHumModifier(Number(e.target.value))}
            className="w-full h-2 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-blue-400"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>-30% Dry Air</span>
            <span>+50% Saturated</span>
          </div>
        </div>

        {/* Wind Speed Slider */}
        <div className="space-y-2 glass-panel p-4 rounded-xl border border-slate-800">
          <div className="flex justify-between text-xs font-semibold text-slate-300">
            <span>Wind Velocity Shift</span>
            <span className="font-mono text-purple-400 font-bold">{windModifier > 0 ? `+${windModifier}%` : `${windModifier}%`}</span>
          </div>
          <input
            type="range"
            min="-20"
            max="120"
            step="10"
            value={windModifier}
            onChange={(e) => setWindModifier(Number(e.target.value))}
            className="w-full h-2 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-purple-400"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>-20% Calm</span>
            <span>+120% Cyclone Wind</span>
          </div>
        </div>

      </div>

      {/* Action Buttons */}
      <div className="flex items-center space-x-3 justify-end">
        <button
          onClick={handleReset}
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center space-x-1.5 transition-all"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Reset Sliders</span>
        </button>

        <button
          onClick={handleSimulate}
          disabled={isSimulating}
          className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold shadow-lg shadow-cyan-500/25 flex items-center space-x-2 transition-all"
        >
          <Sparkles className={`h-4 w-4 ${isSimulating ? 'animate-spin' : ''}`} />
          <span>{isSimulating ? 'Recalculating Models...' : 'Run Simulation'}</span>
        </button>
      </div>

      {/* Simulated Multi-Hazard Output Cards */}
      {displayRisks && (
        <div className="space-y-3 pt-4 border-t border-slate-800">
          <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center justify-between">
            <span>Simulated Multi-Hazard Risk Matrix</span>
            {simulationResult && (
              <span className="text-cyan-400 font-mono text-[11px] font-semibold">
                Updated via ML Models
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
            {Object.entries(displayRisks).map(([k, item]) => (
              <div key={k} className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-slate-300 truncate">{item.disaster_type}</div>
                <div className="text-xl font-black font-mono text-cyan-400">{item.risk_percentage}%</div>
                <div className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 inline-block">
                  {item.risk_level}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
