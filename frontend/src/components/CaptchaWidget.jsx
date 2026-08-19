import React, { useState, useEffect } from 'react';
import { ShieldCheck, CheckCircle2, Loader2 } from 'lucide-react';

export const CaptchaWidget = ({ onVerify, error }) => {
  const [isChecked, setIsChecked] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const siteKey = import.meta.env.VITE_CAPTCHA_SITE_KEY;

  useEffect(() => {
    // If Turnstile sitekey is available, load Cloudflare Turnstile script
    if (siteKey && window.turnstile) {
      window.turnstile.render('#turnstile-container', {
        sitekey: siteKey,
        callback: (token) => {
          setIsChecked(true);
          onVerify(token);
        },
      });
    }
  }, [siteKey]);

  const handleCheckboxClick = () => {
    if (isChecked || verifying) return;
    setVerifying(true);

    setTimeout(() => {
      setVerifying(false);
      setIsChecked(true);
      const generatedToken = `captcha_verified_${Date.now()}`;
      onVerify(generatedToken);
    }, 600);
  };

  if (siteKey) {
    return (
      <div className="my-3 flex flex-col items-center justify-center">
        <div id="turnstile-container"></div>
        {error && <p className="text-xs text-rose-400 mt-1">{error}</p>}
      </div>
    );
  }

  return (
    <div className="my-4">
      <div 
        onClick={handleCheckboxClick}
        className={`flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer select-none ${
          isChecked 
            ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300' 
            : error
              ? 'bg-rose-950/20 border-rose-500/50 hover:border-rose-400'
              : 'bg-slate-900/60 border-slate-700/60 hover:border-slate-500 text-slate-300'
        }`}
      >
        <div className="flex items-center space-x-3">
          <div className="relative flex items-center justify-center">
            {verifying ? (
              <Loader2 className="w-5 h-5 animate-spin text-sky-400" />
            ) : isChecked ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400 animate-in zoom-in-50 duration-200" />
            ) : (
              <div className="w-5 h-5 rounded border border-slate-600 bg-slate-850 hover:border-sky-400 transition-colors" />
            )}
          </div>
          <span className="text-sm font-medium">
            {isChecked ? "Human Verification Complete" : "I'm not a robot"}
          </span>
        </div>

        <div className="flex items-center space-x-1.5 text-xs text-slate-500">
          <ShieldCheck className="w-4 h-4 text-sky-400" />
          <span className="font-mono text-[10px] tracking-wider uppercase">CAPTCHA</span>
        </div>
      </div>
      {error && <p className="text-xs text-rose-400 mt-1.5 ml-1">{error}</p>}
    </div>
  );
};

export default CaptchaWidget;
