import React from 'react';
import { Language } from '../types';
import { Send, QrCode, Download, Zap } from 'lucide-react';

interface ActionCardsGridProps {
  lang: Language;
  onSendMoney: () => void;
  onScanQr: () => void;
  onReceiveMoney: () => void;
  onBillsUtilities: () => void;
}

export const ActionCardsGrid: React.FC<ActionCardsGridProps> = ({
  lang,
  onSendMoney,
  onScanQr,
  onReceiveMoney,
  onBillsUtilities,
}) => {
  return (
    <div className="w-full grid grid-cols-2 gap-3 sm:gap-3.5 select-none">
      {/* 1. Send Money (Emerald Green) */}
      <button
        type="button"
        onClick={onSendMoney}
        className="group relative overflow-hidden rounded-2xl sm:rounded-3xl p-4 sm:p-4.5 text-center flex flex-col items-center justify-center transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] shadow-md hover:shadow-emerald-500/20 bg-gradient-to-b from-[#00A86B] to-[#047857] text-white cursor-pointer min-h-[135px]"
        aria-label="Send Money to Mobile or UPI ID"
      >
        {/* Subtle radial shine */}
        <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

        {/* Top circular icon */}
        <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center mb-2.5 shadow-inner group-hover:rotate-6 transition-transform">
          <Send className="w-6 h-6 text-white" />
        </div>

        {/* Title */}
        <h3 className="text-base font-black tracking-tight leading-tight">
          {lang === 'en' ? 'Send Money' : 'पैसे भेजें'}
        </h3>

        {/* Subtitle */}
        <p className="text-xs text-emerald-100 font-medium mt-0.5">
          {lang === 'en' ? 'To Mobile or UPI ID' : 'मोबाइल या यूपीआई आईडी'}
        </p>
      </button>

      {/* 2. Scan Any QR (Vibrant Violet / Purple) */}
      <button
        type="button"
        onClick={onScanQr}
        className="group relative overflow-hidden rounded-2xl sm:rounded-3xl p-4 sm:p-4.5 text-center flex flex-col items-center justify-center transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] shadow-md hover:shadow-purple-500/20 bg-gradient-to-b from-[#7C3AED] to-[#5B21B6] text-white cursor-pointer min-h-[135px]"
        aria-label="Scan Any QR code to pay at shop or vendor"
      >
        <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

        <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center mb-2.5 shadow-inner group-hover:scale-105 transition-transform">
          <QrCode className="w-6 h-6 text-white" />
        </div>

        <h3 className="text-base font-black tracking-tight leading-tight">
          {lang === 'en' ? 'Scan Any QR' : 'कोई भी क्यूआर स्कैन'}
        </h3>

        <p className="text-xs text-purple-200 font-medium mt-0.5">
          {lang === 'en' ? 'Pay at Shop / Vendor' : 'दुकान या व्यापारी पर भुगतान'}
        </p>
      </button>

      {/* 3. Receive / My QR (Vibrant Orange / Saffron) */}
      <button
        type="button"
        onClick={onReceiveMoney}
        className="group relative overflow-hidden rounded-2xl sm:rounded-3xl p-4 sm:p-4.5 text-center flex flex-col items-center justify-center transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] shadow-md hover:shadow-orange-500/20 bg-gradient-to-b from-[#FF671F] to-[#C2410C] text-white cursor-pointer min-h-[135px]"
        aria-label="Receive Money or Show Personal QR"
      >
        <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

        <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center mb-2.5 shadow-inner group-hover:-translate-y-0.5 transition-transform">
          <Download className="w-6 h-6 text-white" />
        </div>

        <h3 className="text-base font-black tracking-tight leading-tight">
          {lang === 'en' ? 'Receive / My QR' : 'पैसे पाएं / मेरा क्यूआर'}
        </h3>

        <p className="text-xs text-orange-100 font-medium mt-0.5">
          {lang === 'en' ? 'Show Personal QR' : 'अपना व्यक्तिगत क्यूआर दिखाएं'}
        </p>
      </button>

      {/* 4. Bills & Utilities (Vibrant Electric Blue) */}
      <button
        type="button"
        onClick={onBillsUtilities}
        className="group relative overflow-hidden rounded-2xl sm:rounded-3xl p-4 sm:p-4.5 text-center flex flex-col items-center justify-center transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] shadow-md hover:shadow-blue-500/20 bg-gradient-to-b from-[#0284C7] to-[#0369A1] text-white cursor-pointer min-h-[135px]"
        aria-label="Pay Bills & Utilities like Electricity, LPG, Mobile"
      >
        <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

        <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center mb-2.5 shadow-inner group-hover:scale-105 transition-transform">
          <Zap className="w-6 h-6 text-white" />
        </div>

        <h3 className="text-base font-black tracking-tight leading-tight">
          {lang === 'en' ? 'Bills & Utilities' : 'बिल व उपयोगिता'}
        </h3>

        <p className="text-xs text-sky-100 font-medium mt-0.5">
          {lang === 'en' ? 'Electricity, LPG, Mobile' : 'बिजली, गैस, मोबाइल'}
        </p>
      </button>
    </div>
  );
};
