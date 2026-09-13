import React, { useState } from 'react';
import { ChakraLogo } from './ChakraLogo';
import { ShieldCheck, ArrowRight, UserPlus, LogIn, Phone, Lock, ChevronRight } from 'lucide-react';

interface LoginSignupProps {
  onLoginSuccess: (customerId: number) => void;
  lang: 'en' | 'hi';
  theme: 'light' | 'dark';
}

export const LoginSignup: React.FC<LoginSignupProps> = ({ onLoginSuccess, lang, theme }) => {
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [phone, setPhone] = useState('');
  const [pin, setPin] = useState('');
  
  const [confirmPin, setConfirmPin] = useState('');
  
  // Signup fields
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [income, setIncome] = useState('');
  const [dpdpConsent, setDpdpConsent] = useState(false);
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const isDark = theme === 'dark';

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!phone || !pin) {
      setError(lang === 'en' ? 'Phone and PIN are required' : 'फोन और पिन आवश्यक हैं');
      return;
    }
    
    if (pin.length !== 6 || !/^\d+$/.test(pin)) {
      setError(lang === 'en' ? 'PIN must be 6 digits' : 'पिन 6 अंकों का होना चाहिए');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, pin })
      });
      
      const text = await res.text();
      let data: any = {};
      try {
        data = text ? JSON.parse(text) : {};
      } catch {
        data = { error: text || `Server error (${res.status})` };
      }
      if (!res.ok) throw new Error(data.error || data.message || 'Login failed');
      
      if (!data.customer || !data.customer.id) {
        throw new Error('Invalid response from server');
      }

      onLoginSuccess(data.customer.id);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!phone || !pin || !name || !age || !income) {
      setError('All fields are required');
      return;
    }
    
    if (pin.length !== 6 || !/^\d+$/.test(pin)) {
      setError('PIN must be exactly 6 digits');
      return;
    }
    
    if (pin !== confirmPin) {
      setError('PIN confirmation does not match');
      return;
    }

    if (!dpdpConsent) {
      setError('You must accept the DPDP consent to continue');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch('/api/customers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          name, 
          age: parseInt(age), 
          phone, 
          pin, 
          monthly_income: parseFloat(income),
          monthly_emi: 0,
          language: lang,
          consent: dpdpConsent
        })
      });
      
      const text = await res.text();
      let data: any = {};
      try {
        data = text ? JSON.parse(text) : {};
      } catch {
        data = { error: text || `Server error (${res.status})` };
      }
      if (!res.ok) throw new Error(data.error || data.message || 'Signup failed');
      
      // Auto-login after signup by calling the login endpoint
      const loginRes = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, pin })
      });
      
      const loginText = await loginRes.text();
      let loginData: any = {};
      try {
        loginData = loginText ? JSON.parse(loginText) : {};
      } catch {
        loginData = { error: loginText || `Server error (${loginRes.status})` };
      }
      if (!loginRes.ok) throw new Error(loginData.error || loginData.message || 'Auto-login failed');
      
      onLoginSuccess(loginData.customer.id);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`flex-1 flex flex-col items-center p-6 py-12 overflow-y-auto ${isDark ? 'bg-[#070A10]' : 'bg-[#FAF8F5]'}`}>
      <div className="w-full max-w-sm flex flex-col items-center mb-8 animate-fade-in">
        <ChakraLogo className="w-16 h-16 text-[#FF671F] mb-4" />
        <h1 className={`text-2xl font-black tracking-tight ${isDark ? 'text-white' : 'text-slate-900'}`}>
          NEOBHARAT
        </h1>
        <p className={`text-sm mt-1 font-medium ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
          {lang === 'en' ? 'Empowering Your Financial Journey' : 'आपकी वित्तीय यात्रा को सशक्त बनाना'}
        </p>
      </div>

      <div className={`w-full max-w-sm p-6 rounded-3xl shadow-xl border ${
        isDark ? 'bg-[#131A26] border-slate-800' : 'bg-white border-slate-100'
      }`}>
        <h2 className={`text-lg font-bold mb-6 flex items-center gap-2 ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>
          {mode === 'login' ? <LogIn className="w-5 h-5 text-[#FF671F]" /> : <UserPlus className="w-5 h-5 text-[#FF671F]" />}
          {mode === 'login' 
            ? (lang === 'en' ? 'Welcome Back' : 'वापसी पर स्वागत है')
            : (lang === 'en' ? 'Create Account' : 'खाता बनाएं')
          }
        </h2>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-xs font-semibold flex items-center gap-2 border border-red-100 dark:border-red-900/30">
            <ShieldCheck className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        <form onSubmit={mode === 'login' ? handleLogin : handleSignup} className="space-y-4">
          {mode === 'signup' && (
            <>
              <div className="space-y-1">
                <label className={`text-xs font-bold ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Legal Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  className={`w-full p-3 rounded-xl border font-medium text-sm transition-colors ${
                    isDark ? 'bg-slate-900 border-slate-700 text-white focus:border-[#FF671F]' : 'bg-slate-50 border-slate-200 text-slate-900 focus:border-[#FF671F]'
                  } outline-none focus:ring-1 focus:ring-[#FF671F]`}
                  placeholder="Rahul Kumar"
                />
              </div>
              <div className="flex gap-3">
                <div className="space-y-1 flex-1">
                  <label className={`text-xs font-bold ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Age</label>
                  <input
                    type="number"
                    value={age}
                    onChange={e => setAge(e.target.value)}
                    className={`w-full p-3 rounded-xl border font-medium text-sm transition-colors ${
                      isDark ? 'bg-slate-900 border-slate-700 text-white' : 'bg-slate-50 border-slate-200 text-slate-900'
                    } outline-none focus:border-[#FF671F]`}
                    placeholder="28"
                  />
                </div>
                <div className="space-y-1 flex-1">
                  <label className={`text-xs font-bold ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Monthly Income</label>
                  <input
                    type="number"
                    value={income}
                    onChange={e => setIncome(e.target.value)}
                    className={`w-full p-3 rounded-xl border font-medium text-sm transition-colors ${
                      isDark ? 'bg-slate-900 border-slate-700 text-white' : 'bg-slate-50 border-slate-200 text-slate-900'
                    } outline-none focus:border-[#FF671F]`}
                    placeholder="45000"
                  />
                </div>
              </div>
            </>
          )}

          <div className="space-y-1">
            <label className={`text-xs font-bold ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              {lang === 'en' ? 'Mobile Number' : 'मोबाइल नंबर'}
            </label>
            <div className="relative">
              <Phone className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${isDark ? 'text-slate-500' : 'text-slate-400'}`} />
              <input
                type="tel"
                value={phone}
                onChange={e => setPhone(e.target.value)}
                className={`w-full pl-10 p-3 rounded-xl border font-medium text-sm transition-colors ${
                  isDark ? 'bg-slate-900 border-slate-700 text-white focus:border-[#FF671F]' : 'bg-slate-50 border-slate-200 text-slate-900 focus:border-[#FF671F]'
                } outline-none focus:ring-1 focus:ring-[#FF671F]`}
                placeholder="98765 43210"
                maxLength={10}
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className={`text-xs font-bold ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              {lang === 'en' ? '6-Digit PIN' : '6-अंकीय पिन'}
            </label>
            <div className="relative">
              <Lock className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${isDark ? 'text-slate-500' : 'text-slate-400'}`} />
              <input
                type="password"
                inputMode="numeric"
                value={pin}
                onChange={e => setPin(e.target.value.replace(/\D/g, ''))}
                className={`w-full pl-10 p-3 rounded-xl border font-black text-lg tracking-[0.2em] transition-colors ${
                  isDark ? 'bg-slate-900 border-slate-700 text-white focus:border-[#FF671F]' : 'bg-slate-50 border-slate-200 text-slate-900 focus:border-[#FF671F]'
                } outline-none focus:ring-1 focus:ring-[#FF671F]`}
                placeholder="••••••"
                maxLength={6}
              />
            </div>
          </div>

          {mode === 'signup' && (
            <div className="space-y-1">
              <label className={`text-xs font-bold ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                {lang === 'en' ? 'Confirm 6-Digit PIN' : '6-अंकीय पिन की पुष्टि करें'}
              </label>
              <div className="relative">
                <Lock className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${isDark ? 'text-slate-500' : 'text-slate-400'}`} />
                <input
                  type="password"
                  inputMode="numeric"
                  value={confirmPin}
                  onChange={e => setConfirmPin(e.target.value.replace(/\D/g, ''))}
                  className={`w-full pl-10 p-3 rounded-xl border font-black text-lg tracking-[0.2em] transition-colors ${
                    isDark ? 'bg-slate-900 border-slate-700 text-white focus:border-[#FF671F]' : 'bg-slate-50 border-slate-200 text-slate-900 focus:border-[#FF671F]'
                  } outline-none focus:ring-1 focus:ring-[#FF671F]`}
                  placeholder="••••••"
                  maxLength={6}
                />
              </div>
            </div>
          )}

          {mode === 'signup' && (
            <label className="flex items-start gap-3 p-3 rounded-xl bg-orange-50/50 dark:bg-orange-950/20 border border-orange-100 dark:border-orange-900/30 cursor-pointer mt-2">
              <input 
                type="checkbox" 
                checked={dpdpConsent}
                onChange={(e) => setDpdpConsent(e.target.checked)}
                className="mt-0.5 w-4 h-4 text-[#FF671F] rounded focus:ring-[#FF671F]"
              />
              <span className={`text-[10px] leading-snug font-medium ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                I consent to the collection and processing of my personal and financial data under the Digital Personal Data Protection Act (DPDP), 2023 for credit and banking services.
              </span>
            </label>
          )}

          <div className="pt-2 flex flex-col gap-3">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-[#FF671F] via-[#FF8040] to-[#FF671F] hover:opacity-90 shadow-lg shadow-orange-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading 
                ? (lang === 'en' ? 'Processing...' : 'प्रसंस्करण...') 
                : (mode === 'login' 
                    ? (lang === 'en' ? 'SECURE LOGIN' : 'सुरक्षित लॉगिन')
                    : (lang === 'en' ? 'CREATE ACCOUNT' : 'खाता बनाएं')
                  )
              }
              {!loading && <ArrowRight className="w-4 h-4" />}
            </button>

            <button
              type="button"
              onClick={() => {
                setMode(mode === 'login' ? 'signup' : 'login');
                setError('');
                setPin('');
                setConfirmPin('');
              }}
              className={`w-full py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-1 transition-colors border ${
                isDark 
                  ? 'bg-slate-800/50 border-slate-700 text-slate-300 hover:bg-slate-800' 
                  : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
              }`}
            >
              {mode === 'login' 
                ? (lang === 'en' ? 'New to NeoBharat? Create Account' : 'नवभारत में नए हैं? खाता बनाएं')
                : (lang === 'en' ? 'Already have an account? Login' : 'पहले से खाता है? लॉगिन करें')
              }
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
