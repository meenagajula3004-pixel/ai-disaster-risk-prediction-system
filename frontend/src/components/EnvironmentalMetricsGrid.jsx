import React from 'react';
import { Thermometer, Droplets, Gauge, Wind, CloudRain, Mountain, Info } from 'lucide-react';

export default function EnvironmentalMetricsGrid({ envData }) {
  if (!envData) return null;

  const metrics = [
    {
      label: 'Air Temperature',
      value: envData.temperature !== null ? `${envData.temperature}°C` : 'Data unavailable',
      sub: '2m Surface Level',
      icon: Thermometer,
      color: 'text-amber-400',
      bg: 'from-amber-500/10 to-amber-950/20'
    },
    {
      label: 'Relative Humidity',
      value: envData.humidity !== null ? `${envData.humidity}%` : 'Data unavailable',
      sub: 'Atmospheric Saturation',
      icon: Droplets,
      color: 'text-blue-400',
      bg: 'from-blue-500/10 to-blue-950/20'
    },
    {
      label: 'Surface Pressure',
      value: envData.surface_pressure !== null ? `${envData.surface_pressure} hPa` : 'Data unavailable',
      sub: 'Barometric Level',
      icon: Gauge,
      color: 'text-purple-400',
      bg: 'from-purple-500/10 to-purple-950/20'
    },
    {
      label: 'Wind Speed',
      value: envData.wind_speed !== null ? `${envData.wind_speed} km/h` : 'Data unavailable',
      sub: '10m Velocity',
      icon: Wind,
      color: 'text-cyan-400',
      bg: 'from-cyan-500/10 to-cyan-950/20'
    },
    {
      label: '24h Cumulative Rain',
      value: envData.rainfall_24h !== null ? `${envData.rainfall_24h} mm` : 'Data unavailable',
      sub: 'Past 24 Hours Accumulation',
      icon: CloudRain,
      color: 'text-emerald-400',
      bg: 'from-emerald-500/10 to-emerald-950/20'
    },
    {
      label: '7-Day Cumulative Rain',
      value: envData.rainfall_7d !== null ? `${envData.rainfall_7d} mm` : 'Data unavailable',
      sub: 'Past 7 Days Accumulation',
      icon: CloudRain,
      color: 'text-indigo-400',
      bg: 'from-indigo-500/10 to-indigo-950/20'
    },
    {
      label: 'Terrain Elevation',
      value: envData.elevation !== null ? `${envData.elevation} m` : 'Data unavailable',
      sub: 'Height Above Sea Level',
      icon: Mountain,
      color: 'text-rose-400',
      bg: 'from-rose-500/10 to-rose-950/20'
    }
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
          <Info className="h-4 w-4 text-cyan-400" />
          <span>Retrieved Environmental Measurements</span>
        </h3>
        <span className="text-[11px] font-mono text-cyan-400/90 bg-cyan-950/60 px-2.5 py-1 rounded-md border border-cyan-800/50">
          {envData.status || 'Live Open-Meteo Feed'}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div
              key={idx}
              className={`glass-panel p-3.5 rounded-xl border border-slate-800 bg-gradient-to-b ${m.bg} flex flex-col justify-between space-y-2 hover:border-slate-700 transition-all`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-slate-400 truncate">{m.label}</span>
                <Icon className={`h-4 w-4 ${m.color} flex-shrink-0`} />
              </div>

              <div>
                <div className="text-lg font-bold font-mono text-slate-100 tracking-tight">
                  {m.value}
                </div>
                <div className="text-[10px] text-slate-500 truncate mt-0.5">{m.sub}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
