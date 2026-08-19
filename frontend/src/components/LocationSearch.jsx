import React, { useState, useEffect, useRef } from 'react';
import { Search, MapPin, Loader2, Navigation } from 'lucide-react';
import { searchLocationsAPI } from '../services/api';

const QUICK_LOCATIONS = [
  { name: 'Bhimavaram', lat: 16.5449, lon: 81.5212, country: 'India' },
  { name: 'Mumbai', lat: 19.0760, lon: 72.8777, country: 'India' },
  { name: 'Shimla', lat: 31.1048, lon: 77.1734, country: 'India' },
  { name: 'Tokyo', lat: 35.6762, lon: 139.6503, country: 'Japan' },
  { name: 'Miami', lat: 25.7617, lon: -80.1918, country: 'USA' },
];

export default function LocationSearch({ onSelectLocation, selectedLocation }) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handler = setTimeout(async () => {
      if (query.trim().length >= 2) {
        setLoading(true);
        const results = await searchLocationsAPI(query);
        setSuggestions(results);
        setLoading(false);
        setIsOpen(true);
      } else {
        setSuggestions([]);
        setIsOpen(false);
      }
    }, 350);

    return () => clearTimeout(handler);
  }, [query]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (item) => {
    setQuery(item.name);
    setIsOpen(false);
    onSelectLocation({
      name: item.admin1 ? `${item.name}, ${item.admin1}, ${item.country}` : `${item.name}, ${item.country}`,
      latitude: item.latitude,
      longitude: item.longitude,
    });
  };

  return (
    <div className="relative w-full max-w-3xl mx-auto" ref={dropdownRef}>
      
      {/* Search Input Field */}
      <div className="relative glass-panel rounded-2xl p-2 flex items-center shadow-xl border border-slate-700/60 bg-slate-900/90 focus-within:border-cyan-500/80 focus-within:ring-2 focus-within:ring-cyan-500/20 transition-all duration-300">
        <div className="pl-4 pr-2 text-cyan-400">
          {loading ? <Loader2 className="h-6 w-6 animate-spin text-cyan-400" /> : <Search className="h-6 w-6" />}
        </div>
        
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search location (e.g. Bhimavaram, Mumbai, Tokyo, Miami)..."
          className="w-full bg-transparent text-slate-100 placeholder-slate-400 text-sm font-medium focus:outline-none py-3 px-2"
        />

        {query && (
          <button
            onClick={() => { setQuery(''); setSuggestions([]); }}
            className="px-3 py-1 text-xs text-slate-400 hover:text-white bg-slate-800 rounded-lg mr-2 font-mono"
          >
            Clear
          </button>
        )}
      </div>

      {/* Autocomplete Dropdown List */}
      {isOpen && suggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 glass-panel rounded-xl border border-slate-700/80 bg-slate-900/95 shadow-2xl z-50 overflow-hidden divide-y divide-slate-800">
          {suggestions.map((item, idx) => (
            <div
              key={idx}
              onClick={() => handleSelect(item)}
              className="p-3.5 hover:bg-slate-800/80 cursor-pointer flex items-center justify-between transition-colors text-sm"
            >
              <div className="flex items-center space-x-3">
                <MapPin className="h-4 w-4 text-cyan-400 flex-shrink-0" />
                <div>
                  <div className="font-semibold text-slate-200">{item.name}</div>
                  <div className="text-xs text-slate-400">{item.admin1 ? `${item.admin1}, ` : ''}{item.country}</div>
                </div>
              </div>
              <div className="text-[11px] font-mono text-slate-500">
                {item.latitude.toFixed(2)}°, {item.longitude.toFixed(2)}°
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Quick Location Chips */}
      <div className="flex items-center space-x-2 mt-3 overflow-x-auto pb-1 text-xs">
        <span className="text-slate-400 font-medium flex items-center space-x-1 flex-shrink-0">
          <Navigation className="h-3.5 w-3.5 text-cyan-400" />
          <span>Quick Select:</span>
        </span>
        {QUICK_LOCATIONS.map((loc) => (
          <button
            key={loc.name}
            onClick={() => {
              setQuery(loc.name);
              onSelectLocation({ name: `${loc.name}, ${loc.country}`, latitude: loc.lat, longitude: loc.lon });
            }}
            className="px-3 py-1.5 rounded-lg bg-slate-800/60 hover:bg-cyan-950/60 text-slate-300 hover:text-cyan-300 border border-slate-700/50 hover:border-cyan-700/50 font-medium transition-all flex-shrink-0"
          >
            {loc.name}
          </button>
        ))}
      </div>

    </div>
  );
}
