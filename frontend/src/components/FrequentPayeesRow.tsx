import React from 'react';
import { FrequentPayee, Language, ThemeMode } from '../types';
import { ShieldCheck, AlertTriangle } from 'lucide-react';

interface FrequentPayeesRowProps {
  payees: FrequentPayee[];
  lang: Language;
  theme: ThemeMode;
  onSelectPayee: (payee: FrequentPayee) => void;
  onTriggerScamTest: (payee: FrequentPayee) => void;
}

export const FrequentPayeesRow: React.FC<FrequentPayeesRowProps> = ({
  payees,
  lang,
  theme,
  onSelectPayee,
  onTriggerScamTest,
}) => {
  const isDark = theme === 'dark';

  return (
    <div className="w-full space-y-2.5 select-none">
      {/* Section Header */}
      <div className="flex items-center justify-between px-1">
        <h3
          className={`text-xs sm:text-sm font-black tracking-wider uppercase flex items-center gap-1.5 ${
            isDark ? 'text-slate-100' : 'text-slate-900'
          }`}
        >
          <span>{lang === 'en' ? 'FREQUENT PAYEES (1-TAP TRANSFER)' : 'नियमित लाभार्थी (1-टैप भुगतान)'}</span>
        </h3>

        <div className="flex items-center gap-1 text-[11px] font-bold text-emerald-400">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>{lang === 'en' ? 'Verified VPA' : 'सत्यापित वीपीए'}</span>
        </div>
      </div>

      {/* Payee items container (uncongested 3 per row) */}
      <div className="grid grid-cols-3 gap-2.5 sm:gap-3">
        {payees.map((payee) => {
          const isScam = payee.isScam;

          return (
            <button
              key={payee.id}
              type="button"
              onClick={() => {
                if (isScam) {
                  onTriggerScamTest(payee);
                } else {
                  onSelectPayee(payee);
                }
              }}
              className={`group p-2.5 sm:p-3 rounded-2xl border text-center flex flex-col items-center justify-between transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer relative overflow-hidden ${
                isScam
                  ? isDark
                    ? 'bg-[#0F1424] border-amber-500/50 hover:border-amber-400 shadow-md shadow-amber-500/10'
                    : 'bg-amber-50/80 border-amber-400 hover:border-amber-500 shadow-md'
                  : isDark
                  ? 'bg-[#0B1222] border-slate-800 hover:border-slate-700 hover:bg-[#10182C] shadow-sm'
                  : 'bg-white border-slate-200 hover:border-orange-300 hover:bg-orange-50/40 shadow-sm'
              }`}
              title={payee.name}
            >
              {/* Emoji / Icon circular avatar */}
              <div
                className={`w-10 h-10 sm:w-11 sm:h-11 rounded-2xl flex items-center justify-center text-lg sm:text-xl mb-1.5 transition-transform group-hover:scale-110 ${
                  isScam
                    ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                    : isDark
                    ? 'bg-[#060A14] border border-slate-800'
                    : 'bg-slate-100 border border-slate-200'
                }`}
              >
                {isScam ? (
                  <AlertTriangle className="w-5 h-5 text-amber-400 animate-bounce" />
                ) : (
                  <span>{payee.emoji}</span>
                )}
              </div>

              {/* Short name */}
              <span
                className={`text-xs sm:text-xs font-black tracking-tight truncate w-full block ${
                  isScam
                    ? 'text-amber-300 dark:text-amber-300'
                    : isDark
                    ? 'text-white'
                    : 'text-slate-900'
                }`}
              >
                {payee.shortName}
              </span>

              {/* Category */}
              <span
                className={`text-[10px] font-medium mt-0.5 truncate w-full block ${
                  isScam
                    ? 'text-amber-400 font-bold flex items-center justify-center gap-0.5'
                    : isDark
                    ? 'text-slate-400'
                    : 'text-slate-500'
                }`}
              >
                {isScam ? (
                  <>
                    <span>⚠️</span>
                    <span>Test Scam</span>
                  </>
                ) : (
                  payee.category
                )}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
