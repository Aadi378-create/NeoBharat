import React from 'react';
import { ChakraLogo } from './ChakraLogo';
import { TirangaRibbon } from './TirangaRibbon';
import { Language, ThemeMode, ActiveTab, PersonaProfile } from '../types';
import { translations } from '../data/translations';
import {
  Sun,
  Moon,
  Languages,
  Sparkles,
  Smartphone,
  Building2,
  CheckCircle2
} from 'lucide-react';

interface NavbarProps {
  lang: Language;
  setLang: (l: Language) => void;
  theme: ThemeMode;
  setTheme: (t: ThemeMode) => void;
  activeTab: ActiveTab;
  setActiveTab: (t: ActiveTab) => void;
  activePersona: PersonaProfile;
}

export const Navbar: React.FC<NavbarProps> = ({
  lang,
  setLang,
  theme,
  setTheme,
  activeTab,
  setActiveTab,
  activePersona,
}) => {
  const t = translations[lang];
  const isDark = theme === 'dark';
  const isTiranga = !isDark;

  return (
    <header className="sticky top-0 z-40 w-full select-none">
      {/* Main Header Bar matching Image 1 */}
      <div
        className={`border-b transition-colors duration-200 w-full ${
          isTiranga
            ? 'bg-gradient-to-r from-[#FFF5EB] via-white to-[#F0FDF4] border-[#FF671F]/30 text-slate-900 shadow-sm'
            : 'bg-[#0B0F19]/95 border-slate-800 text-slate-100 shadow-md backdrop-blur-md'
        }`}
      >
        <div className="px-2 sm:px-4 py-2 flex items-center w-full max-w-full">
          {/* Left: Brand Identity & Govt Platform Subtitle */}
          <div
            className="flex items-center gap-1.5 sm:gap-2 cursor-pointer shrink min-w-0 group"
            onClick={() => setActiveTab('dashboard')}
          >
            {/* Ashoka Chakra icon with circular ring */}
            <div
              className={`w-7 h-7 sm:w-9 sm:h-9 rounded-full flex items-center justify-center border shrink-0 transition-transform group-hover:scale-105 ${
                isDark
                  ? 'bg-[#060A14] border-amber-500/50 shadow-md shadow-amber-500/10'
                  : 'bg-orange-50 border-[#FF671F] shadow-sm'
              }`}
            >
              <ChakraLogo size={20} animate={true} />
            </div>

            <div className="flex flex-col min-w-0 shrink">
              <span className="text-sm sm:text-lg font-black tracking-tight flex items-center whitespace-nowrap select-none truncate">
                <span className="text-[#FF671F]">NEO</span>
                <span className="text-[#00A86B]">BHARAT</span>
              </span>
              <p
                className={`text-[9px] sm:text-[11px] font-medium leading-tight truncate ${
                  isDark ? 'text-slate-400' : 'text-slate-600'
                }`}
              >
                <span>Govt × RBI Platform</span>
              </p>
            </div>
          </div>

          {/* Flexible Spacer to push controls right and prevent overlap */}
          <div className="flex-1 min-w-[4px] sm:min-w-[8px]"></div>

          {/* Right: Header Controls - Guaranteed fully visible */}
          <div className="flex items-center justify-end gap-1 sm:gap-2 shrink-0">
            {/* SAKHI Vibrant Gradient Button */}
            <button
              onClick={() => setActiveTab('sakhi')}
              className={`h-8 sm:h-9 px-2 sm:px-3 rounded-xl text-xs font-black shrink-0 transition-all hover:scale-105 active:scale-95 inline-flex items-center justify-center gap-1 sm:gap-1.5 shadow-md ${
                activeTab === 'sakhi'
                  ? 'bg-gradient-to-r from-pink-600 to-rose-600 text-white ring-2 ring-pink-400 shadow-pink-500/30'
                  : 'bg-gradient-to-r from-purple-600 via-pink-600 to-rose-500 text-white shadow-purple-500/20 hover:brightness-110'
              }`}
              title="Open Sakhi AI Assistant"
            >
              <Sparkles className="w-3.5 h-3.5 text-yellow-300 shrink-0" />
              <span className="whitespace-nowrap flex items-center h-full pt-[2px]">
                सखी (SAKHI)
              </span>
            </button>

            {/* Language Switcher */}
            <button
              onClick={() => setLang(lang === 'en' ? 'hi' : 'en')}
              className={`h-8 sm:h-9 px-2 sm:px-2.5 rounded-xl text-xs font-bold border transition-colors inline-flex items-center justify-center gap-1 shrink-0 ${
                isTiranga
                  ? 'bg-white border-[#FF671F]/40 text-slate-800 hover:border-[#FF671F] shadow-sm'
                  : 'bg-slate-900 border-slate-700 text-slate-200 hover:border-blue-500'
              }`}
              title={lang === 'en' ? 'Switch to Hindi' : 'Switch to English'}
            >
              <Languages className="w-3.5 h-3.5 text-[#FF671F] shrink-0" />
              <span className="font-bold pt-[2px]">{lang === 'en' ? 'हिन्दी' : 'EN'}</span>
            </button>

            {/* Clean Theme Toggle Button (Sun / Moon) - Always clearly visible and prominent */}
            <button
              onClick={() => setTheme(isDark ? 'light' : 'dark')}
              className={`h-8 sm:h-9 w-8 sm:w-9 rounded-xl border transition-all inline-flex items-center justify-center shrink-0 ${
                isTiranga
                  ? 'bg-white border-slate-300 text-slate-800 hover:border-amber-500 shadow-sm hover:scale-105'
                  : 'bg-slate-900 border-slate-700 text-amber-400 hover:border-amber-400 hover:scale-105'
              }`}
              title={isDark ? 'Switch to Light Theme' : 'Switch to Dark Mode'}
              aria-label="Toggle dark/light theme"
            >
              {isDark ? (
                <Sun className="w-4 h-4 text-amber-400 shrink-0" />
              ) : (
                <Moon className="w-4 h-4 text-indigo-600 shrink-0" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Authentic Indian Flag Tricolour Ribbon (Saffron, White, India Green) underneath header */}
      <TirangaRibbon height={4} />
    </header>
  );
};
