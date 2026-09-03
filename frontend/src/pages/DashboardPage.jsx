import React, { useState, useEffect } from 'react';
import LocationSearch from '../components/LocationSearch';
import PrimaryRiskBanner from '../components/PrimaryRiskBanner';
import EnvironmentalMetricsGrid from '../components/EnvironmentalMetricsGrid';
import DisasterRiskCards from '../components/DisasterRiskCards';
import RiskMap from '../components/RiskMap';
import SHAPExplainerWidget from '../components/SHAPExplainerWidget';
import { predictDisasterRiskAPI } from '../services/api';
import { Activity, ShieldAlert, AlertCircle, RefreshCw } from 'lucide-react';

export default function DashboardPage({ selectedLocation, setSelectedLocation }) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedHazardKey, setSelectedHazardKey] = useState('flood');

  useEffect(() => {
    if (selectedLocation) {
      loadPrediction(selectedLocation.latitude, selectedLocation.longitude, selectedLocation.name);
    }
  }, [selectedLocation]);

  const loadPrediction = async (lat, lon, name) => {
    setLoading(true);
    setError(null);
    try {
      const res = await predictDisasterRiskAPI(lat, lon, name);
      setPrediction(res);
      
      // Default selected hazard key to primary hazard if available
      if (res && res.primary_risk) {
        const pName = res.primary_risk.primary_hazard.toLowerCase();
        if (pName.includes('flood')) setSelectedHazardKey('flood');
        else if (pName.includes('landslide')) setSelectedHazardKey('landslide');
        else if (pName.includes('cyclone')) setSelectedHazardKey('cyclone');
        else if (pName.includes('heatwave')) setSelectedHazardKey('heatwave');
        else if (pName.includes('drought')) setSelectedHazardKey('drought');
      }
    } catch (err) {
      setError('Unable to process prediction request. Verify connection or coordinates.');
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    if (selectedLocation) {
      loadPrediction(selectedLocation.latitude, selectedLocation.longitude, selectedLocation.name);
    }
  };

  return (
    <div className="space-y-8">
      
      {/* Hero Location Search Header */}
      <div className="text-center space-y-4 max-w-3xl mx-auto pt-4">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/80 text-cyan-400 text-xs font-semibold">
          <Activity className="h-3.5 w-3.5" />
          <span>Real-Time Environmental Risk Intelligence Engine</span>
        </div>

        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          AI Multi-Disaster Risk Prediction & Early Warning System
        </h1>

        <p className="text-sm text-slate-400">
          Select a location to automatically fetch live environmental measurements and evaluate risk across 5 natural hazards.
        </p>

        <LocationSearch
          onSelectLocation={(loc) => setSelectedLocation(loc)}
          selectedLocation={selectedLocation}
        />
      </div>

      {/* Loading Indicator */}
      {loading && (
        <div className="glass-panel p-12 rounded-2xl text-center space-y-4">
          <Activity className="h-8 w-8 text-cyan-400 animate-spin mx-auto" />
          <p className="text-sm font-semibold text-slate-300">
            Fetching Open-Meteo Environmental Data & Running ML Models...
          </p>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            (Note: On initial load, cloud backend spin-up may take up to 20 seconds. Please hold on...)
          </p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="glass-panel p-6 rounded-2xl border border-red-500/50 bg-red-950/30 text-center space-y-4">
          <AlertCircle className="h-8 w-8 text-red-400 mx-auto" />
          <div className="text-sm font-bold text-red-200">{error}</div>
          <p className="text-xs text-slate-400">
            The server may be starting up or environmental APIs experienced a brief delay. Click below to retry.
          </p>
          <button
            onClick={handleRetry}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-red-600/80 hover:bg-red-500 text-white rounded-lg text-xs font-semibold transition-colors"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Retry Prediction</span>
          </button>
        </div>
      )}

      {/* Prediction Output Results */}
      {!loading && prediction && (
        <div className="space-y-8">
          
          {/* Primary Risk Alert Banner */}
          <PrimaryRiskBanner
            primaryRisk={prediction.primary_risk}
            locationName={prediction.location_name}
          />

          {/* Retrieved Environmental Data Grid */}
          <EnvironmentalMetricsGrid
            envData={prediction.environmental_data}
          />

          {/* 5 Disaster Risk Cards */}
          <DisasterRiskCards
            disasterRisks={prediction.disaster_risks}
            selectedHazardKey={selectedHazardKey}
            onSelectHazard={(key) => setSelectedHazardKey(key)}
          />

          {/* Map + SHAP Visualizer Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            <RiskMap
              latitude={prediction.latitude}
              longitude={prediction.longitude}
              locationName={prediction.location_name}
              primaryRisk={prediction.primary_risk}
              disasterRisks={prediction.disaster_risks}
            />

            <SHAPExplainerWidget
              selectedHazardData={prediction.disaster_risks[selectedHazardKey]}
              hazardName={prediction.disaster_risks[selectedHazardKey]?.disaster_type}
            />

          </div>

        </div>
      )}

    </div>
  );
}
