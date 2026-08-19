import React, { useState, useEffect } from 'react';
import { X, Mail, Lock, User, Eye, EyeOff, ShieldCheck, ArrowRight, RefreshCw, AlertCircle, CheckCircle2, KeyRound } from 'lucide-react';
import { registerUserAPI, verifyOtpAPI, resendOtpAPI, loginUserAPI, forgotPasswordAPI, resetPasswordAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import CaptchaWidget from './CaptchaWidget';

export const AuthModal = ({ isOpen, onClose, initialView = 'login' }) => {
  const { loginSuccess } = useAuth();
  const [view, setView] = useState(initialView); // 'login', 'register', 'otp', 'forgot', 'reset'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Form Fields
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [captchaToken, setCaptchaToken] = useState('');
  const [captchaError, setCaptchaError] = useState('');
  const [otpPurpose, setOtpPurpose] = useState('registration');

  // Timers
  const [resendCooldown, setResendCooldown] = useState(0);
  const [otpExpiryTimer, setOtpExpiryTimer] = useState(600); // 10 minutes

  // Reset form state function (declared before useEffect usage to prevent TDZ ReferenceError)
  const resetForm = () => {
    setError('');
    setSuccessMsg('');
    setName('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setOtp(['', '', '', '', '', '']);
    setCaptchaToken('');
    setCaptchaError('');
    setShowPassword(false);
    setShowConfirmPassword(false);
  };

  useEffect(() => {
    setView(initialView);
    resetForm();
  }, [initialView, isOpen]);

  // Resend Cooldown Countdown
  useEffect(() => {
    let timer;
    if (resendCooldown > 0) {
      timer = setInterval(() => setResendCooldown(prev => prev - 1), 1000);
    }
    return () => clearInterval(timer);
  }, [resendCooldown]);

  // OTP Expiry Countdown
  useEffect(() => {
    let timer;
    if (view === 'otp' && otpExpiryTimer > 0) {
      timer = setInterval(() => setOtpExpiryTimer(prev => prev - 1), 1000);
    }
    return () => clearInterval(timer);
  }, [view, otpExpiryTimer]);

  // Password Requirement Checklist Evaluation
  const pwdCriteria = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[!@#$%^&*()_+\-=\[\]{};:'",.<>?/\\]/.test(password),
  };

  const isPasswordValid = Object.values(pwdCriteria).every(Boolean);

  const handleOtpChange = (element, index) => {
    if (isNaN(element.value)) return false;
    const newOtp = [...otp];
    newOtp[index] = element.value;
    setOtp(newOtp);
    setError('');

    // Focus next input box automatically
    if (element.value !== '' && element.nextSibling) {
      element.nextSibling.focus();
    }
  };

  // 1. Submit Registration Form
  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');

    if (!name.trim() || !email.trim()) {
      setError('Please fill in all required fields.');
      return;
    }

    if (!isPasswordValid) {
      setError('Password does not satisfy all security requirements.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Password and Confirm Password do not match.');
      return;
    }

    if (!captchaToken) {
      setCaptchaError('Please complete human verification (CAPTCHA).');
      return;
    }

    setLoading(true);
    try {
      const res = await registerUserAPI({
        full_name: name.trim(),
        email: email.trim(),
        password,
        confirm_password: confirmPassword,
        captcha_token: captchaToken
      });

      const registeredEmail = email.trim();
      setPassword('');
      setConfirmPassword('');
      setCaptchaToken('');
      setCaptchaError('');
      setSuccessMsg(res.message || 'Registration Successful! Please login to continue.');
      setEmail(registeredEmail);
      setView('login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // 2. Submit OTP Verification
  const handleVerifyOtpSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const fullOtp = otp.join('');
    if (fullOtp.length !== 6) {
      setError('Please enter the complete 6-digit verification code.');
      return;
    }

    setLoading(true);
    try {
      const res = await verifyOtpAPI({
        email: email.trim(),
        otp: fullOtp,
        purpose: otpPurpose
      });

      if (otpPurpose === 'registration') {
        loginSuccess(res.access_token, res.user);
        onClose();
      } else if (otpPurpose === 'password_reset') {
        setSuccessMsg('OTP verified successfully. Please enter your new password.');
        setView('reset');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'OTP verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // 3. Resend OTP
  const handleResendOtp = async () => {
    if (resendCooldown > 0) return;
    setError('');
    setSuccessMsg('');
    setLoading(true);

    try {
      const res = await resendOtpAPI({
        email: email.trim(),
        purpose: otpPurpose,
        captcha_token: captchaToken || 'verified'
      });
      setSuccessMsg(res.message || 'A new verification code has been sent.');
      setResendCooldown(60);
      setOtpExpiryTimer(600);
      setOtp(['', '', '', '', '', '']);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to resend OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // 4. Submit Login
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');

    if (!email.trim() || !password) {
      setError('Please enter your email and password.');
      return;
    }

    setLoading(true);
    try {
      const res = await loginUserAPI({
        email: email.trim(),
        password,
        captcha_token: captchaToken
      });

      loginSuccess(res.access_token, res.user);
      onClose();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Login failed. Please verify credentials.';
      setError(detail);

      // If user email is unverified
      if (detail.includes('not verified')) {
        setOtpPurpose('registration');
        setView('otp');
      }
    } finally {
      setLoading(false);
    }
  };

  // 5. Forgot Password Request
  const handleForgotPasswordSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!email.trim()) {
      setError('Please enter your email address.');
      return;
    }

    if (!captchaToken) {
      setCaptchaError('Please complete human verification (CAPTCHA).');
      return;
    }

    setLoading(true);
    try {
      const res = await forgotPasswordAPI({
        email: email.trim(),
        captcha_token: captchaToken
      });

      setSuccessMsg(res.message || 'If an account exists, a reset code was sent.');
      setOtpPurpose('password_reset');
      setResendCooldown(60);
      setOtpExpiryTimer(600);
      setView('otp');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process request.');
    } finally {
      setLoading(false);
    }
  };

  // 6. Reset Password Submission
  const handleResetPasswordSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const fullOtp = otp.join('');

    if (!isPasswordValid) {
      setError('New password does not satisfy all security requirements.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const res = await resetPasswordAPI({
        email: email.trim(),
        otp: fullOtp,
        new_password: password,
        confirm_password: confirmPassword
      });

      setSuccessMsg(res.message || 'Password reset successfully. Please log in.');
      setView('login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to reset password.');
    } finally {
      setLoading(false);
    }
  };

  const formatTimer = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden p-6 sm:p-8">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="mb-6 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-sky-500/10 text-sky-400 mb-3 border border-sky-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold text-slate-100">
            {view === 'login' && 'Welcome Back'}
            {view === 'register' && 'Create Account'}
            {view === 'otp' && 'Verify Your Email'}
            {view === 'forgot' && 'Reset Password'}
            {view === 'reset' && 'Set New Password'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {view === 'login' && 'Log in to access your personal risk forecasts and prediction history'}
            {view === 'register' && 'Register for secure multi-hazard early warning monitoring'}
            {view === 'otp' && `We sent a 6-digit OTP code to: ${email}`}
            {view === 'forgot' && 'Enter your email to receive a password reset verification code'}
            {view === 'reset' && 'Create a strong new password for your account'}
          </p>
        </div>

        {/* Alert Error Message */}
        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Alert Success Message */}
        {successMsg && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs flex items-start space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* VIEW 1: LOGIN */}
        {view === 'login' && (
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="user@example.com"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:border-sky-500 focus:outline-none"
                  required
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-medium text-slate-300">Password</label>
                <button
                  type="button"
                  onClick={() => setView('forgot')}
                  className="text-xs text-sky-400 hover:underline"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password"
                  className="w-full pl-10 pr-10 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:border-sky-500 focus:outline-none"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-slate-500 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <CaptchaWidget onVerify={(token) => { setCaptchaToken(token); setCaptchaError(''); }} error={captchaError} />

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-semibold rounded-xl text-sm transition-all shadow-lg shadow-sky-500/20 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {loading ? <span>Authenticating...</span> : <><span>Login to Account</span><ArrowRight className="w-4 h-4" /></>}
            </button>

            <div className="text-center pt-2 text-xs text-slate-400">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={() => setView('register')}
                className="text-sky-400 font-semibold hover:underline"
              >
                Create Account
              </button>
            </div>
          </form>
        )}

        {/* VIEW 2: REGISTER */}
        {view === 'register' && (
          <form onSubmit={handleRegisterSubmit} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
              <div className="relative">
                <User className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:border-sky-500 focus:outline-none"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="user@gmail.com"
                  className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:border-sky-500 focus:outline-none"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Meena@2026"
                  className="w-full pl-10 pr-10 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:border-sky-500 focus:outline-none"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Confirm Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm password"
                  className="w-full pl-10 pr-10 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:border-sky-500 focus:outline-none"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300"
                >
                  {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Live Password Requirement Checklist */}
            <div className="p-2.5 bg-slate-950/60 rounded-xl border border-slate-800 text-[11px] space-y-1">
              <span className="font-semibold text-slate-400 block mb-1">Password requirements:</span>
              <div className="grid grid-cols-2 gap-x-2 gap-y-1">
                <div className={`flex items-center space-x-1.5 ${pwdCriteria.length ? 'text-emerald-400' : 'text-slate-500'}`}>
                  <span>{pwdCriteria.length ? '✓' : '✗'}</span>
                  <span>Minimum 8 characters</span>
                </div>
                <div className={`flex items-center space-x-1.5 ${pwdCriteria.uppercase ? 'text-emerald-400' : 'text-slate-500'}`}>
                  <span>{pwdCriteria.uppercase ? '✓' : '✗'}</span>
                  <span>One uppercase (A-Z)</span>
                </div>
                <div className={`flex items-center space-x-1.5 ${pwdCriteria.lowercase ? 'text-emerald-400' : 'text-slate-500'}`}>
                  <span>{pwdCriteria.lowercase ? '✓' : '✗'}</span>
                  <span>One lowercase (a-z)</span>
                </div>
                <div className={`flex items-center space-x-1.5 ${pwdCriteria.number ? 'text-emerald-400' : 'text-slate-500'}`}>
                  <span>{pwdCriteria.number ? '✓' : '✗'}</span>
                  <span>One number (0-9)</span>
                </div>
                <div className={`flex items-center space-x-1.5 ${pwdCriteria.special ? 'text-emerald-400' : 'text-slate-500'}`}>
                  <span>{pwdCriteria.special ? '✓' : '✗'}</span>
                  <span>One special character</span>
                </div>
              </div>
            </div>

            <CaptchaWidget onVerify={(token) => { setCaptchaToken(token); setCaptchaError(''); }} error={captchaError} />

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-semibold rounded-xl text-sm transition-all shadow-lg shadow-sky-500/20 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {loading ? <span>Sending Verification OTP...</span> : <><span>Create Account</span><ArrowRight className="w-4 h-4" /></>}
            </button>

            <div className="text-center pt-1 text-xs text-slate-400">
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => setView('login')}
                className="text-sky-400 font-semibold hover:underline"
              >
                Login
              </button>
            </div>
          </form>
        )}

        {/* VIEW 3: OTP VERIFICATION */}
        {view === 'otp' && (
          <form onSubmit={handleVerifyOtpSubmit} className="space-y-5">
            <div className="flex justify-center space-x-2 my-4">
              {otp.map((data, index) => (
                <input
                  key={index}
                  type="text"
                  maxLength="1"
                  value={data}
                  onChange={(e) => handleOtpChange(e.target, index)}
                  onFocus={(e) => e.target.select()}
                  className="w-11 h-12 text-center text-xl font-bold bg-slate-950 border border-slate-800 rounded-xl text-sky-400 focus:border-sky-500 focus:outline-none shadow-inner"
                />
              ))}
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400 px-1">
              <span>OTP expires in: <strong className="text-amber-400">{formatTimer(otpExpiryTimer)}</strong></span>
              <button
                type="button"
                onClick={handleResendOtp}
                disabled={resendCooldown > 0 || loading}
                className="text-sky-400 hover:underline disabled:text-slate-600 flex items-center space-x-1"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                <span>{resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend OTP'}</span>
              </button>
            </div>

            <button
              type="submit"
              disabled={loading || otp.join('').length !== 6}
              className="w-full py-3 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-semibold rounded-xl text-sm transition-all shadow-lg shadow-sky-500/20 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {loading ? <span>Verifying OTP...</span> : <><span>Verify OTP & Complete</span><CheckCircle2 className="w-4 h-4" /></>}
            </button>
          </form>
        )}

        {/* VIEW 4: FORGOT PASSWORD */}
        {view === 'forgot' && (
          <form onSubmit={handleForgotPasswordSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Account Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="user@example.com"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:border-sky-500 focus:outline-none"
                  required
                />
              </div>
            </div>

            <CaptchaWidget onVerify={(token) => { setCaptchaToken(token); setCaptchaError(''); }} error={captchaError} />

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-semibold rounded-xl text-sm transition-all shadow-lg shadow-sky-500/20 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {loading ? <span>Processing...</span> : <><span>Send Reset Verification OTP</span><ArrowRight className="w-4 h-4" /></>}
            </button>

            <div className="text-center pt-2 text-xs text-slate-400">
              Remember your password?{' '}
              <button
                type="button"
                onClick={() => setView('login')}
                className="text-sky-400 font-semibold hover:underline"
              >
                Back to Login
              </button>
            </div>
          </form>
        )}

        {/* VIEW 5: RESET PASSWORD */}
        {view === 'reset' && (
          <form onSubmit={handleResetPasswordSubmit} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">New Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Meena@2026"
                  className="w-full pl-10 pr-10 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:border-sky-500 focus:outline-none"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Confirm New Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm new password"
                  className="w-full pl-10 pr-10 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:border-sky-500 focus:outline-none"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300"
                >
                  {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-semibold rounded-xl text-sm transition-all shadow-lg shadow-sky-500/20 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {loading ? <span>Updating Password...</span> : <><span>Update Password</span><KeyRound className="w-4 h-4" /></>}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default AuthModal;
