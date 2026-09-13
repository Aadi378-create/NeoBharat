import React, { useState } from 'react';
import { Language, ThemeMode, PersonaProfile } from '../types';
import { translations } from '../data/translations';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  HeartHandshake,
  Lock,
  Unlock,
  CheckCircle2,
  Activity,
  Zap,
  TrendingDown,
  RefreshCw,
  BellOff,
  KeyRound,
  Fingerprint
} from 'lucide-react';

interface EmpatheticStressRadarProps {
  activePersona: PersonaProfile;
  lang: Language;
  theme: ThemeMode;
  isStressActive: boolean;
  setIsStressActive: (active: boolean) => void;
}

export const EmpatheticStressRadar: React.FC<EmpatheticStressRadarProps> = ({
  activePersona,
  lang,
  theme,
  isStressActive,
  setIsStressActive,
}) => {
  const t = translations[lang];
  const isDark = theme === 'dark';
  const isTiranga = !isDark;

  const [stressType, setStressType] = useState<'medical' | 'income_dip'>('medical');
  const [reliefActivated, setReliefActivated] = useState(false);
  
  // Security Verification Modal State
  const [accountLocked, setAccountLocked] = useState(false);
  const [showVerifyModal, setShowVerifyModal] = useState(false);
  const [mpinInput, setMpinInput] = useState('');
  const [verificationError, setVerificationError] = useState('');
  const [lockReason, setLockReason] = useState('suspicious_activity');
  const [statusNotification, setStatusNotification] = useState<string | null>(null);

  const handleTriggerStress = (type: 'medical' | 'income_dip') => {
    setStressType(type);
    setIsStressActive(true);
    setReliefActivated(false);
  };

  const handleRestoreNormal = () => {
    setIsStressActive(false);
    setReliefActivated(false);
  };

  const handleOpenLockModal = () => {
    setMpinInput('');
    setVerificationError('');
    setShowVerifyModal(true);
  };

  const handleConfirmVerification = (e: React.FormEvent) => {
    e.preventDefault();
    if (mpinInput.length !== 4) {
      setVerificationError(lang === 'en' ? 'Please enter a valid 4-digit MPIN' : 'कृपया 4 अंकों का मान्य MPIN दर्ज करें');
      return;
    }

    // Toggle lock status after successful verification
    const nextLocked = !accountLocked;
    setAccountLocked(nextLocked);
    setShowVerifyModal(false);
    setMpinInput('');
    setVerificationError('');

    setStatusNotification(
      nextLocked ? t.lockSuccessMsg : t.unlockSuccessMsg
    );
    setTimeout(() => setStatusNotification(null), 4000);
  };

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Top Banner */}
      <div
        className={`p-3.5 rounded-2xl border transition-colors ${
          isTiranga
            ? 'bg-gradient-to-r from-[#FFF5EB] via-white to-[#F0FDF4] border-[#FF671F]/30 text-slate-900 shadow-sm border-t-2 border-t-[#FF671F]'
            : isDark
            ? 'bg-[#0E1526] border-slate-800 text-slate-100'
            : 'bg-white border-slate-200 text-slate-900 shadow-sm'
        }`}
      >
        <div className="flex items-center gap-2.5">
          <div
            className={`w-8 h-8 rounded-xl text-white flex items-center justify-center font-bold ${
              isTiranga ? 'bg-[#046A38]' : 'bg-blue-600'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h3
              className={`text-xs sm:text-sm font-bold flex items-center gap-1.5 ${
                isTiranga ? 'text-slate-950' : isDark ? 'text-white' : 'text-slate-950'
              }`}
            >
              <span>{t.stressTitle}</span>
              <span className="w-2 h-2 rounded-full bg-[#046A38] animate-pulse" />
            </h3>
            <p
              className={`text-[11px] ${
                isDark ? 'text-slate-400' : 'text-slate-600'
              }`}
            >
              {t.stressSubtitle}
            </p>
          </div>
        </div>
      </div>

      {/* Status Notification Toast */}
      {statusNotification && (
        <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-700 dark:text-emerald-300 text-xs font-bold flex items-center gap-2 animate-fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
          <span>{statusNotification}</span>
        </div>
      )}

      {/* 1. Proactive Empathetic Intervention & Hardship Simulator (Pillar 3) */}
      <div
        className={`p-4 rounded-2xl border transition-colors ${
          isStressActive
            ? isDark
              ? 'bg-amber-500/10 border-amber-500/40 text-slate-100'
              : 'bg-amber-50 border-amber-300 text-slate-900'
            : isDark
            ? 'bg-[#0E1526] border-slate-800 text-slate-100'
            : 'bg-white border-slate-200 text-slate-900 shadow-sm'
        }`}
      >
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-2">
            <Activity className={`w-4 h-4 ${isStressActive ? 'text-amber-500' : 'text-blue-500'}`} />
            <h4
              className={`font-bold text-xs uppercase tracking-wider ${
                isDark ? 'text-slate-200' : 'text-slate-800'
              }`}
            >
              {t.distressSimulatorTitle}
            </h4>
          </div>
          <span
            className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${
              isStressActive
                ? 'bg-amber-500/20 text-amber-700 dark:text-amber-300 border-amber-500/40 animate-pulse'
                : 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30'
            }`}
          >
            {isStressActive
              ? lang === 'en' ? 'EARLY ASSISTANCE NEEDED' : 'वित्तीय सहायता संकेत सक्रिय'
              : lang === 'en' ? 'NORMAL HEALTHY ACCOUNT' : 'सामान्य खाता स्थिति'}
          </span>
        </div>

        <p
          className={`text-xs leading-relaxed mb-3 ${
            isDark ? 'text-slate-300' : 'text-slate-600'
          }`}
        >
          {lang === 'en'
            ? 'Detects sudden household distress (medical shocks, seasonal drops) to proactively offer assistance and suppress aggressive loan marketing.'
            : 'आकस्मिक कठिनाई (चिकित्सा खर्च, आय में गिरावट) की पहचान कर तुरंत दंडात्मक कार्रवाई के बदले सहायता प्रदान करता है।'}
        </p>

        {/* Simulation Controls */}
        {!isStressActive ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <button
              onClick={() => handleTriggerStress('medical')}
              className={`h-11 px-3.5 rounded-xl border font-bold text-xs inline-flex items-center justify-center gap-2 transition-colors ${
                isDark
                  ? 'bg-slate-900 border-amber-500/40 text-amber-300 hover:bg-slate-800'
                  : 'bg-white border-amber-300 text-amber-900 hover:bg-amber-50 shadow-sm'
              }`}
            >
              <TrendingDown className="w-4 h-4 text-amber-500 shrink-0" />
              <span>{lang === 'en' ? 'Simulate Emergency Medical Bill' : 'आपातकालीन चिकित्सा खर्च'}</span>
            </button>

            <button
              onClick={() => handleTriggerStress('income_dip')}
              className={`h-11 px-3.5 rounded-xl border font-bold text-xs inline-flex items-center justify-center gap-2 transition-colors ${
                isDark
                  ? 'bg-slate-900 border-slate-700 text-slate-300 hover:bg-slate-800'
                  : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50 shadow-sm'
              }`}
            >
              <TrendingDown className="w-4 h-4 text-blue-500 shrink-0" />
              <span>{lang === 'en' ? 'Simulate Sudden Inflow Dip (-60%)' : 'मासिक आय में 60% गिरावट'}</span>
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {/* Active Distress Interventions Box */}
            <div
              className={`p-3 rounded-xl border text-xs space-y-2 ${
                isDark
                  ? 'bg-black/40 border-amber-500/30 text-slate-200'
                  : 'bg-white border-amber-200 text-slate-800'
              }`}
            >
              <div className="flex items-center justify-between font-bold">
                <span className="text-amber-600 dark:text-amber-400 flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4" />
                  <span>
                    {stressType === 'medical'
                      ? lang === 'en' ? 'Sudden ₹18,500 Medical Debit Detected' : 'अचानक ₹18,500 का चिकित्सा खर्च दर्ज'
                      : lang === 'en' ? 'Cashflow Disruption: Monthly inflows down 62%' : 'व्यापारिक आवक में 62% की गिरावट'}
                  </span>
                </span>
              </div>

              {/* Empathetic Safeguards */}
              <div className="pt-2 border-t border-slate-200 dark:border-slate-800 space-y-1.5 text-[11px]">
                <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold">
                  <BellOff className="w-3.5 h-3.5 shrink-0" />
                  <span>{lang === 'en' ? '1. Promotional Loan Pop-ups Suppressed' : '1. सभी प्रचार व लोन ऑफर्स तुरंत निलंबित'}</span>
                </div>
                <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-bold">
                  <HeartHandshake className="w-3.5 h-3.5 shrink-0" />
                  <span>{lang === 'en' ? '2. Proactive 30-Day Zero Penalty Grace Period' : '2. 30 दिन की बिना किसी जुर्माने वाली मोहलत'}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300 font-bold">
                  <ShieldCheck className="w-3.5 h-3.5 shrink-0 text-emerald-500" />
                  <span>{lang === 'en' ? '3. No Adverse Credit Bureau (CIBIL) Impact' : '3. क्रेडिट ब्यूरो स्कोर पर कोई प्रतिकूल असर नहीं'}</span>
                </div>
              </div>
            </div>

            {/* Moratorium Button */}
            {!reliefActivated ? (
              <button
                onClick={() => setReliefActivated(true)}
                className="w-full h-11 px-4 rounded-xl bg-emerald-600 text-white font-bold text-xs hover:bg-emerald-500 transition-colors inline-flex items-center justify-center gap-2 shadow-sm"
              >
                <HeartHandshake className="w-4 h-4" />
                <span>{lang === 'en' ? 'Activate 30-Day Zero Penalty Moratorium' : '30 दिन की शून्य जुर्माना मोहलत शुरू करें'}</span>
              </button>
            ) : (
              <div className="h-11 px-3.5 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-700 dark:text-emerald-300 text-xs font-bold inline-flex items-center gap-2 w-full">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span className="truncate">
                  {lang === 'en'
                    ? 'Proactive relief active: Next payment deferred by 30 days.'
                    : 'राहत सक्रिय: अगली किस्त 30 दिन आगे बढ़ा दी गई है।'}
                </span>
              </div>
            )}

            <button
              onClick={handleRestoreNormal}
              className={`w-full h-11 px-4 rounded-xl border text-xs font-bold inline-flex items-center justify-center gap-2 transition-colors ${
                isDark
                  ? 'bg-slate-900 border-slate-700 text-slate-300 hover:bg-slate-800'
                  : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
              }`}
            >
              <RefreshCw className="w-4 h-4" />
              <span>{t.restoreNormalBtn}</span>
            </button>
          </div>
        )}
      </div>

      {/* 2. Real-Time Fraud & Phishing Interception Shield */}
      <div
        className={`p-4 rounded-2xl border transition-colors ${
          isDark
            ? 'bg-[#0E1526] border-slate-800 text-slate-100'
            : 'bg-white border-slate-200 text-slate-900 shadow-sm'
        }`}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <h4
              className={`font-bold text-xs uppercase tracking-wider ${
                isDark ? 'text-slate-200' : 'text-slate-800'
              }`}
            >
              {lang === 'en' ? 'Real-Time Fraud & Anomaly Shield' : 'लाइव धोखाधड़ी रोकथाम कवच'}
            </h4>
          </div>
          <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/30">
            Active Protection
          </span>
        </div>

        {/* Intercepted Alerts */}
        <div className="space-y-2 text-xs">
          <div
            className={`p-3 rounded-xl border space-y-1 ${
              isDark
                ? 'bg-slate-900/60 border-slate-800 text-slate-200'
                : 'bg-slate-50 border-slate-200 text-slate-800'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-bold flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{lang === 'en' ? 'Malicious Phishing SMS Blocked' : 'फर्जी एसएमएस लिंक रोका गया'}</span>
              </span>
              <span className="text-[10px] text-slate-500">15 Mins Ago</span>
            </div>
            <p
              className={`text-[11px] leading-relaxed ${
                isDark ? 'text-slate-300' : 'text-slate-600'
              }`}
            >
              {lang === 'en'
                ? 'Fake message requesting electricity bill verification via external link was intercepted before compromising account credentials.'
                : 'बिजली बिल के नाम पर फर्जी लिंक भेजकर ओटीपी चुराने वाला संदेश सफलतापूर्वक ब्लॉक किया गया।'}
            </p>
          </div>

          <div
            className={`p-3 rounded-xl border space-y-1 ${
              isDark
                ? 'bg-slate-900/60 border-slate-800 text-slate-200'
                : 'bg-slate-50 border-slate-200 text-slate-800'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-bold flex items-center gap-1.5 text-blue-600 dark:text-blue-400">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                <span>{lang === 'en' ? 'Device & SIM Binding Verified' : 'सिम व डिवाइस सुरक्षा सत्यापित'}</span>
              </span>
              <span className="text-[10px] text-slate-500">Continuous</span>
            </div>
            <p
              className={`text-[11px] leading-relaxed ${
                isDark ? 'text-slate-300' : 'text-slate-600'
              }`}
            >
              {lang === 'en'
                ? 'Registered mobile SIM is securely bound to this device. No remote-access mirroring tools detected.'
                : 'पंजीकृत सिम आपके फोन से पूरी तरह सत्यापित है। कोई रिमोट स्क्रीन ऐप मौजूद नहीं है।'}
            </p>
          </div>
        </div>

        {/* Account & UPI Lock with Mandatory Verification */}
        <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-3">
          <div>
            <span
              className={`text-xs font-bold block ${
                isDark ? 'text-slate-200' : 'text-slate-800'
              }`}
            >
              {t.securityLockTitle}
            </span>
            <span
              className={`text-[11px] ${
                isDark ? 'text-slate-400' : 'text-slate-500'
              }`}
            >
              {accountLocked
                ? lang === 'en' ? 'Status: Currently Locked (All debits paused)' : 'स्थिति: सुरक्षित लॉक (सभी निकासी रुकी हैं)'
                : lang === 'en' ? 'Status: Active & Protected' : 'स्थिति: सक्रिय एवं सुरक्षित'}
            </span>
          </div>

          <button
            onClick={handleOpenLockModal}
            className={`h-9 px-3.5 rounded-xl text-xs font-bold inline-flex items-center justify-center gap-2 transition-colors shadow-sm ${
              accountLocked
                ? 'bg-emerald-600 text-white hover:bg-emerald-500'
                : 'bg-red-600 text-white hover:bg-red-500'
            }`}
          >
            {accountLocked ? (
              <>
                <Unlock className="w-4 h-4" />
                <span>{lang === 'en' ? 'Unlock Account' : 'खाता अनलॉक करें'}</span>
              </>
            ) : (
              <>
                <Lock className="w-4 h-4" />
                <span>{lang === 'en' ? 'Freeze Account' : 'खाता लॉक करें'}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* VERIFICATION MODAL (Requires MPIN before freezing / unfreezing) */}
      {showVerifyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
          <form
            onSubmit={handleConfirmVerification}
            className={`w-full max-w-sm rounded-2xl border p-5 space-y-4 shadow-2xl ${
              isDark
                ? 'bg-[#0E1526] border-slate-700 text-slate-100'
                : 'bg-white border-slate-300 text-slate-900'
            }`}
          >
            <div className="flex items-center justify-between border-b pb-2 border-slate-200 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <KeyRound className="w-4 h-4 text-blue-500" />
                <span className="font-bold text-xs uppercase tracking-wider">
                  {lang === 'en' ? 'Security Verification Required' : 'सुरक्षा सत्यापन आवश्यक'}
                </span>
              </div>
              <button
                type="button"
                onClick={() => setShowVerifyModal(false)}
                className="w-8 h-8 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-400 hover:text-slate-700 dark:hover:text-white text-xs font-bold inline-flex items-center justify-center transition-colors"
              >
                ✕
              </button>
            </div>

            <p
              className={`text-xs leading-relaxed ${
                isDark ? 'text-slate-300' : 'text-slate-600'
              }`}
            >
              {accountLocked
                ? lang === 'en'
                  ? 'To restore outgoing UPI payments and ATM withdrawals, please verify with your 4-digit banking MPIN.'
                  : 'खाते से पुनः भुगतान शुरू करने के लिए अपना 4 अंकों का बैंकिंग MPIN दर्ज करें।'
                : lang === 'en'
                  ? 'Freezing will immediately pause all outgoing UPI, card, and net banking debits. Enter your 4-digit MPIN to confirm.'
                  : 'खाता लॉक करने पर सभी यूपीआई और कार्ड निकासी तुरंत रुक जाएगी। पुष्टि हेतु अपना 4 अंकों का MPIN दर्ज करें।'}
            </p>

            {/* Reason Selector */}
            {!accountLocked && (
              <div className="space-y-1">
                <label
                  className={`text-[11px] font-semibold block ${
                    isDark ? 'text-slate-300' : 'text-slate-700'
                  }`}
                >
                  {lang === 'en' ? 'Reason for freeze:' : 'लॉक करने का कारण:'}
                </label>
                <select
                  value={lockReason}
                  onChange={(e) => setLockReason(e.target.value)}
                  className={`w-full text-xs p-2 rounded-xl border outline-none ${
                    isDark
                      ? 'bg-slate-900 border-slate-700 text-white'
                      : 'bg-slate-50 border-slate-300 text-slate-900'
                  }`}
                >
                  <option value="suspicious_activity">
                    {lang === 'en' ? 'Suspicious SMS or call received' : 'संदिग्ध कॉल या संदेश प्राप्त हुआ'}
                  </option>
                  <option value="lost_phone">
                    {lang === 'en' ? 'Misplaced phone / SIM card' : 'फोन या सिम कार्ड खो गया'}
                  </option>
                  <option value="precautionary">
                    {lang === 'en' ? 'Temporary safety precaution' : 'अस्थायी सुरक्षा सावधानी'}
                  </option>
                </select>
              </div>
            )}

            {/* MPIN Input */}
            <div className="space-y-1">
              <label
                className={`text-[11px] font-semibold block ${
                  isDark ? 'text-slate-300' : 'text-slate-700'
                }`}
              >
                {t.enterMpin}
              </label>
              <input
                type="password"
                maxLength={4}
                autoFocus
                value={mpinInput}
                onChange={(e) => {
                  const val = e.target.value.replace(/\D/g, '');
                  setMpinInput(val);
                  setVerificationError('');
                }}
                placeholder="••••"
                className={`w-full text-center tracking-[1em] text-lg font-mono p-2.5 rounded-xl border outline-none font-bold ${
                  isDark
                    ? 'bg-slate-900 border-slate-700 text-white focus:border-blue-500'
                    : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-blue-600'
                }`}
              />
              {verificationError && (
                <p className="text-[11px] text-red-500 font-semibold">{verificationError}</p>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowVerifyModal(false)}
                className={`flex-1 h-11 rounded-xl border text-xs font-bold inline-flex items-center justify-center transition-colors ${
                  isDark
                    ? 'border-slate-700 text-slate-300 hover:bg-slate-800'
                    : 'border-slate-300 text-slate-700 hover:bg-slate-100'
                }`}
              >
                {t.cancel}
              </button>
              <button
                type="submit"
                className={`flex-1 h-11 rounded-xl text-xs font-bold text-white inline-flex items-center justify-center transition-colors ${
                  accountLocked
                    ? 'bg-emerald-600 hover:bg-emerald-500'
                    : 'bg-red-600 hover:bg-red-500'
                }`}
              >
                {accountLocked ? t.confirmUnlock : t.confirmLock}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
