import React from 'react';
import { ActiveTab, Language, ThemeMode } from '../types';
import { translations } from '../data/translations';
import {
  Home,
  Bot,
  ShieldCheck,
  ReceiptText
} from 'lucide-react';

interface MobileBottomNavProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  lang: Language;
  theme: ThemeMode;
}

export const MobileBottomNav: React.FC<MobileBottomNavProps> = ({
  activeTab,
  setActiveTab,
  lang,
  theme,
}) => {
  const t = translations[lang];
  const isDark = theme === 'dark';
  const isTiranga = !isDark;

  return (
    <nav
      className={`sticky bottom-0 z-40 w-full border-t transition-colors select-none ${
        isTiranga
          ? 'bg-white/95 border-[#FF671F]/30 text-slate-800 shadow-lg'
          : 'bg-[#0B0F19]/95 border-slate-800 text-slate-200'
      }`}
    >
      <div className="max-w-md mx-auto px-2 py-1 grid grid-cols-4 items-center justify-items-center">
        {/* Tab 1: Home / Dashboard */}
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`w-full h-12 flex flex-col items-center justify-center rounded-xl transition-all relative ${
            activeTab === 'dashboard'
              ? isTiranga
                ? 'text-[#FF671F] font-bold'
                : isDark
                ? 'text-blue-400 font-bold'
                : 'text-blue-600 font-bold'
              : isDark
              ? 'text-slate-400 hover:text-slate-200'
              : 'text-slate-600 hover:text-slate-950'
          }`}
        >
          <Home className={`w-5 h-5 ${activeTab === 'dashboard' ? 'stroke-[2.5]' : 'stroke-2'}`} />
          <span className="text-[10px] mt-0.5 tracking-tight font-medium">
            {t.navDashboard}
          </span>
          {activeTab === 'dashboard' && (
            <span
              className={`w-1.5 h-1.5 rounded-full mt-0.5 ${
                isTiranga ? 'bg-[#FF671F]' : 'bg-blue-500'
              }`}
            />
          )}
        </button>

        {/* Tab 2: Sakhi Conversational AI Assistant */}
        <div className="w-full flex flex-col items-center justify-center relative -top-2">
          <button
            onClick={() => setActiveTab('sakhi')}
            className={`w-11 h-11 rounded-full p-0.5 shadow-xl transition-transform active:scale-95 flex items-center justify-center ${
              activeTab === 'sakhi'
                ? isTiranga
                  ? 'ring-4 ring-[#FF671F]/40 scale-105 bg-gradient-to-tr from-[#FF671F] to-[#046A38]'
                  : 'ring-4 ring-blue-500/30 scale-105 bg-blue-600'
                : isTiranga
                ? 'hover:scale-105 bg-gradient-to-tr from-[#FF671F] via-[#000080] to-[#046A38]'
                : 'hover:scale-105 bg-gradient-to-tr from-blue-600 to-indigo-600'
            }`}
            title={lang === 'en' ? 'Talk to Sakhi Voice Assistant' : 'सखी वॉइस से बात करें'}
          >
            <div className="w-full h-full rounded-full flex flex-col items-center justify-center text-white">
              <Bot className="w-5 h-5" />
            </div>
          </button>
          <span
            className={`block text-center text-[10px] font-bold mt-0.5 ${
              activeTab === 'sakhi'
                ? isTiranga
                  ? 'text-[#FF671F]'
                  : isDark ? 'text-blue-400' : 'text-blue-600'
                : isDark ? 'text-slate-400' : 'text-slate-600'
            }`}
          >
            {lang === 'en' ? 'Sakhi AI' : 'सखी'}
          </span>
        </div>

        {/* Tab 3: Protection & Safety (Fraud & Stress Intervention) */}
        <button
          onClick={() => setActiveTab('stress-guard')}
          className={`w-full h-12 flex flex-col items-center justify-center rounded-xl transition-all relative ${
            activeTab === 'stress-guard'
              ? isTiranga
                ? 'text-[#046A38] font-bold'
                : isDark
                ? 'text-blue-400 font-bold'
                : 'text-blue-600 font-bold'
              : isDark
              ? 'text-slate-400 hover:text-slate-200'
              : 'text-slate-600 hover:text-slate-950'
          }`}
        >
          <ShieldCheck className={`w-5 h-5 ${activeTab === 'stress-guard' ? 'stroke-[2.5]' : 'stroke-2'}`} />
          <span className="text-[10px] mt-0.5 tracking-tight font-medium">
            {lang === 'en' ? 'Protection' : 'सुरक्षा'}
          </span>
          {activeTab === 'stress-guard' && (
            <span
              className={`w-1.5 h-1.5 rounded-full mt-0.5 ${
                isTiranga ? 'bg-[#046A38]' : 'bg-blue-500'
              }`}
            />
          )}
        </button>

        {/* Tab 4: Transactions */}
        <button
          onClick={() => setActiveTab('passbook')}
          className={`w-full h-12 flex flex-col items-center justify-center rounded-xl transition-all relative ${
            activeTab === 'passbook'
              ? isTiranga
                ? 'text-[#000080] font-bold'
                : isDark
                ? 'text-blue-400 font-bold'
                : 'text-blue-600 font-bold'
              : isDark
              ? 'text-slate-400 hover:text-slate-200'
              : 'text-slate-600 hover:text-slate-950'
          }`}
        >
          <ReceiptText className={`w-5 h-5 ${activeTab === 'passbook' ? 'stroke-[2.5]' : 'stroke-2'}`} />
          <span className="text-[10px] mt-0.5 tracking-tight font-medium">
            {t.navPassbook}
          </span>
          {activeTab === 'passbook' && (
            <span
              className={`w-1.5 h-1.5 rounded-full mt-0.5 ${
                isTiranga ? 'bg-[#000080]' : 'bg-blue-500'
              }`}
            />
          )}
        </button>
      </div>

      {/* Subtle Mobile Gesture Bar with Tricolour Accent in Tiranga mode */}
      <div className="w-full flex justify-center pb-1 pt-0.5">
        <div
          className={`w-28 h-1 rounded-full ${
            isTiranga
              ? 'bg-gradient-to-r from-[#FF671F] via-slate-300 to-[#046A38]'
              : isDark
              ? 'bg-slate-700/60'
              : 'bg-slate-300'
          }`}
        />
      </div>
    </nav>
  );
};
