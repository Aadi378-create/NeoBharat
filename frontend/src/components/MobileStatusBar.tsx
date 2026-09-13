import React, { useState, useEffect } from 'react';
import { Wifi, BatteryMedium, ShieldCheck, Signal } from 'lucide-react';
import { ThemeMode } from '../types';

interface MobileStatusBarProps {
  theme: ThemeMode;
}

export const MobileStatusBar: React.FC<MobileStatusBarProps> = ({ theme }) => {
  const [time, setTime] = useState('11:42');
  const isDark = theme === 'dark';
  const isTiranga = !isDark;

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      setTime(`${hours}:${minutes}`);
    };
    updateTime();
    const interval = setInterval(updateTime, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`px-5 pt-2 pb-1.5 flex items-center justify-between text-[11px] font-semibold tracking-tight select-none border-b ${
        isDark
          ? 'bg-[#06080E] border-slate-800/60 text-slate-300'
          : 'bg-white border-[#FF671F]/20 text-slate-800'
      }`}
    >
      {/* Left: Current Time and Indian 5G Network */}
      <div className="flex items-center gap-1.5">
        <span className="font-bold tracking-tight">{time}</span>
        <span className="text-[10px] text-slate-400 flex items-center gap-0.5">
          <span className="font-mono">Jio True 5G</span>
        </span>
      </div>

      {/* Middle: Subtle Front Camera Cutout in Phone Frame */}
      <div className="hidden sm:flex items-center justify-center">
        <div className="w-3.5 h-3.5 rounded-full bg-black/90 ring-1 ring-slate-700/50 flex items-center justify-center">
          <div className="w-1.5 h-1.5 rounded-full bg-slate-900 ring-1 ring-blue-500/20" />
        </div>
      </div>

      {/* Right: Network status, Vo5G, Battery */}
      <div className="flex items-center gap-2">
        <span className="font-mono text-[10px] font-bold text-amber-500">5G</span>
        <Signal className="w-3 h-3" />
        <Wifi className="w-3 h-3" />
        <div className="flex items-center gap-0.5 font-mono text-[10px]">
          <span>98%</span>
          <BatteryMedium className="w-3.5 h-3.5" />
        </div>
      </div>
    </div>
  );
};
