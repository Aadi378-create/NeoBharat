import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { MobileStatusBar } from './components/MobileStatusBar';
import { MobileBottomNav } from './components/MobileBottomNav';
import { PersonalizedDashboard } from './components/PersonalizedDashboard';
import { SakhiChatWindow } from './components/SakhiChatWindow';
import { EmpatheticStressRadar } from './components/EmpatheticStressRadar';
import { TransactionsList } from './components/TransactionsList';
import { ChakraLogo } from './components/ChakraLogo';
import { TirangaRibbon } from './components/TirangaRibbon';

import { getCustomers, createTransaction } from './services/api';
import { fetchDashboardData, toPersona } from './services/neobharatAdapter';
import { translations } from './data/translations';
import { Language, ThemeMode, ActiveTab, PersonaProfile, FrequentPayee, AccountTransaction } from './types';
import { PaymentModals } from './components/PaymentModals';
import { LoginSignup } from './components/LoginSignup';

import {
  Smartphone,
  Maximize2,
  ShieldCheck,
  ExternalLink,
  Bot
} from 'lucide-react';

export default function App() {
  const [lang, setLang] = useState<Language>('en');
  // Light theme is now the lively Indian Tiranga theme (Saffron, White, Emerald Green, Chakra Navy)
  const [theme, setTheme] = useState<ThemeMode>('light');
  const [activeTab, setActiveTab] = useState<ActiveTab>('dashboard');
  const [deviceFrameMode, setDeviceFrameMode] = useState<'mobile' | 'expanded'>('mobile');

  // Multi-Persona State for demonstrating personalization across demographics
  const [personas, setPersonas] = useState<PersonaProfile[]>([]);
  const [activePersona, setActivePersona] = useState<PersonaProfile | null>(null);
  const [authenticatedCustomerId, setAuthenticatedCustomerId] = useState<number | null>(null);
  
  const [isLoadingData, setIsLoadingData] = useState(false);
  const [dataError, setDataError] = useState<string | null>(null);
  // Payment & Banking Interactive Modals State
  const [showSendModal, setShowSendModal] = useState(false);
  const [showReceiveModal, setShowReceiveModal] = useState(false);
  const [showScanModal, setShowScanModal] = useState(false);
  const [showBillsModal, setShowBillsModal] = useState(false);
  const [showScamModal, setShowScamModal] = useState(false);
  const [showLoanModal, setShowLoanModal] = useState(false);
  const [showInstallModal, setShowInstallModal] = useState(false);
  const [showVerifyModal, setShowVerifyModal] = useState(false);
  const [showDpdpModal, setShowDpdpModal] = useState(false);
  const [selectedPayee, setSelectedPayee] = useState<FrequentPayee | null>(null);
  const [isLoanDisbursed, setIsLoanDisbursed] = useState(false);

  // Financial Distress Simulator state across the app
  const [isStressActive, setIsStressActive] = useState(false);

  // Sakhi prompt handler when navigating from dashboard
  const [sakhiPrompt, setSakhiPrompt] = useState<string | undefined>(undefined);

  const t = translations[lang];
  const isDark = theme === 'dark';
  // Light theme is intrinsically the authentic Tiranga theme
  const isTiranga = !isDark;

  // Real-time balance and transaction synchronization handlers
  const loadCustomerData = async (customerId: number) => {
    setIsLoadingData(true);
    setDataError(null);
    try {
      const p = toPersona(await fetchDashboardData(customerId));
      setActivePersona(p);
      setPersonas([p]); // For now, the user only sees themselves
    } catch (error) {
      setDataError(error instanceof Error ? error.message : 'Unable to load NeoBharat data.');
      setAuthenticatedCustomerId(null);
    } finally {
      setIsLoadingData(false);
    }
  };

  useEffect(() => {
    if (authenticatedCustomerId !== null) {
      void loadCustomerData(authenticatedCustomerId);
    } else {
      setActivePersona(null);
      setPersonas([]);
    }
  }, [authenticatedCustomerId]);

  const refreshActivePersona = async () => {
    if (!activePersona) return;
    const fresh = toPersona(await fetchDashboardData(activePersona.id));
    setPersonas([fresh]);
    setActivePersona(fresh);
  };

  const handleBalanceUpdate = (newBalance: number) => {
    setActivePersona((prev) => prev ? ({
      ...prev,
      accountBalance: newBalance
    }) : prev);
  };

  const handleAddTransaction = (newTx: AccountTransaction) => {
    setActivePersona((prev) => prev ? ({
      ...prev,
      recentTransactions: [newTx, ...prev.recentTransactions]
    }) : prev);
  };

  const handleSelectPayee = (payee: FrequentPayee) => {
    setSelectedPayee(payee);
    setShowSendModal(true);
  };

  const handleTriggerScamTest = (payee: FrequentPayee) => {
    setSelectedPayee(payee);
    setShowScamModal(true);
  };

  // Apply dark / light (Tiranga) class to root document element and body
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      document.body.style.backgroundColor = '#070A10';
      document.body.style.color = '#F8FAFC';
    } else {
      document.documentElement.classList.remove('dark');
      document.body.style.backgroundColor = '#FAF8F5';
      document.body.style.color = '#0F172A';
    }
  }, [theme]);

  // Navigate to Sakhi Voice assistant with context
  const handleNavigateToSakhi = (promptText?: string) => {
    if (promptText) {
      setSakhiPrompt(promptText);
    }
    setActiveTab('sakhi');
  };

  const handleLogout = () => {
    setAuthenticatedCustomerId(null);
    setActiveTab('dashboard');
  };

  return (
    <div
      className={`h-screen overflow-hidden transition-colors duration-200 flex flex-col font-sans ${
        isDark
          ? 'bg-[#070A10] text-slate-100'
          : 'bg-[#FAF8F5] text-slate-900'
      }`}
    >
      {/* Top Banner & Viewport Switcher */}
      <aside
        aria-label="Theme Header Bar"
        className={`w-full min-h-[44px] border-b px-3 sm:px-4 py-1.5 text-xs flex items-center justify-between gap-3 ${
          isDark
            ? 'bg-[#0B0F19] border-slate-800 text-slate-300'
            : 'bg-white border-[#FF671F]/30 text-slate-800 shadow-sm'
        }`}
      >
        {/* Left: App Title, Indian Flag Theme Indicator, and Direct RBI Framework URL */}
        <div className="flex items-center gap-2 flex-wrap min-w-0">
          <ChakraLogo size={18} animate={isTiranga} />
          <span
            className={`font-black uppercase tracking-wider text-[11px] flex items-center shrink-0 ${
              isTiranga
                ? 'text-slate-950'
                : isDark ? 'text-blue-400' : 'text-blue-700'
            }`}
          >
            <span className="text-[#FF671F]">NEO</span>
            <span className="text-[#00A86B]">BHARAT</span>
          </span>

          {/* Tiranga Flag Theme Active Badge */}
          {isTiranga && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10.5px] font-bold bg-gradient-to-r from-[#FF671F]/15 via-white to-[#046A38]/15 border border-[#FF671F]/40 text-slate-800 shrink-0">
              <span className="leading-none">🇮🇳</span>
              <span className="text-[#FF671F]">Saffron</span>
              <span className="text-slate-400">·</span>
              <span className="text-slate-800">White</span>
              <span className="text-slate-400">·</span>
              <span className="text-[#046A38]">Green</span>
            </span>
          )}

          <a
            href={t.rbiDirectUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10.5px] font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-700 dark:text-emerald-400 hover:underline shrink-0"
            title="Official RBI Regulatory Directives"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-[#046A38] shrink-0" />
            <span>{t.rbiDirectLinkText}</span>
            <ExternalLink className="w-2.5 h-2.5 ml-0.5 shrink-0 opacity-70" />
          </a>
        </div>

        {/* Right: Viewport Mode Switcher (Phone Frame vs Expanded View) */}
        <div className="flex items-center gap-2 shrink-0">
          <span
            className={`text-[11px] hidden sm:inline font-medium ${
              isDark ? 'text-slate-400' : 'text-slate-500'
            }`}
          >
            Layout:
          </span>
          <div
            className={`h-8 flex items-center rounded-xl p-0.5 border shrink-0 ${
              isDark
                ? 'border-slate-700 bg-slate-900/60'
                : 'border-slate-300 bg-slate-100'
            }`}
          >
            <button
              onClick={() => setDeviceFrameMode('mobile')}
              className={`min-w-[80px] h-7 px-2.5 rounded-lg text-xs font-bold inline-flex items-center justify-center gap-1.5 transition-colors ${
                deviceFrameMode === 'mobile'
                  ? isTiranga
                    ? 'bg-gradient-to-r from-[#FF671F] to-[#E65100] text-white shadow-sm'
                    : 'bg-blue-600 text-white shadow-sm'
                  : isDark
                  ? 'text-slate-400 hover:text-white'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              title="Mobile Device Frame"
            >
              <Smartphone className="w-3.5 h-3.5 shrink-0" />
              <span>Mobile</span>
            </button>

            <button
              onClick={() => setDeviceFrameMode('expanded')}
              className={`min-w-[80px] h-7 px-2.5 rounded-lg text-xs font-bold inline-flex items-center justify-center gap-1.5 transition-colors ${
                deviceFrameMode === 'expanded'
                  ? isTiranga
                    ? 'bg-gradient-to-r from-[#FF671F] to-[#E65100] text-white shadow-sm'
                    : 'bg-blue-600 text-white shadow-sm'
                  : isDark
                  ? 'text-slate-400 hover:text-white'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              title="Expanded Window"
            >
              <Maximize2 className="w-3.5 h-3.5 shrink-0" />
              <span>Expanded</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Canvas */}
      <main className="flex-1 w-full flex items-center justify-center p-0 sm:p-4 md:p-6 overflow-hidden">
        <div
          className={`w-full h-full transition-all duration-300 flex flex-col ${
            deviceFrameMode === 'mobile'
              ? isDark
                ? 'max-w-[390px] rounded-none sm:rounded-[36px] sm:border-[5px] sm:border-slate-800 sm:shadow-2xl overflow-hidden bg-[#0B0F19]'
                : 'max-w-[390px] rounded-none sm:rounded-[36px] sm:border-[5px] sm:border-[#FF671F]/40 sm:shadow-2xl overflow-hidden bg-[#FAF8F5]'
              : isDark
              ? 'max-w-4xl rounded-2xl border border-slate-800 shadow-xl overflow-hidden bg-[#0B0F19]'
              : 'max-w-4xl rounded-2xl border border-[#FF671F]/30 shadow-xl overflow-hidden bg-[#FAF8F5]'
          }`}
          style={{
            maxHeight: deviceFrameMode === 'mobile' ? '844px' : '900px',
          }}
        >
          {/* Authentic Mobile Status Bar */}
          <MobileStatusBar theme={theme} />

          {/* Clean App Navbar with Ashoka Chakra, Profile Name, Language & Tiranga (Light) / Dark Theme Toggles */}
          {!authenticatedCustomerId ? (
            <LoginSignup 
              onLoginSuccess={setAuthenticatedCustomerId} 
              lang={lang} 
              theme={theme} 
            />
          ) : isLoadingData ? (
            <div className="flex-1 flex flex-col items-center justify-center min-h-[500px]">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
              <p className="text-gray-500">Loading NeoBharat Secure Banking...</p>
            </div>
          ) : dataError ? (
            <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
              <div className="bg-red-50 text-red-600 p-4 rounded-xl">
                <p className="font-medium">Connection Error</p>
                <p className="text-sm mt-1">{dataError}</p>
              </div>
              <button 
                onClick={() => loadCustomerData(authenticatedCustomerId!)}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg"
              >
                Retry Connection
              </button>
            </div>
          ) : !activePersona ? (
            <div className="flex-1 flex items-center justify-center">
              <p>No customer profiles found.</p>
            </div>
          ) : (
            <>
              <Navbar
                lang={lang}
                setLang={setLang}
                theme={theme}
                setTheme={setTheme}
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                activePersona={activePersona}
              />

              {/* RBI Regulatory Transparency Advisory Strip */}
          <div
            className={`py-1.5 px-3 border-b text-[11px] flex items-center justify-between ${
              isDark
                ? 'bg-slate-950 border-slate-800 text-slate-300'
                : 'bg-orange-50/70 border-orange-200/80 text-orange-950'
            }`}
          >
            <div className="flex items-center gap-1.5 truncate">
              <span className="w-1.5 h-1.5 rounded-full bg-[#046A38] shrink-0" />
              <span
                className={`font-bold shrink-0 ${
                  isTiranga
                    ? 'text-[#FF671F]'
                    : isDark ? 'text-blue-400' : 'text-blue-700'
                }`}
              >
                {lang === 'en' ? 'RBI Guideline:' : 'आरबीआई नियम:'}
              </span>
              <span className="truncate">
                {lang === 'en'
                  ? 'All credit products include 100% upfront Key Facts Statements (KFS). Zero hidden charges.'
                  : 'सभी डिजिटल ऋणों पर 100% पारदर्शी मुख्य तथ्य विवरण (KFS) उपलब्ध।'}
              </span>
            </div>
            <a
              href={t.rbiDirectUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[10px] font-bold text-[#046A38] hover:underline flex items-center gap-0.5 shrink-0 ml-2"
            >
              <span>rbi.org.in</span>
              <ExternalLink className="w-2.5 h-2.5" />
            </a>
          </div>

          {/* Scrollable Main Window Content */}
          <div className="flex-1 p-3.5 sm:p-4 overflow-y-auto">
            {/* Window 1: Hyper-Personalized Banking Dashboard (Pillar 1) */}
            {activeTab === 'dashboard' && (
              <PersonalizedDashboard
                activePersona={activePersona}
                onSelectPersona={setActivePersona}
                lang={lang}
                theme={theme}
                onNavigateToSakhi={handleNavigateToSakhi}
                isStressActive={isStressActive}
                onSendMoney={() => {
                  setSelectedPayee(null);
                  setShowSendModal(true);
                }}
                onScanQr={() => setShowScanModal(true)}
                onReceiveMoney={() => setShowReceiveModal(true)}
                onBillsUtilities={() => setShowBillsModal(true)}
                onSelectPayee={handleSelectPayee}
                onTriggerScamTest={handleTriggerScamTest}
                onAcceptLoan={() => setShowLoanModal(true)}
                onVerifyClick={() => setShowVerifyModal(true)}
                onDpdpClick={() => setShowDpdpModal(true)}
                isLoanDisbursed={isLoanDisbursed}
              />
            )}

            {/* Window 2: Sakhi Conversational Voice & Chat Banking (Pillar 2) */}
            {activeTab === 'sakhi' && (
              <SakhiChatWindow
                activePersona={activePersona}
                lang={lang}
                theme={theme}
                initialPrompt={sakhiPrompt}
                onClearInitialPrompt={() => setSakhiPrompt(undefined)}
              />
            )}

            {/* Window 3: Protection & Safety / Empathetic Hardship Radar (Pillar 3) */}
            {activeTab === 'stress-guard' && (
              <EmpatheticStressRadar
                activePersona={activePersona}
                lang={lang}
                theme={theme}
                isStressActive={isStressActive}
                setIsStressActive={setIsStressActive}
              />
            )}

            {/* Window 4: Account Transactions & Cashflow */}
            {activeTab === 'passbook' && (
              <TransactionsList
                activePersona={activePersona}
                lang={lang}
                theme={theme}
              />
            )}
          </div>

          {/* Mobile Bottom Navigation Bar (Home, Sakhi AI, Protection, Transactions) */}
          <MobileBottomNav
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            lang={lang}
            theme={theme}
          />

          {/* Interactive Payment, Receive, Scan, BillPay, & Scam Shield Modals */}
          <PaymentModals
            activePersona={activePersona}
            lang={lang}
            theme={theme}
            showSendModal={showSendModal}
            setShowSendModal={setShowSendModal}
            showReceiveModal={showReceiveModal}
            setShowReceiveModal={setShowReceiveModal}
            showScanModal={showScanModal}
            setShowScanModal={setShowScanModal}
            showBillsModal={showBillsModal}
            setShowBillsModal={setShowBillsModal}
            showScamModal={showScamModal}
            setShowScamModal={setShowScamModal}
            showLoanModal={showLoanModal}
            setShowLoanModal={setShowLoanModal}
            showInstallModal={showInstallModal}
            setShowInstallModal={setShowInstallModal}
            showVerifyModal={showVerifyModal}
            setShowVerifyModal={setShowVerifyModal}
            showDpdpModal={showDpdpModal}
            setShowDpdpModal={setShowDpdpModal}
            selectedPayee={selectedPayee}
            setSelectedPayee={setSelectedPayee}
            onBalanceUpdate={handleBalanceUpdate}
            onAddTransaction={handleAddTransaction}
            onLoanDisbursedSuccess={() => setIsLoanDisbursed(true)}
            refreshCustomerData={refreshActivePersona}
          />
          </>
          )}
        </div>
      </main>

      {/* Production Footer with Tiranga Tricolour and Direct RBI Official Links */}
      <footer
        className={`border-t py-3.5 text-center text-xs transition-colors ${
          isDark
            ? 'bg-[#070A10] border-slate-800 text-slate-400'
            : 'bg-white border-[#FF671F]/30 text-slate-700'
        }`}
      >
        <div className="max-w-4xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <ChakraLogo size={16} animate={false} />
            <span className="font-bold tracking-tight">
              <span className="text-[#FF671F]">NEO</span>
              <span className="text-[#00A86B]">BHARAT</span>
            </span>
            <span>·</span>
            <span>AI-Powered Digital Banking</span>
          </div>

          <div className="flex items-center gap-3 text-[11px] flex-wrap justify-center">
            <a
              href="https://www.rbi.org.in"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#046A38] font-semibold hover:underline inline-flex items-center gap-1"
            >
              <span>Reserve Bank of India (RBI Direct)</span>
              <ExternalLink className="w-2.5 h-2.5" />
            </a>
            <span>•</span>
            <a
              href="https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=54187"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 dark:text-blue-400 font-semibold hover:underline inline-flex items-center gap-1"
            >
              <span>RBI Digital Lending Framework</span>
              <ExternalLink className="w-2.5 h-2.5" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
