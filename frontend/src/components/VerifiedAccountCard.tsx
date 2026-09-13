import React from 'react';
import { PersonaProfile, Language, ThemeMode } from '../types';
import { ChakraLogo } from './ChakraLogo';
import { Smartphone, ShieldCheck, CheckCircle2, Building2 } from 'lucide-react';

interface VerifiedAccountCardProps {
  activePersona: PersonaProfile;
  lang: Language;
  theme: ThemeMode;
  onInstallClick?: () => void;
  onVerifyClick: () => void;
  onDpdpClick: () => void;
  onLogout: () => void;
}

export const VerifiedAccountCard: React.FC<VerifiedAccountCardProps> = ({
  activePersona,
  lang,
  theme,
  onVerifyClick,
  onDpdpClick,
  onLogout,
}) => {
  const isDark = theme === 'dark';
  const isTiranga = !isDark;

  const phone = activePersona.phone || '+91 98350 44102';
  const bank = activePersona.bankName || 'State Bank of India';

  return (
    <div
      className={`w-full rounded-2xl sm:rounded-3xl border transition-all p-3.5 sm:p-4 shadow-xl ${
        isDark
          ? 'bg-[#0B1020] border-slate-800/80 text-slate-100 shadow-black/40'
          : 'bg-white border-[#FF671F]/30 text-slate-900 shadow-orange-500/5'
      }`}
    >
      <div className="flex flex-col gap-3 sm:gap-4 w-full">
        {/* Top: Ashoka Chakra badge + Account details */}
        <div className="flex flex-row items-start gap-3 sm:gap-4 w-full">
          {/* Circular Ashoka Chakra badge */}
          <div
            className={`w-12 h-12 rounded-full flex items-center justify-center shrink-0 border-2 mt-0.5 ${
              isDark
                ? 'bg-[#060A14] border-amber-500/60 shadow-lg shadow-amber-500/10'
                : 'bg-orange-50 border-[#FF671F] shadow-md shadow-orange-500/20'
            }`}
          >
            <ChakraLogo size={28} animate={true} />
          </div>

          <div className="flex flex-col flex-1 min-w-0 gap-1.5">
            {/* Top row: Badge Title */}
            <span className="text-sm font-black tracking-wider text-[#FF671F] uppercase leading-tight break-words">
              {lang === 'en' ? 'VERIFIED CITIZEN BANKING ACCOUNT' : 'सत्यापित नागरिक बैंकिंग खाता'}
            </span>

            {/* Bottom row: Name, Phone & Bank info */}
            <div
              className={`text-sm font-bold flex flex-wrap items-center gap-x-2 gap-y-1 ${
                isDark ? 'text-slate-200' : 'text-slate-800'
              }`}
            >
              <span className="font-extrabold text-slate-900 dark:text-white">
                {lang === 'en' ? activePersona.name : activePersona.hindiName}
              </span>
              <span className="text-slate-400 hidden sm:inline">•</span>
              <span className="font-mono text-slate-700 dark:text-slate-300">
                {phone}
              </span>
              <span className="text-slate-400 hidden sm:inline">•</span>
              <span className="flex items-center gap-1 text-slate-700 dark:text-slate-300">
                <Building2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span className="truncate">
                  {bank} ({activePersona.accountNumber})
                </span>
              </span>
            </div>
          </div>
        </div>

        {/* Bottom action buttons: Verify Phone & Bank, DPDP Consent */}
        <div className="flex items-center gap-2 flex-wrap w-full">
          <button
            onClick={onVerifyClick}
            className={`px-3 py-2 flex-1 sm:flex-none justify-center rounded-xl text-xs font-bold border inline-flex items-center gap-1.5 transition-all hover:scale-105 active:scale-95 ${
              isDark
                ? 'bg-amber-950/40 border-amber-500/50 text-amber-300 hover:bg-amber-900/50'
                : 'bg-amber-50 border-amber-500 text-amber-800 hover:bg-amber-100'
            }`}
            title="Verify Phone & Bank NPCI Linkage"
          >
            <Smartphone className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span>{lang === 'en' ? 'Verify Phone & Bank' : 'फ़ोन व बैंक सत्यापन'}</span>
          </button>

          <button
            onClick={onDpdpClick}
            className={`px-3 py-2 flex-1 sm:flex-none justify-center rounded-xl text-xs font-bold border inline-flex items-center gap-1.5 transition-all hover:scale-105 active:scale-95 ${
              isDark
                ? 'bg-slate-800/80 border-slate-700 text-slate-200 hover:bg-slate-700'
                : 'bg-slate-100 border-slate-300 text-slate-700 hover:bg-slate-200'
            }`}
            title="Digital Personal Data Protection Consent Manager"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-blue-400 shrink-0" />
            <span>{lang === 'en' ? 'DPDP Consent' : 'डीपीडीपी सहमति'}</span>
          </button>
          
          <button
            onClick={onLogout}
            className={`px-3 py-2 flex-1 sm:flex-none justify-center rounded-xl text-xs font-bold border inline-flex items-center gap-1.5 transition-all hover:scale-105 active:scale-95 ${
              isDark
                ? 'bg-red-950/40 border-red-900/50 text-red-400 hover:bg-red-900/50'
                : 'bg-red-50 border-red-200 text-red-600 hover:bg-red-100'
            }`}
            title="Secure Logout"
          >
            <span>{lang === 'en' ? 'Logout' : 'लॉग आउट'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
