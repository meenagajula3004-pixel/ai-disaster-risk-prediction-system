import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import DashboardPage from './pages/DashboardPage';
import WhatIfSimulator from './components/WhatIfSimulator';
import AdminDashboard from './components/AdminDashboard';
import ModelInfoModal from './components/ModelInfoModal';
import AuthModal from './components/AuthModal';
import UserHistoryModal from './components/UserHistoryModal';
import { AuthProvider } from './context/AuthContext';

function MainApp() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedLocation, setSelectedLocation] = useState({
    name: 'Bhimavaram, Andhra Pradesh, India',
    latitude: 16.5449,
    longitude: 81.5212,
  });
  const [isLocating, setIsLocating] = useState(false);

  // Modal States
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authInitialView, setAuthInitialView] = useState('login');
  const [historyModalOpen, setHistoryModalOpen] = useState(false);

  const handleDetectLocation = () => {
    if (navigator.geolocation) {
      setIsLocating(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setSelectedLocation({
            name: `Detected Location (${position.coords.latitude.toFixed(2)}°, ${position.coords.longitude.toFixed(2)}°)`,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
          setIsLocating(false);
        },
        (error) => {
          console.error('Geolocation error:', error);
          setIsLocating(false);
          alert('Unable to retrieve current browser location. Using default location.');
        }
      );
    } else {
      alert('Geolocation is not supported by your browser.');
    }
  };

  const handleOpenAuth = (view = 'login') => {
    setAuthInitialView(view);
    setAuthModalOpen(true);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#090D16] text-slate-100 font-['Plus_Jakarta_Sans',sans-serif]">
      
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onDetectLocation={handleDetectLocation}
        isLocating={isLocating}
        onOpenAuth={handleOpenAuth}
        onOpenHistory={() => setHistoryModalOpen(true)}
      />

      {/* Main Content Body */}
      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {activeTab === 'dashboard' && (
          <DashboardPage
            selectedLocation={selectedLocation}
            setSelectedLocation={setSelectedLocation}
          />
        )}

        {activeTab === 'whatif' && (
          <div className="space-y-6 pt-4">
            <WhatIfSimulator
              latitude={selectedLocation.latitude}
              longitude={selectedLocation.longitude}
              locationName={selectedLocation.name}
            />
          </div>
        )}

        {activeTab === 'admin' && (
          <div className="space-y-6 pt-4">
            <AdminDashboard />
          </div>
        )}

        {activeTab === 'modelinfo' && (
          <div className="space-y-6 pt-4">
            <ModelInfoModal />
          </div>
        )}

      </main>

      {/* Auth Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        initialView={authInitialView}
      />

      {/* Prediction History Modal */}
      <UserHistoryModal
        isOpen={historyModalOpen}
        onClose={() => setHistoryModalOpen(false)}
      />

      {/* Footer */}
      <Footer />

    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
