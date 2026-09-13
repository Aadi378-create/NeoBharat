import React, { useState, useEffect } from 'react';
import { PersonaProfile, FrequentPayee, Language, ThemeMode, AccountTransaction } from '../types';
import { ChakraLogo } from './ChakraLogo';
import {
  X,
  Send,
  Download,
  QrCode,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Fingerprint,
  Smartphone,
  ShieldCheck,
  Copy,
  Check,
  Share2,
  RefreshCw,
  Building2,
  ArrowDownLeft,
  ArrowUpRight,
  ShieldAlert,
  Flame,
  Car
} from 'lucide-react';

interface PaymentModalsProps {
  activePersona: PersonaProfile;
  lang: Language;
  theme: ThemeMode;
  // Modal states
  showSendModal: boolean;
  setShowSendModal: (v: boolean) => void;
  showReceiveModal: boolean;
  setShowReceiveModal: (v: boolean) => void;
  showScanModal: boolean;
  setShowScanModal: (v: boolean) => void;
  showBillsModal: boolean;
  setShowBillsModal: (v: boolean) => void;
  showScamModal: boolean;
  setShowScamModal: (v: boolean) => void;
  showLoanModal: boolean;
  setShowLoanModal: (v: boolean) => void;
  showInstallModal: boolean;
  setShowInstallModal: (v: boolean) => void;
  showVerifyModal: boolean;
  setShowVerifyModal: (v: boolean) => void;
  showDpdpModal: boolean;
  setShowDpdpModal: (v: boolean) => void;

  selectedPayee: FrequentPayee | null;
  setSelectedPayee: (payee: FrequentPayee | null) => void;

  // Actions that mutate state
  onBalanceUpdate: (newBalance: number) => void;
  onAddTransaction: (newTx: AccountTransaction) => void;
  onLoanDisbursedSuccess: () => void;
  refreshCustomerData?: () => Promise<void>;
}

export const PaymentModals: React.FC<PaymentModalsProps> = ({
  activePersona,
  lang,
  theme,
  showSendModal,
  setShowSendModal,
  showReceiveModal,
  setShowReceiveModal,
  showScanModal,
  setShowScanModal,
  showBillsModal,
  setShowBillsModal,
  showScamModal,
  setShowScamModal,
  showLoanModal,
  setShowLoanModal,
  showInstallModal,
  setShowInstallModal,
  showVerifyModal,
  setShowVerifyModal,
  showDpdpModal,
  setShowDpdpModal,
  selectedPayee,
  setSelectedPayee,
  onBalanceUpdate,
  onAddTransaction,
  onLoanDisbursedSuccess,
  refreshCustomerData,
}) => {
  const isDark = theme === 'dark';

  // --- SEND MONEY STATE ---
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount] = useState('850');
  const [note, setNote] = useState('Wholesale supplies');
  const [isProcessingSend, setIsProcessingSend] = useState(false);
  const [sendSuccess, setSendSuccess] = useState<null | {
    utr: string;
    amount: number;
    recipientName: string;
    date: string;
  }>(null);

  // Sync recipient with selected payee
  useEffect(() => {
    if (selectedPayee) {
      setRecipient(`${selectedPayee.name} (${selectedPayee.vpa})`);
      if (selectedPayee.defaultAmount) {
        setAmount(selectedPayee.defaultAmount.toString());
      }
    }
  }, [selectedPayee]);

  const handleSendPayment = async () => {
    const numAmount = parseFloat(amount) || 0;
    if (numAmount <= 0) return;

    setIsProcessingSend(true);

    try {
      const payeeName = selectedPayee ? selectedPayee.name : (recipient || 'Merchant Payee');
      
      const payload = {
        amount: numAmount,
        type: 'DEBIT',
        merchant: payeeName,
        category: 'SHOPPING',
        status: 'SUCCESS',
        title: `Paid to ${payeeName}`,
        description: note || 'Instant Payment'
      };
      
      const { createTransaction } = await import('../services/api');
      await createTransaction(activePersona.id, payload);
      
      if (refreshCustomerData) {
        await refreshCustomerData();
      }

      const utrNumber = `UPI/${Math.floor(100000000000 + Math.random() * 900000000000)}`;
      const now = new Date();
      const timeStr = `Today, ${now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}`;

      setSendSuccess({
        utr: utrNumber,
        amount: numAmount,
        recipientName: payeeName,
        date: timeStr,
      });
    } catch (error) {
      console.error('Send payment failed:', error);
      alert('Transaction failed: ' + (error instanceof Error ? error.message : 'Unknown error'));

    } finally {
      setIsProcessingSend(false);
    }
  };

  // --- RECEIVE MONEY STATE ---
  const [receiveAmount, setReceiveAmount] = useState('');
  const [copiedVpa, setCopiedVpa] = useState(false);
  const [receivedToast, setReceivedToast] = useState<null | {
    amount: number;
    sender: string;
  }>(null);

  const handleCopyVpa = () => {
    navigator.clipboard?.writeText(activePersona.upiId || 'rameshkumar@sbi');
    setCopiedVpa(true);
    setTimeout(() => setCopiedVpa(false), 2000);
  };

  const handleSimulateCustomerPayment = async (customAmt?: number) => {
    const amt = customAmt || parseFloat(receiveAmount) || 1200;
    const senders = ['Anand Verma (Kirana Customer)', 'Pooja Sharma (Retail Buyer)', 'Amitabh Roy (UPI 2.0 Auto)'];
    const randomSender = senders[Math.floor(Math.random() * senders.length)];

    try {
      const payload = {
        amount: amt,
        type: 'CREDIT',
        merchant: randomSender,
        category: 'OTHER',
        status: 'SUCCESS',
        title: `Received from ${randomSender}`,
      };
      
      const { createTransaction } = await import('../services/api');
      await createTransaction(activePersona.id, payload);

      if (refreshCustomerData) {
        await refreshCustomerData();
      }

      const now = new Date();
      const timeStr = `Today, ${now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}`;
      setReceivedToast({ amount: amt, sender: randomSender });
      setTimeout(() => setReceivedToast(null), 5000);
    } catch (error) {
      console.error('Receive payment failed:', error);
      alert('Simulation failed: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  // --- LOAN DISBURSAL STATE ---
  const [loanStep, setLoanStep] = useState<'review' | 'biometric' | 'disbursed'>('review');

  const handleDisburseLoan = () => {
    setLoanStep('biometric');
    setTimeout(async () => {
      try {
        const payload = {
          amount: 25000,
          type: 'CREDIT',
          merchant: 'NeoBharat Capital',
          category: 'OTHER',
          status: 'SUCCESS',
          title: 'Loan Disbursal',
        };
        const { createTransaction } = await import('../services/api');
        await createTransaction(activePersona.id, payload);

        if (refreshCustomerData) {
          await refreshCustomerData();
        }

        setLoanStep('disbursed');
        onLoanDisbursedSuccess();
      } catch (error) {
        alert('Failed to disburse loan');
        setLoanStep('review');
      }
    }, 2000);
  };

  return (
    <>
      {/* GLOBAL TOAST FOR RECEIVED PAYMENTS */}
      {receivedToast && (
        <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 animate-bounce max-w-md w-[92%] p-3.5 rounded-2xl bg-gradient-to-r from-emerald-600 via-[#00A86B] to-[#046A38] text-white shadow-2xl flex items-center justify-between gap-3 border border-emerald-300 select-none">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center shrink-0">
              <ArrowDownLeft className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-emerald-100">
                {lang === 'en' ? 'UPI Payment Received!' : 'यूपीआई भुगतान प्राप्त हुआ!'}
              </p>
              <p className="text-sm font-black">
                +₹{receivedToast.amount.toLocaleString('en-IN')}
                <span className="font-normal text-xs opacity-90 ml-1.5">
                  from {receivedToast.sender}
                </span>
              </p>
            </div>
          </div>
          <button
            onClick={() => setReceivedToast(null)}
            className="p-1 rounded-lg hover:bg-white/20 text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* 1. SEND MONEY MODAL */}
      {showSendModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 animate-fade-in">
          <div
            className={`w-full max-w-lg rounded-3xl border p-5 shadow-2xl overflow-hidden transition-all ${
              isDark ? 'bg-[#0B1020] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900'
            }`}
          >
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-700/60 dark:border-slate-800 border-slate-200">
              <div className="flex items-center gap-2.5">
                <div className="w-10 h-10 rounded-2xl bg-[#00A86B] text-white flex items-center justify-center shadow-md shadow-emerald-500/30">
                  <Send className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-black text-base sm:text-lg">
                    {lang === 'en' ? 'Send Money via UPI' : 'यूपीआई द्वारा पैसे भेजें'}
                  </h3>
                  <p className="text-xs text-emerald-400 font-bold">
                    {lang === 'en' ? 'Instant 24×7 Zero Charges' : 'तत्काल 24×7 शून्य शुल्क'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => {
                  setShowSendModal(false);
                  setSendSuccess(null);
                  setSelectedPayee(null);
                }}
                className="w-8 h-8 rounded-full bg-slate-800/60 hover:bg-slate-700 flex items-center justify-center text-slate-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {sendSuccess ? (
              /* Success View */
              <div className="py-6 text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-emerald-500/20 border-2 border-emerald-500 flex items-center justify-center mx-auto text-emerald-400 animate-bounce">
                  <CheckCircle2 className="w-9 h-9" />
                </div>

                <div>
                  <h4 className="text-xl font-black text-emerald-400">
                    {lang === 'en' ? 'Payment Successful!' : 'भुगतान सफल रहा!'}
                  </h4>
                  <p className="text-3xl font-black font-mono mt-1 text-white dark:text-white text-slate-900">
                    ₹{sendSuccess.amount.toLocaleString('en-IN')}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    {lang === 'en' ? 'Transferred to' : 'भेजा गया:'}{' '}
                    <span className="font-bold text-slate-200">{sendSuccess.recipientName}</span>
                  </p>
                </div>

                {/* Receipt Card */}
                <div
                  className={`p-3.5 rounded-2xl text-left text-xs space-y-1.5 border font-mono ${
                    isDark ? 'bg-[#060A14] border-slate-800 text-slate-300' : 'bg-slate-50 border-slate-200 text-slate-700'
                  }`}
                >
                  <div className="flex justify-between">
                    <span className="text-slate-500">UTR / Ref:</span>
                    <span className="font-bold text-emerald-400">{sendSuccess.utr}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Debited From:</span>
                    <span>State Bank of India (•••• 4821)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Date & Time:</span>
                    <span>{sendSuccess.date}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Status:</span>
                    <span className="text-emerald-400 font-bold">COMPLETED (NPCI)</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-2">
                  <button
                    onClick={() => {
                      setShowSendModal(false);
                      setSendSuccess(null);
                      setSelectedPayee(null);
                    }}
                    className="flex-1 py-3 rounded-xl bg-gradient-to-r from-[#00A86B] to-[#047857] text-white font-black text-sm shadow-md"
                  >
                    {lang === 'en' ? 'Done' : 'पूर्ण'}
                  </button>
                  <button
                    onClick={() => {
                      alert('Receipt shared via WhatsApp successfully!');
                    }}
                    className="p-3 rounded-xl border border-slate-700 hover:bg-slate-800 text-slate-200"
                    title="Share Receipt"
                  >
                    <Share2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ) : (
              /* Input Form */
              <div className="py-4 space-y-4">
                {/* Debiting Account Strip */}
                <div
                  className={`p-3 rounded-2xl border flex items-center justify-between text-xs ${
                    isDark ? 'bg-[#060812] border-slate-800' : 'bg-slate-50 border-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <div>
                      <span className="font-bold block">
                        State Bank of India ({activePersona.accountNumber})
                      </span>
                      <span className="text-slate-400 text-[11px]">Primary Citizen Account</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-slate-400 text-[10px] block">Available Balance</span>
                    <span className="font-mono font-bold text-emerald-400">
                      ₹{activePersona.accountBalance.toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>

                {/* Recipient Input */}
                <div>
                  <label className="text-xs font-bold text-slate-400 mb-1 block">
                    {lang === 'en' ? 'Payee UPI ID or Mobile Number' : 'लाभार्थी का यूपीआई आईडी या मोबाइल'}
                  </label>
                  <input
                    type="text"
                    value={recipient}
                    onChange={(e) => setRecipient(e.target.value)}
                    placeholder="e.g. 9835044102 or merchant@sbi"
                    className={`w-full p-3 rounded-xl border text-sm font-semibold outline-none transition-all ${
                      isDark
                        ? 'bg-[#060A14] border-slate-700 text-white focus:border-emerald-500'
                        : 'bg-white border-slate-300 text-slate-900 focus:border-emerald-600'
                    }`}
                  />
                </div>

                {/* Amount Input & Quick Chips */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-bold text-slate-400">
                      {lang === 'en' ? 'Enter Amount (₹)' : 'राशि दर्ज करें (₹)'}
                    </label>
                    <span className="text-[11px] font-bold text-emerald-400">Zero Charges</span>
                  </div>
                  <div className="relative">
                    <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-xl font-bold text-slate-400 font-mono">
                      ₹
                    </span>
                    <input
                      type="number"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      className={`w-full pl-9 pr-3 py-3 rounded-xl border text-xl font-black font-mono outline-none transition-all ${
                        isDark
                          ? 'bg-[#060A14] border-slate-700 text-white focus:border-emerald-500'
                          : 'bg-white border-slate-300 text-slate-900 focus:border-emerald-600'
                      }`}
                    />
                  </div>

                  {/* Quick chips */}
                  <div className="flex items-center gap-1.5 mt-2 overflow-x-auto no-scrollbar">
                    {['200', '500', '850', '1000', '2500', '5000'].map((chip) => (
                      <button
                        key={chip}
                        type="button"
                        onClick={() => setAmount(chip)}
                        className={`px-2.5 py-1 rounded-lg text-xs font-bold font-mono border transition-all ${
                          amount === chip
                            ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400'
                            : 'bg-slate-800/40 border-slate-700 text-slate-300 hover:border-slate-600'
                        }`}
                      >
                        +₹{chip}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Note */}
                <div>
                  <label className="text-xs font-bold text-slate-400 mb-1 block">
                    {lang === 'en' ? 'Note / Purpose (Optional)' : 'विवरण (वैकल्पिक)'}
                  </label>
                  <input
                    type="text"
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    placeholder="e.g. Vegetable order, groceries, fee"
                    className={`w-full p-2.5 rounded-xl border text-xs font-medium outline-none transition-all ${
                      isDark
                        ? 'bg-[#060A14] border-slate-700 text-white focus:border-emerald-500'
                        : 'bg-white border-slate-300 text-slate-900 focus:border-emerald-600'
                    }`}
                  />
                </div>

                {/* Pay Button */}
                <button
                  type="button"
                  disabled={isProcessingSend || !recipient || !amount}
                  onClick={handleSendPayment}
                  className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-[#00A86B] to-[#047857] hover:brightness-110 active:scale-[0.99] text-white font-black text-sm sm:text-base shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  {isProcessingSend ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      <span>{lang === 'en' ? 'Authorizing with UPI...' : 'यूपीआई से भुगतान हो रहा है...'}</span>
                    </>
                  ) : (
                    <>
                      <Fingerprint className="w-5 h-5" />
                      <span>
                        {lang === 'en'
                          ? `Pay ₹${parseFloat(amount || '0').toLocaleString('en-IN')} with 1-Tap UPI`
                          : `1-टैप यूपीआई से ₹${parseFloat(amount || '0').toLocaleString('en-IN')} चुकाएं`}
                      </span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 2. RECEIVE MONEY / MY QR MODAL */}
      {showReceiveModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 animate-fade-in">
          <div
            className={`w-full max-w-md rounded-3xl border p-5 shadow-2xl overflow-hidden transition-all text-center ${
              isDark ? 'bg-[#0B1020] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900'
            }`}
          >
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-700/60 dark:border-slate-800 border-slate-200">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-2xl bg-[#FF671F] text-white flex items-center justify-center shadow-md shadow-orange-500/30">
                  <Download className="w-5 h-5" />
                </div>
                <div className="text-left">
                  <h3 className="font-black text-base">
                    {lang === 'en' ? 'Receive Money / My QR' : 'पैसे पाएं / मेरा क्यूआर'}
                  </h3>
                  <p className="text-[11px] text-[#FF671F] font-bold">
                    {lang === 'en' ? 'Bharat QR & Any UPI App' : 'भारत क्यूआर एवं सभी यूपीआई ऐप'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowReceiveModal(false)}
                className="w-8 h-8 rounded-full bg-slate-800/60 hover:bg-slate-700 flex items-center justify-center text-slate-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* QR Card Container */}
            <div className="py-4 space-y-4">
              <div className="bg-white p-4 sm:p-5 rounded-3xl border border-orange-200 shadow-xl inline-block mx-auto max-w-[260px] w-full">
                {/* SVG Bharat QR Code */}
                <div className="relative aspect-square w-full rounded-xl overflow-hidden flex items-center justify-center bg-white p-2">
                  <svg viewBox="0 0 100 100" className="w-full h-full">
                    {/* QR Code Matrix Pattern */}
                    <rect width="100" height="100" fill="#FFFFFF" />
                    {/* Corners */}
                    <rect x="5" y="5" width="26" height="26" fill="#000000" rx="3" />
                    <rect x="8" y="8" width="20" height="20" fill="#FFFFFF" rx="2" />
                    <rect x="11" y="11" width="14" height="14" fill="#000080" rx="2" />

                    <rect x="69" y="5" width="26" height="26" fill="#000000" rx="3" />
                    <rect x="72" y="8" width="20" height="20" fill="#FFFFFF" rx="2" />
                    <rect x="75" y="11" width="14" height="14" fill="#000080" rx="2" />

                    <rect x="5" y="69" width="26" height="26" fill="#000000" rx="3" />
                    <rect x="8" y="72" width="20" height="20" fill="#FFFFFF" rx="2" />
                    <rect x="11" y="75" width="14" height="14" fill="#000080" rx="2" />

                    {/* Data Pixels */}
                    <rect x="36" y="8" width="6" height="6" fill="#000000" />
                    <rect x="46" y="8" width="6" height="6" fill="#FF671F" />
                    <rect x="56" y="8" width="6" height="6" fill="#000000" />
                    <rect x="36" y="18" width="6" height="6" fill="#046A38" />
                    <rect x="48" y="22" width="6" height="6" fill="#000000" />

                    <rect x="8" y="36" width="6" height="6" fill="#000000" />
                    <rect x="18" y="36" width="6" height="6" fill="#FF671F" />
                    <rect x="28" y="44" width="6" height="6" fill="#000000" />
                    <rect x="12" y="48" width="6" height="6" fill="#046A38" />

                    <rect x="68" y="36" width="6" height="6" fill="#000000" />
                    <rect x="78" y="44" width="6" height="6" fill="#046A38" />
                    <rect x="86" y="36" width="6" height="6" fill="#FF671F" />
                    <rect x="72" y="52" width="6" height="6" fill="#000000" />

                    <rect x="36" y="68" width="6" height="6" fill="#000000" />
                    <rect x="44" y="78" width="6" height="6" fill="#FF671F" />
                    <rect x="54" y="68" width="6" height="6" fill="#046A38" />
                    <rect x="60" y="80" width="6" height="6" fill="#000000" />

                    {/* Center Ashoka Chakra Badge */}
                    <circle cx="50" cy="50" r="14" fill="#FFFFFF" stroke="#FF671F" strokeWidth="1.5" />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <ChakraLogo size={22} animate={true} />
                  </div>
                </div>

                <div className="mt-2 text-center">
                  <p className="text-xs font-black text-slate-900">
                    {activePersona.name}
                  </p>
                  <p className="text-[10px] text-slate-600 font-mono font-bold">
                    {activePersona.upiId}
                  </p>
                </div>
              </div>

              {/* UPI ID Copy Bar */}
              <div
                className={`p-2.5 rounded-2xl border flex items-center justify-between text-xs ${
                  isDark ? 'bg-[#060812] border-slate-800' : 'bg-slate-100 border-slate-200 text-slate-800'
                }`}
              >
                <div className="text-left truncate mr-2">
                  <span className="text-[10px] text-slate-400 block font-semibold">Your UPI ID</span>
                  <span className="font-mono font-bold text-xs truncate block">
                    {activePersona.upiId}
                  </span>
                </div>
                <button
                  onClick={handleCopyVpa}
                  className="px-2.5 py-1 rounded-xl bg-orange-500/20 text-[#FF671F] font-bold text-xs flex items-center gap-1 shrink-0 hover:bg-orange-500/30"
                >
                  {copiedVpa ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>

              {/* Instant Simulation: Customer Pays You */}
              <div className="p-3 rounded-2xl bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-emerald-500/10 border border-emerald-500/30 text-left">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold text-emerald-400">
                    {lang === 'en' ? '🧪 Test Receive Money (Live Simulation)' : '🧪 पैसे प्राप्त करने का परीक्षण करें'}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 leading-tight mb-2.5">
                  {lang === 'en'
                    ? 'Simulate a customer paying you ₹1,200 via PhonePe/GPay to test instant balance update.'
                    : 'ग्राहक द्वारा ₹1,200 यूपीआई भुगतान का तुरंत परीक्षण करें।'}
                </p>

                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => handleSimulateCustomerPayment(500)}
                    className="py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs font-mono shadow-sm"
                  >
                    +₹500
                  </button>
                  <button
                    onClick={() => handleSimulateCustomerPayment(1200)}
                    className="py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs font-mono shadow-sm"
                  >
                    +₹1,200
                  </button>
                  <button
                    onClick={() => handleSimulateCustomerPayment(2500)}
                    className="py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs font-mono shadow-sm"
                  >
                    +₹2,500
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 3. SCAN ANY QR MODAL */}
      {showScanModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 animate-fade-in">
          <div
            className={`w-full max-w-md rounded-3xl border p-5 shadow-2xl overflow-hidden transition-all text-center ${
              isDark ? 'bg-[#0B1020] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900'
            }`}
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-2xl bg-[#7C3AED] text-white flex items-center justify-center shadow-md">
                  <QrCode className="w-5 h-5" />
                </div>
                <div className="text-left">
                  <h3 className="font-black text-base">
                    {lang === 'en' ? 'Scan Any QR Code' : 'कोई भी क्यूआर कोड स्कैन करें'}
                  </h3>
                  <p className="text-[11px] text-purple-400 font-bold">
                    {lang === 'en' ? 'Shop, Mandi & Vendor QR' : 'दुकान व मंडी क्यूआर'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowScanModal(false)}
                className="w-8 h-8 rounded-full bg-slate-800/60 hover:bg-slate-700 flex items-center justify-center text-slate-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Camera Viewfinder simulator */}
            <div className="py-4 space-y-3">
              <div className="relative w-full aspect-square max-w-[250px] mx-auto rounded-3xl bg-slate-950 border-2 border-purple-500/50 overflow-hidden flex items-center justify-center shadow-2xl">
                {/* Viewfinder crosshairs */}
                <div className="absolute top-4 left-4 w-7 h-7 border-t-4 border-l-4 border-purple-400 rounded-tl-xl" />
                <div className="absolute top-4 right-4 w-7 h-7 border-t-4 border-r-4 border-purple-400 rounded-tr-xl" />
                <div className="absolute bottom-4 left-4 w-7 h-7 border-b-4 border-l-4 border-purple-400 rounded-bl-xl" />
                <div className="absolute bottom-4 right-4 w-7 h-7 border-b-4 border-r-4 border-purple-400 rounded-br-xl" />

                {/* Animated scanning laser line */}
                <div className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-purple-400 to-transparent animate-pulse shadow-lg shadow-purple-500" />

                <div className="text-center px-4">
                  <QrCode className="w-16 h-16 text-purple-400/40 mx-auto animate-pulse" />
                  <p className="text-xs text-purple-300 font-bold mt-2">
                    {lang === 'en' ? 'Align QR inside the box' : 'क्यूआर कोड को फ्रेम में रखें'}
                  </p>
                </div>
              </div>

              {/* Demo QR Presets */}
              <div className="text-left space-y-2">
                <p className="text-xs font-bold text-slate-400">
                  {lang === 'en' ? 'Or Tap Quick Merchant to Simulate Scan:' : 'या त्वरित व्यापारी स्कैन चुनें:'}
                </p>

                <div className="space-y-1.5">
                  <button
                    onClick={() => {
                      setShowScanModal(false);
                      setRecipient('Ranchi Sabzi Mandi Wholesale (ranchisabzi@sbi)');
                      setAmount('850');
                      setShowSendModal(true);
                    }}
                    className="w-full p-2.5 rounded-xl bg-slate-900 hover:bg-purple-950/40 border border-slate-800 hover:border-purple-500 text-left flex items-center justify-between text-xs transition-all"
                  >
                    <span className="flex items-center gap-2">
                      <span>🥦</span>
                      <span className="font-bold">Ranchi Sabzi Mandi</span>
                    </span>
                    <span className="font-mono font-bold text-emerald-400">₹850</span>
                  </button>

                  <button
                    onClick={() => {
                      setShowScanModal(false);
                      setRecipient('Hindustan Unilever Wholesale (hulwholesale@icici)');
                      setAmount('3200');
                      setShowSendModal(true);
                    }}
                    className="w-full p-2.5 rounded-xl bg-slate-900 hover:bg-purple-950/40 border border-slate-800 hover:border-purple-500 text-left flex items-center justify-between text-xs transition-all"
                  >
                    <span className="flex items-center gap-2">
                      <span>📦</span>
                      <span className="font-bold">Hindustan Unilever Depot</span>
                    </span>
                    <span className="font-mono font-bold text-emerald-400">₹3,200</span>
                  </button>

                  <button
                    onClick={() => {
                      setShowScanModal(false);
                      setRecipient('Jharkhand Bijli Vitran Nigam (jbvnl.bills@sbi)');
                      setAmount('1420');
                      setShowSendModal(true);
                    }}
                    className="w-full p-2.5 rounded-xl bg-slate-900 hover:bg-purple-950/40 border border-slate-800 hover:border-purple-500 text-left flex items-center justify-between text-xs transition-all"
                  >
                    <span className="flex items-center gap-2">
                      <span>⚡</span>
                      <span className="font-bold">Jharkhand Bijli Board</span>
                    </span>
                    <span className="font-mono font-bold text-emerald-400">₹1,420</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 4. BILLS & UTILITIES MODAL */}
      {showBillsModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 animate-fade-in">
          <div
            className={`w-full max-w-md rounded-3xl border p-5 shadow-2xl overflow-hidden transition-all ${
              isDark ? 'bg-[#0B1020] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900'
            }`}
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-2xl bg-[#0284C7] text-white flex items-center justify-center shadow-md">
                  <Zap className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-black text-base">
                    {lang === 'en' ? 'Bills & Utilities (BBPS)' : 'बिल व उपयोगिता (भारत बिलपे)'}
                  </h3>
                  <p className="text-[11px] text-sky-400 font-bold">
                    {lang === 'en' ? 'Official NPCI Bharat BillPay' : 'एनपीसीआई भारत बिलपे एकीकृत'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowBillsModal(false)}
                className="w-8 h-8 rounded-full bg-slate-800/60 hover:bg-slate-700 flex items-center justify-center text-slate-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="py-4 space-y-2.5">
              {[
                {
                  id: 'bill-1',
                  name: 'Jharkhand Bijli Vitran Nigam',
                  cat: 'Electricity',
                  icon: <Zap className="w-5 h-5 text-amber-400" />,
                  amount: 1420,
                  due: 'Due in 4 days',
                },
                {
                  id: 'bill-2',
                  name: 'Indane Gas LPG Cylinder',
                  cat: 'LPG Gas',
                  icon: <Flame className="w-5 h-5 text-orange-400" />,
                  amount: 850,
                  due: 'Refill ready',
                },
                {
                  id: 'bill-3',
                  name: 'Jio Prepaid 5G Plan',
                  cat: 'Mobile',
                  icon: <Smartphone className="w-5 h-5 text-blue-400" />,
                  amount: 299,
                  due: '28 Days 2GB/Day',
                },
                {
                  id: 'bill-4',
                  name: 'NHAI FASTag Recharge',
                  cat: 'FASTag',
                  icon: <Car className="w-5 h-5 text-emerald-400" />,
                  amount: 500,
                  due: 'Auto-Toll Active',
                },
              ].map((bill) => (
                <div
                  key={bill.id}
                  className="p-3 rounded-2xl bg-[#060812] border border-slate-800 flex items-center justify-between text-xs hover:border-sky-500 transition-all"
                >
                  <div className="flex items-center gap-2.5">
                    <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center border border-slate-800">
                      {bill.icon}
                    </div>
                    <div>
                      <span className="font-bold text-white block">{bill.name}</span>
                      <span className="text-slate-400 text-[10px]">{bill.due}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      setShowBillsModal(false);
                      setRecipient(`${bill.name} (BBPS/${bill.id})`);
                      setAmount(bill.amount.toString());
                      setShowSendModal(true);
                    }}
                    className="px-3 py-1.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-bold font-mono text-xs flex items-center gap-1 shadow-sm"
                  >
                    <span>Pay ₹{bill.amount}</span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 5. ANTI-SCAM ALERT MODAL (TRIGGERED ON URGENT ELECTRICITY TEST SCAM) */}
      {showScamModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3 sm:p-4 animate-fade-in">
          <div className="w-full max-w-md rounded-3xl border-2 border-amber-500 bg-[#0E121E] text-white p-5 shadow-2xl shadow-amber-500/20">
            <div className="flex items-center gap-3 pb-3 border-b border-amber-500/30">
              <div className="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500 flex items-center justify-center text-amber-400 animate-pulse">
                <ShieldAlert className="w-7 h-7" />
              </div>
              <div>
                <h3 className="text-base sm:text-lg font-black text-amber-400">
                  {lang === 'en' ? '🚨 High-Risk Cyber Scam Blocked!' : '🚨 उच्च जोखिम साइबर धोखाधड़ी अवरुद्ध!'}
                </h3>
                <p className="text-xs text-slate-300 font-semibold">
                  NeoBharat AI Fraud & Phishing Shield
                </p>
              </div>
            </div>

            <div className="py-4 space-y-3 text-xs leading-relaxed">
              <div className="p-3 rounded-xl bg-amber-950/40 border border-amber-500/30 text-amber-200 space-y-1">
                <div className="flex justify-between font-bold">
                  <span>Targeted Payee:</span>
                  <span className="font-mono text-white">urgent.electricity.due@ybl</span>
                </div>
                <div className="flex justify-between font-bold">
                  <span>Citizens Flagged:</span>
                  <span className="text-amber-400">1,420 Reports (I4C Portal 1930)</span>
                </div>
              </div>

              <p className="text-slate-300">
                {lang === 'en'
                  ? 'This payee was detected impersonating Jharkhand Bijli Vitran Nigam using artificial urgency ("Electricity will be disconnected in 2 hours"). NeoBharat has blocked this payment to protect your funds.'
                  : 'यह यूपीआई पता फर्जी बिजली बिल नोटिस भेजकर नागरिकों को ठगने हेतु चिह्नित किया गया है। नियो-भारत ने आपकी सुरक्षा हेतु यह भुगतान ब्लॉक कर दिया है।'}
              </p>

              <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                <span className="text-[11px] font-bold">
                  {lang === 'en' ? 'Your account balance is safe. Zero money was deducted.' : 'आपका बैंक बैलेंस पूरी तरह सुरक्षित है। कोई कटौती नहीं हुई।'}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <button
                onClick={() => setShowScamModal(false)}
                className="flex-1 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs"
              >
                {lang === 'en' ? 'Close Safely' : 'सुरक्षित बंद करें'}
              </button>
              <button
                onClick={() => {
                  alert('Report logged with National Cyber Crime Reporting Portal (1930). Thank you for keeping Bharat safe!');
                  setShowScamModal(false);
                }}
                className="flex-1 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs"
              >
                {lang === 'en' ? 'Report to Cyber Cell 1930' : '1930 पर रिपोर्ट करें'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 6. BIOMETRIC LOAN ACCEPTANCE MODAL */}
      {showLoanModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3 sm:p-4 animate-fade-in">
          <div className="w-full max-w-md rounded-3xl border border-slate-800 bg-[#0B1020] text-white p-5 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-[#FF671F] to-[#10B981] flex items-center justify-center text-slate-950 font-black">
                  <Fingerprint className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-black text-base">
                    {lang === 'en' ? '3-Factor Biometric Disbursal' : '3-कारक बायोमेट्रिक ऋण संवितरण'}
                  </h3>
                  <p className="text-[11px] text-emerald-400 font-bold">
                    {lang === 'en' ? 'RBI Compliant · Instant Credit' : 'आरबीआई प्रमाणित · तुरंत जमा'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowLoanModal(false)}
                className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {loanStep === 'review' && (
              <div className="py-4 space-y-4">
                <div className="p-4 rounded-2xl bg-[#060810] border border-slate-800 text-center">
                  <span className="text-xs text-slate-400 block font-semibold">Sanctioned Amount</span>
                  <span className="text-3xl font-black text-[#FF7700] font-mono mt-1 block">
                    ₹25,000
                  </span>
                  <span className="text-xs text-emerald-400 font-bold block mt-1">
                    Diwali Festive Working Capital
                  </span>
                </div>

                <div className="text-xs space-y-2 text-slate-300">
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Credited To:</span>
                    <span className="font-bold text-white">State Bank of India (•••• 4821)</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Monthly EMI:</span>
                    <span className="font-bold text-white">₹2,204</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Interest Rate:</span>
                    <span className="font-bold text-emerald-400">10.5% p.a.</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Processing Fee:</span>
                    <span className="font-bold text-emerald-400">₹0 (शून्य)</span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleDisburseLoan}
                  className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-[#FF671F] via-[#F59E0B] to-[#10B981] text-slate-950 font-black text-sm shadow-lg flex items-center justify-center gap-2 hover:brightness-110 active:scale-95"
                >
                  <Fingerprint className="w-5 h-5" />
                  <span>{lang === 'en' ? 'Confirm with Aadhaar Biometrics' : 'आधार बायोमेट्रिक से पुष्टि करें'}</span>
                </button>
              </div>
            )}

            {loanStep === 'biometric' && (
              <div className="py-8 text-center space-y-4">
                <div className="w-20 h-20 rounded-full bg-orange-500/20 border-2 border-orange-500 flex items-center justify-center mx-auto text-[#FF671F] animate-pulse">
                  <Fingerprint className="w-12 h-12 animate-bounce" />
                </div>
                <div>
                  <h4 className="text-base font-black text-white">
                    {lang === 'en' ? 'Verifying 3-Factor Biometric...' : '3-कारक बायोमेट्रिक सत्यापन जारी...'}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1">
                    Aadhaar OTP + Face Liveness + Fingerprint via UIDAI
                  </p>
                </div>
              </div>
            )}

            {loanStep === 'disbursed' && (
              <div className="py-6 text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-emerald-500/20 border-2 border-emerald-500 flex items-center justify-center mx-auto text-emerald-400">
                  <CheckCircle2 className="w-10 h-10" />
                </div>
                <div>
                  <h4 className="text-xl font-black text-emerald-400">
                    {lang === 'en' ? '₹25,000 Credited Instantly!' : '₹25,000 तुरंत खाते में जमा!'}
                  </h4>
                  <p className="text-xs text-slate-300 mt-1">
                    Deposited into State Bank of India (•••• 4821)
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => setShowLoanModal(false)}
                  className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs"
                >
                  {lang === 'en' ? 'View Updated Account Balance' : 'अद्यतन बैंक बैलेंस देखें'}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 7. INSTALL APP MODAL */}
      {showInstallModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 animate-fade-in">
          <div className="w-full max-w-md rounded-3xl border border-slate-800 bg-[#0B1020] text-white p-5 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Smartphone className="w-5 h-5 text-emerald-400" />
                <h3 className="font-black text-base">
                  {lang === 'en' ? 'Install NeoBharat Mobile App' : 'नियो-भारत मोबाइल ऐप इंस्टॉल'}
                </h3>
              </div>
              <button
                onClick={() => setShowInstallModal(false)}
                className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="py-4 space-y-3 text-xs text-slate-300">
              <p>
                {lang === 'en'
                  ? 'NeoBharat is certified by the Digital India Initiative as a zero-bloat, secure PWA and Android Package (APK/AAB).'
                  : 'नियो-भारत डिजिटल इंडिया द्वारा प्रमाणित त्वरित, सुरक्षित ऐप है।'}
              </p>

              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
                <div className="flex justify-between font-bold">
                  <span>Release:</span>
                  <span className="text-emerald-400">v2.4 Production (Build 4821)</span>
                </div>
                <div className="flex justify-between font-bold">
                  <span>Security:</span>
                  <span className="text-emerald-400">Cert-In & RBI Fair Lending Certified</span>
                </div>
                <div className="flex justify-between font-bold">
                  <span>Size:</span>
                  <span className="font-mono text-white">4.2 MB (Lightweight Offline Cache)</span>
                </div>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  onClick={() => {
                    alert('NeoBharat PWA installed to your home screen!');
                    setShowInstallModal(false);
                  }}
                  className="flex-1 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-black text-xs"
                >
                  {lang === 'en' ? 'Add to Home Screen (PWA)' : 'होम स्क्रीन पर जोड़ें'}
                </button>
                <button
                  onClick={() => {
                    alert('Downloading official NeoBharat.apk (4.2 MB)...');
                    setShowInstallModal(false);
                  }}
                  className="flex-1 py-3 rounded-xl border border-slate-700 hover:bg-slate-800 text-slate-200 font-bold text-xs"
                >
                  {lang === 'en' ? 'Download APK/AAB' : 'एपीके डाउनलोड'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 8. VERIFY PHONE & BANK MODAL */}
      {showVerifyModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 animate-fade-in">
          <div className="w-full max-w-md rounded-3xl border border-slate-800 bg-[#0B1020] text-white p-5 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-amber-400" />
                <h3 className="font-black text-base">
                  {lang === 'en' ? 'Phone & Bank Verification Status' : 'फ़ोन व बैंक सत्यापन स्थिति'}
                </h3>
              </div>
              <button
                onClick={() => setShowVerifyModal(false)}
                className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="py-4 space-y-2.5 text-xs text-slate-300">
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-slate-400 block text-[10px]">Aadhaar-Linked Mobile</span>
                  <span className="font-bold text-white font-mono">{activePersona.phone || '+91 98350 44102'}</span>
                </div>
                <span className="text-emerald-400 font-bold text-xs">✓ Verified OTP</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-slate-400 block text-[10px]">NPCI Aadhaar Payment Bridge (APB)</span>
                  <span className="font-bold text-white">{activePersona.bankName || 'State Bank of India'}</span>
                </div>
                <span className="text-emerald-400 font-bold text-xs">✓ Active DBT</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-slate-400 block text-[10px]">UPI 2.0 Auto-Pay & Mandates</span>
                  <span className="font-bold text-white font-mono">{activePersona.upiId}</span>
                </div>
                <span className="text-emerald-400 font-bold text-xs">✓ Active</span>
              </div>
            </div>

            <button
              onClick={() => setShowVerifyModal(false)}
              className="w-full py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs"
            >
              {lang === 'en' ? 'Close' : 'बंद करें'}
            </button>
          </div>
        </div>
      )}

      {/* 9. DPDP CONSENT MODAL */}
      {showDpdpModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 animate-fade-in">
          <div className="w-full max-w-md rounded-3xl border border-slate-800 bg-[#0B1020] text-white p-5 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-blue-400" />
                <h3 className="font-black text-base">
                  {lang === 'en' ? 'DPDP Act 2023 Consent Manager' : 'डीपीडीपी अधिनियम 2023 सहमति प्रबंधन'}
                </h3>
              </div>
              <button
                onClick={() => setShowDpdpModal(false)}
                className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="py-4 space-y-3 text-xs text-slate-300">
              <p className="text-slate-400">
                {lang === 'en'
                  ? 'Digital Personal Data Protection Act (DPDP) 2023 grants you 100% control over your financial data. You may revoke consent anytime.'
                  : 'डिजिटल व्यक्तिगत डेटा संरक्षण अधिनियम (डीपीडीपी) के तहत आपका अपने डेटा पर पूर्ण अधिकार है।'}
              </p>

              <div className="space-y-2">
                {[
                  {
                    title: 'Account Aggregator (RBI-AA)',
                    desc: 'Read-only financial statements for working capital evaluation',
                    status: true,
                  },
                  {
                    title: 'Credit Bureau Periodic Scoring',
                    desc: 'Monthly credit score check for fair interest reductions',
                    status: true,
                  },
                  {
                    title: 'Zero Third-Party Advertising Sharing',
                    desc: 'Strict bank privacy, data is never monetized or sold',
                    status: true,
                  },
                ].map((item, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex items-start justify-between gap-2"
                  >
                    <div>
                      <span className="font-bold text-white block">{item.title}</span>
                      <span className="text-[10px] text-slate-400 leading-tight">{item.desc}</span>
                    </div>
                    <span className="text-emerald-400 font-bold text-xs shrink-0">Active</span>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={() => setShowDpdpModal(false)}
              className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-black text-xs"
            >
              {lang === 'en' ? 'Save & Close' : 'सुरक्षित करें'}
            </button>
          </div>
        </div>
      )}
    </>
  );
};
