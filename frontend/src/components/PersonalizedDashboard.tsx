import React, { useState } from 'react';
import { PersonaProfile, Language, ThemeMode, FrequentPayee } from '../types';
import { translations } from '../data/translations';
import { mockPersonas, mockFrequentPayees } from '../data/mockData';
import { VerifiedAccountCard } from './VerifiedAccountCard';
import { ActionCardsGrid } from './ActionCardsGrid';
import { FrequentPayeesRow } from './FrequentPayeesRow';
import { SmartLoanCard } from './SmartLoanCard';
import {
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  FileText,
  Bot,
  HelpCircle,
  Clock,
  ArrowUpRight,
  TrendingUp,
  ExternalLink,
  ChevronRight,
  AlertTriangle
} from 'lucide-react';

interface PersonalizedDashboardProps {
  activePersona: PersonaProfile;
  onSelectPersona: (p: PersonaProfile) => void;
  lang: Language;
  theme: ThemeMode;
  onNavigateToSakhi: (contextText?: string) => void;
  isStressActive: boolean;
  onSendMoney: () => void;
  onScanQr: () => void;
  onReceiveMoney: () => void;
  onBillsUtilities: () => void;
  onSelectPayee: (payee: FrequentPayee) => void;
  onTriggerScamTest: (payee: FrequentPayee) => void;
  onAcceptLoan: () => void;
  onVerifyClick: () => void;
  onDpdpClick: () => void;
  isLoanDisbursed: boolean;
  onLogout: () => void;
}

export const PersonalizedDashboard: React.FC<PersonalizedDashboardProps> = ({
  activePersona,
  onSelectPersona,
  lang,
  theme,
  onNavigateToSakhi,
  isStressActive,
  onSendMoney,
  onScanQr,
  onReceiveMoney,
  onBillsUtilities,
  onSelectPayee,
  onTriggerScamTest,
  onAcceptLoan,
  onVerifyClick,
  onDpdpClick,
  isLoanDisbursed,
  onLogout,
}) => {
  const t = translations[lang];
  const isDark = theme === 'dark';
  // Light theme is intrinsically the authentic Indian Tiranga theme
  const isTiranga = !isDark;
  const [showKfsModal, setShowKfsModal] = useState(false);
  const [showExplainModal, setShowExplainModal] = useState(false);

  const product = activePersona.recommendedProduct;

  return (
    <div className="space-y-4 sm:space-y-5 animate-fade-in">
      {/* 1. Verified Citizen Banking Account Card */}
      <VerifiedAccountCard
        activePersona={activePersona}
        lang={lang}
        theme={theme}
        onVerifyClick={onVerifyClick}
        onDpdpClick={onDpdpClick}
        onLogout={onLogout}
      />

      {/* 2. Four Big Colorful Action Cards (Image 1: Send Money, Scan Any QR, Receive / My QR, Bills & Utilities) */}
      <ActionCardsGrid
        lang={lang}
        onSendMoney={onSendMoney}
        onScanQr={onScanQr}
        onReceiveMoney={onReceiveMoney}
        onBillsUtilities={onBillsUtilities}
      />

      {/* 3. Frequent Payees 1-Tap Transfer Row (Image 3) */}
      <FrequentPayeesRow
        payees={mockFrequentPayees}
        lang={lang}
        theme={theme}
        onSelectPayee={onSelectPayee}
        onTriggerScamTest={onTriggerScamTest}
      />

      {/* 4. Smart AI Working Capital Loan Card (Image 2) */}
      <SmartLoanCard
        lang={lang}
        theme={theme}
        onAcceptLoan={onAcceptLoan}
        isLoanDisbursed={isLoanDisbursed}
      />

      {/* Lively Bharat Digital Public Infrastructure Banner (Tiranga) */}
      <div
        className={`p-3.5 rounded-2xl border transition-all select-none relative overflow-hidden ${
          isTiranga
            ? 'bg-gradient-to-r from-[#FFF5EB] via-white to-[#F0FDF4] border-[#FF671F]/40 text-slate-900 shadow-md shadow-orange-500/5'
            : 'bg-gradient-to-r from-[#0E1526] via-[#111A30] to-[#0A1F18] border-slate-800 text-slate-100 shadow-md'
        }`}
      >
        <div className="flex items-center justify-between gap-2.5 relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#FF671F] via-[#FF8C38] to-[#046A38] p-0.5 shadow-sm flex items-center justify-center shrink-0">
              <div className="w-full h-full bg-white dark:bg-slate-900 rounded-[14px] flex items-center justify-center">
                <span className="text-xl leading-none">🇮🇳</span>
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-black tracking-tight bg-gradient-to-r from-[#FF671F] via-[#000080] to-[#046A38] bg-clip-text text-transparent dark:text-white">
                  {lang === 'en' ? 'NEO-BHARAT DIGITAL INCLUSION' : 'नियो-भारत डिजिटल समावेश'}
                </span>
                <span className="inline-flex items-center gap-1 text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-[#046A38]"></span>
                  </span>
                  <span>{lang === 'en' ? 'Live DPI & AA 2.0' : 'लाइव डीपीआई व एए'}</span>
                </span>
              </div>
              <p className="text-[11px] text-slate-600 dark:text-slate-300 mt-0.5 font-medium">
                {lang === 'en'
                  ? 'Official RBI Fair-Lending compliant · Zero hidden charges · Instant 8-min UPI disbursal'
                  : 'आरबीआई निष्पक्ष ऋण नियम प्रमाणित · शून्य गुप्त शुल्क · तुरंत यूपीआई संवितरण'}
              </p>
            </div>
          </div>
        </div>

        {/* Lively quick badge row */}
        <div className="mt-2.5 pt-2 border-t border-slate-200/80 dark:border-slate-800/80 flex items-center gap-1.5 overflow-x-auto no-scrollbar text-[10px] font-bold">
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-orange-500/10 text-[#FF671F] border border-[#FF671F]/30 shrink-0">
            <span>⚡</span>
            <span>{lang === 'en' ? 'Instant UPI Disbursal' : 'त्वरित यूपीआई भुगतान'}</span>
          </span>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-emerald-500/10 text-[#046A38] dark:text-emerald-400 border border-emerald-500/30 shrink-0">
            <span>🌾</span>
            <span>{lang === 'en' ? 'Zero-Penalty Moratorium' : 'शून्य जुर्माना राहत'}</span>
          </span>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-blue-500/10 text-blue-700 dark:text-blue-400 border border-blue-500/30 shrink-0">
            <span>🛡️</span>
            <span>{lang === 'en' ? '100% KFS Transparency' : '100% स्पष्ट केएफएस'}</span>
          </span>
        </div>
      </div>

      <div
        className={`p-3.5 rounded-2xl border transition-all border-dashed border-red-500/50 bg-red-50/10`}
      >
        <div className="flex items-center justify-between gap-2 mb-2.5">
          <div className="flex items-center gap-1.5">
            <span
              className={`text-xs font-black uppercase tracking-wider text-red-500`}
            >
              DEMO / DEV FEATURE
            </span>
          </div>
          <span
            className={`text-[11px] font-medium ${
              isDark ? 'text-slate-400' : 'text-slate-500'
            }`}
          >
            {lang === 'en' ? 'Quick switch' : 'त्वरित बदलें'}
          </span>
        </div>

        {/* 3 Lively Profile Selector Buttons */}
        <div className="grid grid-cols-3 gap-2">
          {mockPersonas.map((persona) => {
            const isSelected = persona.id === activePersona.id;
            const personaIcons: Record<string, string> = {
              ramesh: '🌾',
              priya: '🧵',
              sunil: '🛵',
            };

            return (
              <button
                key={persona.id}
                onClick={() => onSelectPersona(persona)}
                className={`p-2.5 rounded-xl text-left border transition-all flex flex-col justify-between relative overflow-hidden group hover:scale-[1.02] ${
                  isSelected
                    ? isTiranga
                      ? 'bg-gradient-to-br from-orange-50/90 via-white to-amber-50/50 border-[#FF671F] text-slate-950 shadow-md ring-2 ring-[#FF671F]/30'
                      : 'bg-gradient-to-br from-blue-900/40 via-slate-900 to-indigo-950/40 border-blue-500 text-white shadow-md ring-2 ring-blue-500/30'
                    : isDark
                    ? 'bg-slate-900/70 border-slate-800 text-slate-300 hover:bg-slate-800 hover:border-slate-700'
                    : 'bg-slate-50/90 border-slate-200 text-slate-700 hover:bg-orange-50/50 hover:border-orange-200'
                }`}
              >
                <div className="flex items-center justify-between w-full mb-1">
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm leading-none">{personaIcons[persona.id] || '👤'}</span>
                    <span className="font-extrabold text-xs tracking-tight">
                      {lang === 'en' ? persona.name.split(' ')[0] : persona.hindiName.split(' ')[0]}
                    </span>
                  </div>
                  {isSelected ? (
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#FF671F] opacity-75" />
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-[#FF671F]" />
                    </span>
                  ) : (
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-300 dark:bg-slate-700" />
                  )}
                </div>

                <p
                  className={`text-[10px] truncate font-medium ${
                    isSelected ? (isDark ? 'text-slate-200' : 'text-slate-800') : (isDark ? 'text-slate-400' : 'text-slate-500')
                  }`}
                >
                  {lang === 'en' ? persona.occupation.split('&')[0] : persona.hindiOccupation.split('&')[0]}
                </p>

                <div className="mt-1 flex items-center justify-between text-[10px] font-mono font-bold">
                  <span className="text-emerald-600 dark:text-emerald-400">
                    ₹{(persona.monthlyIncome / 1000).toFixed(0)}k/mo
                  </span>
                  <span className="text-[9px] font-sans px-1 rounded bg-slate-200/60 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                    {persona.creditHealthScore} pts
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Available Balance & Financial Overview */}
      <div
        className={`p-4 rounded-2xl border transition-all relative overflow-hidden ${
          isTiranga
            ? 'bg-gradient-to-br from-white via-[#FFFBF7] to-[#F5FFF8] border-[#FF671F]/30 text-slate-900 shadow-md shadow-orange-500/5'
            : 'bg-[#0E1526] border-slate-800 text-slate-100 shadow-md'
        }`}
      >
        <div className="flex items-center justify-between pb-3.5 border-b border-slate-200 dark:border-slate-800">
          <div>
            <div className="flex items-center gap-1.5">
              <span
                className={`text-xs font-bold uppercase tracking-wider block ${
                  isTiranga ? 'text-[#FF671F]' : 'text-slate-400'
                }`}
              >
                {t.accountBalance}
              </span>
              <span className="text-[9.5px] font-extrabold px-1.5 py-0.2 rounded bg-emerald-500/10 text-[#046A38] dark:text-emerald-400 border border-emerald-500/30">
                UPI Active
              </span>
            </div>
            <div
              className={`text-2xl sm:text-3xl font-black mt-0.5 tracking-tight ${
                isDark ? 'text-white' : 'text-slate-950'
              }`}
            >
              ₹{activePersona.accountBalance.toLocaleString('en-IN')}
            </div>
            <span
              className={`text-[11px] font-medium block mt-0.5 ${
                isDark ? 'text-slate-400' : 'text-slate-500'
              }`}
            >
              A/C {activePersona.accountNumber} · {activePersona.location}
            </span>
          </div>

          <div className="text-right flex flex-col items-end">
            <span
              className={`text-[11px] font-bold uppercase tracking-wider block ${
                isDark ? 'text-slate-400' : 'text-slate-500'
              }`}
            >
              {t.financialHealth}
            </span>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-gradient-to-r from-emerald-500/15 via-emerald-500/10 to-teal-500/15 border border-emerald-500/40 text-emerald-700 dark:text-emerald-400 mt-1 font-black shadow-sm">
              <ShieldCheck className="w-4 h-4 text-[#046A38] dark:text-emerald-400 shrink-0" />
              <span className="font-mono text-xs">{activePersona.creditHealthScore}/100</span>
              <span className="text-[10px] font-sans font-bold text-emerald-600 dark:text-emerald-400">
                {activePersona.creditHealthScore >= 80 ? (lang === 'en' ? 'Excellent' : 'उत्कृष्ट') : (lang === 'en' ? 'Good' : 'अच्छा')}
              </span>
            </div>
            <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold mt-0.5">
              ↗ {lang === 'en' ? '+8 pts this month' : '+8 अंक इस माह'}
            </span>
          </div>
        </div>

        {/* Inflow vs Outflow & Live Surplus */}
        <div className="grid grid-cols-2 gap-2.5 pt-3">
          <div
            className={`p-2.5 rounded-xl border transition-colors ${
              isDark
                ? 'bg-slate-900/60 border-slate-800 text-slate-200'
                : 'bg-emerald-50/70 border-emerald-200/80 text-emerald-950'
            }`}
          >
            <div className="flex items-center justify-between">
              <span
                className={`text-[11px] font-bold block ${
                  isDark ? 'text-emerald-400' : 'text-emerald-700'
                }`}
              >
                {t.monthlyInflow}
              </span>
              <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 font-bold">
                ▲ UPI + Cash
              </span>
            </div>
            <span
              className={`text-base font-black font-mono mt-0.5 block ${
                isDark ? 'text-white' : 'text-slate-900'
              }`}
            >
              +₹{activePersona.monthlyIncome.toLocaleString('en-IN')}
            </span>
          </div>

          <div
            className={`p-2.5 rounded-xl border transition-colors ${
              isDark
                ? 'bg-slate-900/60 border-slate-800 text-slate-200'
                : 'bg-blue-50/70 border-blue-200/80 text-blue-950'
            }`}
          >
            <div className="flex items-center justify-between">
              <span
                className={`text-[11px] font-bold block ${
                  isDark ? 'text-blue-400' : 'text-blue-700'
                }`}
              >
                {t.monthlyOutflow}
              </span>
              <span className="text-[10px] font-mono text-slate-500 font-bold">
                ▼ Living + Ops
              </span>
            </div>
            <span
              className={`text-base font-black font-mono mt-0.5 block ${
                isDark ? 'text-white' : 'text-slate-900'
              }`}
            >
              -₹{activePersona.monthlyExpense.toLocaleString('en-IN')}
            </span>
          </div>
        </div>

        {/* Dynamic Cashflow Surplus Bar */}
        <div className="mt-2.5 pt-2 border-t border-slate-200/60 dark:border-slate-800/60 flex items-center justify-between text-[11px]">
          <span className="text-slate-500 dark:text-slate-400 font-medium">
            {lang === 'en' ? 'Estimated Monthly Surplus:' : 'मासिक शुद्ध बचत:'}
          </span>
          <span className="font-extrabold font-mono text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/30">
            +₹{(activePersona.monthlyIncome - activePersona.monthlyExpense).toLocaleString('en-IN')}
          </span>
        </div>
      </div>

      {/* 3. Detected Life-Stage Signal / Identified Opportunity */}
      <div
        className={`p-3.5 rounded-2xl border transition-all ${
          isTiranga
            ? 'bg-gradient-to-r from-orange-50/70 via-white to-amber-50/50 border-orange-200 text-slate-900 shadow-sm'
            : 'bg-[#0E1526] border-blue-500/30 text-slate-100 shadow-sm'
        }`}
      >
        <div className="flex items-start gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#FF671F] to-[#E65100] text-white flex items-center justify-center shrink-0 mt-0.5 font-bold shadow-sm shadow-orange-500/30">
            <Sparkles className="w-4 h-4 animate-pulse" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5">
              <span
                className={`text-[11px] font-bold block ${
                  isTiranga ? 'text-[#FF671F]' : 'text-blue-400'
                }`}
              >
                {t.lifeStageSignalTitle}
              </span>
              <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-amber-500/15 text-amber-800 dark:text-amber-300 border border-amber-500/30">
                {lang === 'en' ? 'AI Insight' : 'एआई संकेत'}
              </span>
            </div>
            <h4
              className={`text-xs sm:text-sm font-bold mt-0.5 ${
                isDark ? 'text-white' : 'text-slate-950'
              }`}
            >
              {lang === 'en' ? activePersona.lifeStageSignal : activePersona.hindiLifeStageSignal}
            </h4>
            <p
              className={`text-[11px] mt-0.5 leading-relaxed ${
                isDark ? 'text-slate-300' : 'text-slate-600'
              }`}
            >
              {lang === 'en' ? activePersona.primaryNeed : activePersona.hindiPrimaryNeed}
            </p>
          </div>
        </div>
      </div>

      {/* 4. PROACTIVE RELEVANT RECOMMENDATION CARD (Pillar 1) */}
      {isStressActive ? (
        /* When financial stress is active -> Anti-Predatory Safeguard replaces commercial credit offers! */
        <div
          className={`p-4 rounded-2xl border ${
            isDark
              ? 'bg-amber-500/10 border-amber-500/40 text-slate-100'
              : 'bg-amber-50 border-amber-300 text-amber-950'
          } space-y-2.5`}
        >
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0" />
            <h3 className="font-bold text-xs sm:text-sm text-amber-900 dark:text-amber-300">
              {t.stressActiveAlert}
            </h3>
          </div>
          <p
            className={`text-xs leading-relaxed ${
              isDark ? 'text-slate-300' : 'text-slate-700'
            }`}
          >
            {t.stressExplanation}
          </p>
          <div
            className={`p-3 rounded-xl border text-xs space-y-1 ${
              isDark
                ? 'bg-black/40 border-amber-500/20 text-slate-200'
                : 'bg-white border-amber-200 text-slate-800'
            }`}
          >
            <div className="flex items-center gap-1.5 font-bold text-emerald-600 dark:text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span>
                {lang === 'en'
                  ? '30-Day Zero Penalty Moratorium Available'
                  : '30 दिन की बिना किसी जुर्माने वाली राहत उपलब्ध'}
              </span>
            </div>
            <p className="text-[11px] opacity-80">
              {lang === 'en'
                ? 'No adverse reporting to credit bureaus. Go to Protection & Safety tab to activate.'
                : 'क्रेडिट स्कोर पर कोई प्रतिकूल प्रभाव नहीं पड़ेगा।'}
            </p>
          </div>
        </div>
      ) : (
        /* Standard Proactive Contextual Recommendation */
        <div
          className={`p-4 rounded-2xl border transition-colors ${
            isTiranga
              ? 'bg-white border-slate-200 border-t-4 border-t-[#FF671F] text-slate-900 shadow-lg ring-1 ring-orange-100'
              : isDark
              ? 'bg-[#0E1526] border-blue-500/40 text-slate-100 shadow-xl'
              : 'bg-white border-blue-300 text-slate-900 shadow-md ring-1 ring-blue-100'
          }`}
        >
          {/* Top Pill */}
          <div className="flex items-center justify-between gap-2 mb-2">
            <div className="flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full animate-pulse ${
                  isTiranga ? 'bg-[#FF671F]' : 'bg-blue-500'
                }`}
              />
              <span
                className={`text-[11px] font-bold uppercase tracking-wider ${
                  isTiranga
                    ? 'text-[#FF671F]'
                    : isDark ? 'text-blue-400' : 'text-blue-700'
                }`}
              >
                {t.personalizedOfferHeader}
              </span>
            </div>
            <span
              className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                isTiranga
                  ? 'bg-[#046A38]/10 border-[#046A38]/30 text-[#046A38]'
                  : isDark
                  ? 'bg-blue-500/20 border-blue-500/30 text-blue-300'
                  : 'bg-blue-50 border-blue-200 text-blue-800'
              }`}
            >
              {lang === 'en' ? product.categoryBadge : product.hindiCategoryBadge}
            </span>
          </div>

          <h3
            className={`text-base sm:text-lg font-black tracking-tight ${
              isDark ? 'text-white' : 'text-slate-950'
            }`}
          >
            {lang === 'en' ? product.title : product.hindiTitle}
          </h3>

          {/* Key Loan / Product Numbers Grid */}
          <div
            className={`grid grid-cols-3 gap-2 my-3 p-3 rounded-xl border ${
              isDark
                ? 'bg-slate-900/80 border-slate-800 text-slate-100'
                : 'bg-slate-50 border-slate-200 text-slate-900'
            }`}
          >
            <div>
              <span
                className={`text-[10px] font-semibold block ${
                  isDark ? 'text-slate-400' : 'text-slate-500'
                }`}
              >
                {lang === 'en' ? 'Sanctioned Limit' : 'स्वीकृत सीमा'}
              </span>
              <span
                className={`text-sm sm:text-base font-black font-mono ${
                  isDark ? 'text-amber-400' : 'text-amber-700'
                }`}
              >
                {product.amountOrCover}
              </span>
            </div>

            <div>
              <span
                className={`text-[10px] font-semibold block ${
                  isDark ? 'text-slate-400' : 'text-slate-500'
                }`}
              >
                {lang === 'en' ? 'Transparent APR' : 'वार्षिक ब्याज'}
              </span>
              <span
                className={`text-sm sm:text-base font-black font-mono ${
                  isDark ? 'text-emerald-400' : 'text-emerald-700'
                }`}
              >
                {lang === 'en' ? product.rateOrCost.split('(')[0] : product.hindiRateOrCost.split('(')[0]}
              </span>
            </div>

            <div>
              <span
                className={`text-[10px] font-semibold block ${
                  isDark ? 'text-slate-400' : 'text-slate-500'
                }`}
              >
                {lang === 'en' ? 'Tenure' : 'अवधि'}
              </span>
              <span
                className={`text-xs sm:text-sm font-bold ${
                  isDark ? 'text-slate-200' : 'text-slate-800'
                }`}
              >
                {lang === 'en' ? product.tenure.split('(')[0] : product.hindiTenure.split('(')[0]}
              </span>
            </div>
          </div>

          <p
            className={`text-xs leading-relaxed mb-3 ${
              isDark ? 'text-slate-300' : 'text-slate-700'
            }`}
          >
            <strong className={isDark ? 'text-white' : 'text-slate-900'}>
              {lang === 'en' ? 'Repayment: ' : 'भुगतान: '}
            </strong>
            {product.monthlyCommitment}
          </p>

          {/* Customer-Friendly "Why Recommended for You" Box */}
          <div
            className={`p-3 rounded-xl border space-y-2 mb-3 ${
              isDark
                ? 'bg-slate-900/60 border-slate-800 text-slate-200'
                : 'bg-slate-50 border-slate-200 text-slate-800'
            }`}
          >
            <div className="flex items-center justify-between">
              <span
                className={`text-xs font-bold flex items-center gap-1.5 ${
                  isDark ? 'text-blue-400' : 'text-blue-700'
                }`}
              >
                <HelpCircle className="w-3.5 h-3.5" />
                <span>{t.whyRecommendedTitle}</span>
              </span>
              <span
                className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${
                  isDark
                    ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
                    : 'bg-emerald-50 border-emerald-200 text-emerald-800'
                }`}
              >
                {product.whyRecommended.confidenceScore}% {t.confidenceScore}
              </span>
            </div>

            <p
              className={`text-xs leading-relaxed ${
                isDark ? 'text-slate-300' : 'text-slate-700'
              }`}
            >
              {lang === 'en'
                ? product.whyRecommended.aiTriggerSummary
                : product.whyRecommended.hindiAiTriggerSummary}
            </p>

            <button
              onClick={() => setShowExplainModal(true)}
              className={`h-8 px-3 rounded-lg border text-xs font-bold inline-flex items-center gap-1.5 transition-colors ${
                isTiranga
                  ? 'bg-white border-[#FF671F]/30 text-[#FF671F] hover:bg-orange-50'
                  : isDark
                  ? 'bg-slate-900 border-slate-700 text-blue-400 hover:bg-slate-800'
                  : 'bg-white border-blue-200 text-blue-700 hover:bg-blue-50'
              }`}
            >
              <span>{lang === 'en' ? 'View Details on Cashflow Match →' : 'विस्तृत कैशफ्लो विवरण देखें →'}</span>
            </button>
          </div>

          {/* Action Row: Apply with Sakhi Voice Assistant vs View RBI KFS */}
          <div className="flex flex-col sm:flex-row gap-2.5">
            <button
              onClick={() => onNavigateToSakhi(`I would like to apply for ${lang === 'en' ? product.title : product.hindiTitle}`)}
              className={`flex-1 h-11 px-4 rounded-xl text-white font-bold text-xs sm:text-sm inline-flex items-center justify-center gap-2 shadow-md transition-transform active:scale-98 ${
                isTiranga
                  ? 'bg-gradient-to-r from-[#FF671F] via-[#000080] to-[#046A38] hover:opacity-95 shadow-orange-500/20'
                  : 'bg-blue-600 hover:bg-blue-500'
              }`}
            >
              <Bot className="w-4 h-4 text-white shrink-0" />
              <span>{t.applyWithSakhi}</span>
            </button>

            <button
              onClick={() => setShowKfsModal(true)}
              className={`h-11 px-4 rounded-xl border text-xs sm:text-sm font-bold inline-flex items-center justify-center gap-2 transition-colors ${
                isDark
                  ? 'bg-slate-900 border-slate-700 text-slate-200 hover:bg-slate-800'
                  : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-100'
              }`}
            >
              <FileText className="w-4 h-4 text-slate-400 shrink-0" />
              <span>{lang === 'en' ? 'Key Facts (KFS)' : 'मुख्य तथ्य (KFS)'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Modal 1: RBI Key Facts Statement (KFS) */}
      {showKfsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
          <div
            className={`w-full max-w-md rounded-2xl border p-5 space-y-4 shadow-2xl ${
              isDark
                ? 'bg-[#0E1526] border-slate-700 text-slate-100'
                : 'bg-white border-slate-300 text-slate-900'
            }`}
          >
            <div className="flex items-center justify-between border-b pb-2 border-slate-200 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-500" />
                <span className="font-bold text-xs uppercase tracking-wider">
                  RBI Master Direction · Key Facts Statement
                </span>
              </div>
              <button
                onClick={() => setShowKfsModal(false)}
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
              {lang === 'en'
                ? 'Mandatory disclosure statement complying with RBI Digital Lending Directives. 100% transparent terms with zero hidden charges.'
                : 'आरबीआई डिजिटल लेंडिंग दिशानिर्देशों के अनुसार पारदर्शी खुलासा विवरण। कोई छुपा हुआ शुल्क नहीं।'}
            </p>

            <div className="space-y-2 text-xs divide-y divide-slate-200 dark:divide-slate-800">
              <div className="flex justify-between pt-1.5">
                <span className={isDark ? 'text-slate-400' : 'text-slate-600'}>
                  {lang === 'en' ? 'Annual Percentage Rate (APR):' : 'वार्षिक ब्याज दर (APR):'}
                </span>
                <span className="font-bold font-mono text-emerald-600 dark:text-emerald-400">
                  {product.keyFactsStatement.apr}
                </span>
              </div>
              <div className="flex justify-between pt-1.5">
                <span className={isDark ? 'text-slate-400' : 'text-slate-600'}>
                  {lang === 'en' ? 'Processing Fees:' : 'प्रोसेसिंग फीस:'}
                </span>
                <span className="font-bold text-blue-600 dark:text-blue-400">
                  {product.keyFactsStatement.processingFee}
                </span>
              </div>
              <div className="flex justify-between pt-1.5">
                <span className={isDark ? 'text-slate-400' : 'text-slate-600'}>
                  {lang === 'en' ? 'Prepayment / Foreclosure:' : 'पूर्व भुगतान शुल्क:'}
                </span>
                <span className="font-bold text-emerald-600 dark:text-emerald-400">
                  {product.keyFactsStatement.prepaymentPenalty}
                </span>
              </div>
              <div className="flex justify-between pt-1.5">
                <span className={isDark ? 'text-slate-400' : 'text-slate-600'}>
                  {lang === 'en' ? 'Cooling-off Period:' : 'कूलिंग-ऑफ अवधि:'}
                </span>
                <span className="font-bold">3 Days (Exit anytime with zero penalty)</span>
              </div>
              <div className="flex justify-between pt-1.5">
                <span className={isDark ? 'text-slate-400' : 'text-slate-600'}>
                  {lang === 'en' ? 'Official RBI Guidelines URL:' : 'आधिकारिक आरबीआई लिंक:'}
                </span>
                <a
                  href={product.keyFactsStatement.rbiDirectUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-bold text-blue-600 dark:text-blue-400 underline flex items-center gap-1"
                >
                  <span>rbi.org.in</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>

            <button
              onClick={() => setShowKfsModal(false)}
              className="w-full h-11 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs sm:text-sm inline-flex items-center justify-center transition-colors"
            >
              {lang === 'en' ? 'Close Statement' : 'बंद करें'}
            </button>
          </div>
        </div>
      )}

      {/* Modal 2: Details on Cashflow Match */}
      {showExplainModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
          <div
            className={`w-full max-w-md rounded-2xl border p-5 space-y-4 shadow-2xl ${
              isDark
                ? 'bg-[#0E1526] border-slate-700 text-slate-100'
                : 'bg-white border-slate-300 text-slate-900'
            }`}
          >
            <div className="flex items-center justify-between border-b pb-2 border-slate-200 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-blue-500" />
                <span className="font-bold text-xs uppercase tracking-wider">
                  {lang === 'en' ? 'Cashflow Analysis Behind Recommendation' : 'सिफारिश के पीछे का कैशफ्लो विश्लेषण'}
                </span>
              </div>
              <button
                onClick={() => setShowExplainModal(false)}
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
              {lang === 'en'
                ? 'Our recommendation is matched strictly to your verified banking track record, ensuring affordability and avoiding burdensome credit.'
                : 'यह सिफारिश पूरी तरह से आपके बैंक खाते के वास्तविक लेन-देन के आधार पर की गई है, ताकि आप पर कोई अनावश्यक बोझ न पड़े।'}
            </p>

            <div className="space-y-2">
              {(lang === 'en'
                ? product.whyRecommended.dataPointsAnalyzed
                : product.whyRecommended.hindiDataPointsAnalyzed
              ).map((point, idx) => (
                <div
                  key={idx}
                  className={`flex items-start gap-2 p-2.5 rounded-xl border text-xs ${
                    isDark
                      ? 'bg-slate-900/80 border-slate-800 text-slate-200'
                      : 'bg-slate-50 border-slate-200 text-slate-800'
                  }`}
                >
                  <span className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                    ✓
                  </span>
                  <span className="leading-relaxed">{point}</span>
                </div>
              ))}
            </div>

            <button
              onClick={() => setShowExplainModal(false)}
              className="w-full h-11 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs sm:text-sm inline-flex items-center justify-center transition-colors"
            >
              {lang === 'en' ? 'Close' : 'बंद करें'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
