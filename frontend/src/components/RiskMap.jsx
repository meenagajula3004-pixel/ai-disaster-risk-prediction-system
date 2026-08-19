import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import { MapPin, Navigation } from 'lucide-react';

// Fix leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

function MapRecenter({ lat, lon }) {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lon], 10, { animate: true });
  }, [lat, lon, map]);
  return null;
}

export default function RiskMap({ latitude, longitude, locationName, primaryRisk, disasterRisks }) {
  const lat = latitude || 16.5449;
  const lon = longitude || 81.5212;

  const riskColors = {
    LOW: '#10B981',
    MODERATE: '#F59E0B',
    HIGH: '#EF4444',
    CRITICAL: '#8B5CF6'
  };

  const primaryLevel = primaryRisk?.risk_level || 'LOW';
  const circleColor = riskColors[primaryLevel] || '#10B981';

  return (
    <div className="glass-panel rounded-2xl border border-slate-800 p-4 space-y-3 shadow-xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Navigation className="h-4 w-4 text-cyan-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
            Geographical Risk Spatial View
          </h3>
        </div>
        <div className="text-xs font-mono text-slate-400">
          {lat.toFixed(4)}°N, {lon.toFixed(4)}°E
        </div>
      </div>

      <div className="h-[320px] w-full rounded-xl overflow-hidden border border-slate-800 relative z-0">
        <MapContainer center={[lat, lon]} zoom={10} scrollWheelZoom={false} style={{ width: '100%', height: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          <MapRecenter lat={lat} lon={lon} />

          {/* Spatial Risk Intensity Overlay Circle */}
          <Circle
            center={[lat, lon]}
            radius={15000}
            pathOptions={{
              color: circleColor,
              fillColor: circleColor,
              fillOpacity: 0.25,
              weight: 2
            }}
          />

          <Marker position={[lat, lon]}>
            <Popup className="dark-popup">
              <div className="p-1 space-y-2 text-xs">
                <div className="font-bold text-slate-100 border-b border-slate-700 pb-1">
                  📍 {locationName}
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Primary Risk:</span>
                    <span className="font-bold text-cyan-400">{primaryRisk?.primary_hazard}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Probability:</span>
                    <span className="font-bold text-amber-400">{primaryRisk?.risk_percentage}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Level:</span>
                    <span className="font-bold text-red-400">{primaryRisk?.risk_level}</span>
                  </div>
                </div>
              </div>
            </Popup>
          </Marker>
        </MapContainer>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800 pt-2">
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span><span>Low</span></span>
          <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block"></span><span>Moderate</span></span>
          <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block"></span><span>High</span></span>
          <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-purple-600 inline-block"></span><span>Critical</span></span>
        </div>
        <span>Leaflet + OpenStreetMap</span>
      </div>
    </div>
  );
}
