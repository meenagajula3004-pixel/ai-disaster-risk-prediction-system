import React, { useState, useEffect } from 'react';
import { X, History, MapPin, AlertTriangle, Calendar, ShieldCheck, Loader2 } from 'lucide-react';
import { fetchUserHistoryAPI } from '../services/api';

export const UserHistoryModal = ({ isOpen, onClose }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadUserHistory();
    }
  }, [isOpen]);

  const loadUserHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchUserHistoryAPI();
      setHistory(data);
    } catch (err) {
      console.error('Failed to load user prediction history:', err);
      setError('Failed to retrieve your prediction history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const getRiskBadgeColor = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-950/60 border-rose-500/50 text-rose-300';
      case 'HIGH':
        return 'bg-orange-950/60 border-orange-500/50 text-orange-300';
      case 'MODERATE':
        return 'bg-amber-950/60 border-amber-500/50 text-amber-300';
      default:
        return 'bg-emerald-950/60 border-emerald-500/50 text-emerald-300';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden p-6 sm:p-8 flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <History className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-100">My Prediction History</h2>
              <p className="text-xs text-slate-400">Personal AI Multi-Hazard Risk Forecast Audit Log</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto pr-1">
          {loading ? (
            <div className="py-16 text-center text-slate-400 flex flex-col items-center justify-center space-y-3">
              <Loader2 className="w-8 h-8 animate-spin text-sky-400" />
              <p className="text-sm">Fetching secure prediction records...</p>
            </div>
          ) : error ? (
            <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/30 text-rose-300 text-sm text-center">
              {error}
            </div>
          ) : history.length === 0 ? (
            <div className="py-16 text-center text-slate-400 space-y-2">
              <History className="w-12 h-12 text-slate-600 mx-auto" />
              <p className="text-base font-semibold text-slate-300">No Prediction Records Found</p>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Select a location on the interactive map and generate a risk forecast to log your predictions.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                    <th className="pb-3 px-3">Date & Time</th>
                    <th className="pb-3 px-3">Location</th>
                    <th className="pb-3 px-3">Primary Hazard</th>
                    <th className="pb-3 px-3">Risk Level</th>
                    <th className="pb-3 px-3 text-right">Probability</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {history.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-850/50 transition-colors">
                      <td className="py-3 px-3 text-slate-300 font-mono text-[11px] whitespace-nowrap">
                        <div className="flex items-center space-x-1.5">
                          <Calendar className="w-3.5 h-3.5 text-slate-500" />
                          <span>{item.timestamp ? new Date(item.timestamp).toLocaleString() : 'N/A'}</span>
                        </div>
                      </td>
                      <td className="py-3 px-3 text-slate-100 font-medium whitespace-nowrap">
                        <div className="flex items-center space-x-1.5">
                          <MapPin className="w-3.5 h-3.5 text-sky-400" />
                          <span>{item.location_name}</span>
                        </div>
                      </td>
                      <td className="py-3 px-3 text-slate-200 font-semibold whitespace-nowrap">
                        {item.primary_risk}
                      </td>
                      <td className="py-3 px-3 whitespace-nowrap">
                        <span className={`px-2.5 py-1 rounded-full border text-[10px] font-bold ${getRiskBadgeColor(item.primary_level)}`}>
                          {item.primary_level}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-right font-mono font-bold text-slate-100 text-sm whitespace-nowrap">
                        {item.primary_probability ? item.primary_probability.toFixed(1) : 0.0}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-800 mt-4 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center space-x-2 text-slate-500">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>End-to-End User Data Isolation Enforced</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded-xl transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserHistoryModal;
