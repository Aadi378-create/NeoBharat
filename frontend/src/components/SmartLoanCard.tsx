import React from 'react';
import { Language, ThemeMode } from '../types';
import { Sparkles, Fingerprint, CheckCircle2 } from 'lucide-react';

interface SmartLoanCardProps {
  lang: Language;
  theme: ThemeMode;
  onAcceptLoan: () => void;
  isLoanDisbursed?: boolean;
}

export const SmartLoanCard: React.FC<SmartLoanCardProps> = ({
  lang,
  theme,
  onAcceptLoan,
  isLoanDisbursed = false,
}) => {
  const isDark = theme === 'dark';

  return (
    <div
      className={`w-full rounded-2xl sm:rounded-3xl border transition-all p-4 sm:p-5 relative overflow-hidden shadow-xl ${
        isDark
          ? 'bg-[#0B1020] border-slate-800/90 text-slate-100 shadow-black/50'
          : 'bg-white border-[#FF671F]/30 text-slate-900 shadow-orange-500/5'
      }`}
    >
      {/* Top row: Badge & Zero Paperwork */}
      <div className="flex items-center justify-between gap-2">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10.5px] sm:text-xs font-black uppercase tracking-wider bg-orange-500/15 border border-[#FF671F]/50 text-[#FF671F]">
          <Sparkles className="w-3.5 h-3.5 text-[#FF671F] shrink-0" />
          <span>{lang === 'en' ? 'SMART AI WORKING CAPITAL LOAN' : 'स्मार्ट एआई कार्यशील पूंजी ऋण'}</span>
        </div>

        <span className="text-xs sm:text-sm font-bold text-emerald-400 shrink-0">
          {lang === 'en' ? 'Zero Paperwork' : 'शून्य दस्तावेज़'}
        </span>
      </div>

      {/* Main Title & Subtitle */}
      <h2
        className={`text-lg sm:text-2xl font-black mt-3 tracking-tight ${
          isDark ? 'text-white' : 'text-slate-950'
        }`}
      >
        {lang === 'en' ? 'Diwali Festive Working Capital Loan' : 'दीवाली त्योहारी कार्यशील पूंजी ऋण'}
      </h2>
      <p
        className={`text-xs sm:text-sm mt-1 leading-relaxed ${
          isDark ? 'text-slate-400' : 'text-slate-600'
        }`}
      >
        {lang === 'en'
          ? 'Wholesale festive inventory stock purchases before Diwali rush'
          : 'दिवाली की मांग से पूर्व थोक इन्वेंट्री स्टॉक खरीद हेतु विशेष पूंजी'}
      </p>

      {/* Dark Inner Stat Box */}
      <div
        className={`mt-4 rounded-2xl p-4 sm:p-5 border transition-all ${
          isDark
            ? 'bg-[#060810] border-slate-800/80 shadow-inner'
            : 'bg-[#FAF8F5] border-orange-100 shadow-inner'
        }`}
      >
        {/* Top: Available Loan and Amount */}
        <div className="flex items-baseline justify-between gap-2 pb-3 border-b border-slate-800/80 dark:border-slate-800/80 border-slate-200">
          <span
            className={`text-xs sm:text-sm font-bold ${
              isDark ? 'text-slate-400' : 'text-slate-600'
            }`}
          >
            {lang === 'en' ? 'Available Loan' : 'उपलब्ध ऋण राशि'}
          </span>
          <span className="text-2xl sm:text-4xl font-black text-[#FF7700] tracking-tight font-mono">
            ₹25,000
          </span>
        </div>

        {/* 3-Column Stats Row */}
        <div className="grid grid-cols-3 gap-2 sm:gap-4 pt-3 text-left">
          <div>
            <span
              className={`text-[11px] sm:text-xs font-semibold block ${
                isDark ? 'text-slate-400' : 'text-slate-500'
              }`}
            >
              {lang === 'en' ? 'Monthly EMI' : 'मासिक ईएमआई'}
            </span>
            <span
              className={`text-xs sm:text-base font-black font-mono mt-0.5 block ${
                isDark ? 'text-white' : 'text-slate-900'
              }`}
            >
              ₹2,204
            </span>
          </div>

          <div>
            <span
              className={`text-[11px] sm:text-xs font-semibold block ${
                isDark ? 'text-slate-400' : 'text-slate-500'
              }`}
            >
              {lang === 'en' ? 'Interest Rate' : 'ब्याज दर'}
            </span>
            <span className="text-xs sm:text-base font-black font-mono text-emerald-400 mt-0.5 block">
              10.5% p.a.
            </span>
          </div>

          <div>
            <span
              className={`text-[11px] sm:text-xs font-semibold block ${
                isDark ? 'text-slate-400' : 'text-slate-500'
              }`}
            >
              {lang === 'en' ? 'Hidden Charges' : 'गुप्त शुल्क'}
            </span>
            <span className="text-xs sm:text-base font-black text-emerald-400 mt-0.5 block">
              ₹0 (शून्य)
            </span>
          </div>
        </div>
      </div>

      {/* Bottom Full-Width Action Button */}
      {isLoanDisbursed ? (
        <div className="mt-4 w-full py-3.5 px-4 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-bold text-sm sm:text-base flex items-center justify-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <span>
            {lang === 'en'
              ? '₹25,000 Disbursed to State Bank of India (•••• 4821)'
              : '₹25,000 भारतीय स्टेट बैंक (•••• 4821) में जमा हो चुके हैं'}
          </span>
        </div>
      ) : (
        <button
          type="button"
          onClick={onAcceptLoan}
          className="mt-4 w-full py-3.5 sm:py-4 px-4 rounded-2xl bg-gradient-to-r from-[#FF671F] via-[#F59E0B] to-[#10B981] hover:brightness-110 active:scale-[0.99] transition-all text-slate-950 font-black text-sm sm:text-base shadow-lg hover:shadow-orange-500/20 flex items-center justify-center gap-2.5 cursor-pointer"
        >
          <Fingerprint className="w-5 h-5 text-slate-950 shrink-0" />
          <span>
            {lang === 'en'
              ? 'Accept with 3-Factor Biometric (Instant Credit)'
              : '3-कारक बायोमेट्रिक से स्वीकारें (त्वरित क्रेडिट)'}
          </span>
        </button>
      )}
    </div>
  );
};
