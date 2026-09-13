import React, { useState } from 'react';
import { Language, ThemeMode, PersonaProfile } from '../types';
import { translations } from '../data/translations';
import {
  ArrowDownLeft,
  ArrowUpRight,
  Search,
  ReceiptText,
  Tag
} from 'lucide-react';

interface TransactionsListProps {
  activePersona: PersonaProfile;
  lang: Language;
  theme: ThemeMode;
}

export const TransactionsList: React.FC<TransactionsListProps> = ({
  activePersona,
  lang,
  theme,
}) => {
  const t = translations[lang];
  const isDark = theme === 'dark';
  const isTiranga = !isDark;

  const [filterType, setFilterType] = useState<'all' | 'credit' | 'debit'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const txList = activePersona.recentTransactions;

  const filtered = txList.filter((tx) => {
    const matchesType = filterType === 'all' || tx.type === filterType;
    const matchesSearch =
      tx.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tx.hindiTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tx.category.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Top Cashflow Summary Card */}
      <div
        className={`p-4 rounded-2xl border transition-colors ${
          isTiranga
            ? 'bg-gradient-to-r from-[#FFF5EB] via-white to-[#F0FDF4] border-[#FF671F]/30 text-slate-900 shadow-sm border-t-2 border-t-[#FF671F]'
            : isDark
            ? 'bg-[#0E1526] border-slate-800 text-slate-100'
            : 'bg-white border-slate-200 text-slate-900 shadow-sm'
        }`}
      >
        <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
          <div>
            <h2
              className={`text-sm sm:text-base font-bold tracking-tight flex items-center gap-1.5 ${
                isDark ? 'text-white' : 'text-slate-950'
              }`}
            >
              <ReceiptText className="w-4 h-4 text-blue-500" />
              <span>{t.transactionsTitle}</span>
            </h2>
            <p
              className={`text-[11px] font-medium mt-0.5 ${
                isDark ? 'text-slate-400' : 'text-slate-500'
              }`}
            >
              {lang === 'en'
                ? `Account ${activePersona.accountNumber} · ${activePersona.name}`
                : `खाता ${activePersona.accountNumber} · ${activePersona.hindiName}`}
            </p>
          </div>

          <span
            className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
              isDark
                ? 'bg-blue-500/10 border-blue-500/30 text-blue-400'
                : 'bg-blue-50 border-blue-200 text-blue-800'
            }`}
          >
            A/C Verified
          </span>
        </div>

        {/* Monthly Summary */}
        <div className="grid grid-cols-2 gap-2.5 pt-3">
          <div
            className={`p-2.5 rounded-xl border ${
              isDark
                ? 'bg-slate-900/60 border-slate-800 text-slate-200'
                : 'bg-emerald-50/70 border-emerald-200 text-emerald-950'
            }`}
          >
            <span
              className={`text-[10px] font-bold block ${
                isDark ? 'text-emerald-400' : 'text-emerald-700'
              }`}
            >
              {t.monthlyInflow}
            </span>
            <span
              className={`text-base font-black font-mono mt-0.5 block ${
                isDark ? 'text-white' : 'text-slate-900'
              }`}
            >
              +₹{activePersona.monthlyIncome.toLocaleString('en-IN')}
            </span>
          </div>

          <div
            className={`p-2.5 rounded-xl border ${
              isDark
                ? 'bg-slate-900/60 border-slate-800 text-slate-200'
                : 'bg-blue-50/70 border-blue-200 text-blue-950'
            }`}
          >
            <span
              className={`text-[10px] font-bold block ${
                isDark ? 'text-blue-400' : 'text-blue-700'
              }`}
            >
              {t.monthlyOutflow}
            </span>
            <span
              className={`text-base font-black font-mono mt-0.5 block ${
                isDark ? 'text-white' : 'text-slate-900'
              }`}
            >
              -₹{activePersona.monthlyExpense.toLocaleString('en-IN')}
            </span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex items-center gap-2">
        <div
          className={`flex-1 h-9 flex items-center gap-2 px-3 rounded-xl border text-xs ${
            isDark
              ? 'bg-[#0E1526] border-slate-800 text-slate-200'
              : 'bg-white border-slate-300 text-slate-900 shadow-sm'
          }`}
        >
          <Search className="w-4 h-4 text-slate-400 shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={lang === 'en' ? 'Search transactions...' : 'लेन-देन खोजें...'}
            className="w-full bg-transparent outline-none placeholder:text-slate-500 text-xs"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex gap-1.5">
          {(['all', 'credit', 'debit'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`h-9 px-3 rounded-xl text-xs font-bold border transition-colors inline-flex items-center justify-center min-w-[54px] ${
                filterType === type
                  ? isTiranga
                    ? 'bg-[#FF671F] text-white border-[#FF671F] shadow-sm'
                    : 'bg-blue-600 text-white border-blue-600 shadow-sm'
                  : isDark
                  ? 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                  : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
              }`}
            >
              {type === 'all'
                ? lang === 'en' ? 'All' : 'सभी'
                : type === 'credit'
                ? lang === 'en' ? 'Credits' : 'आवक'
                : lang === 'en' ? 'Debits' : 'खर्च'}
            </button>
          ))}
        </div>
      </div>

      {/* Transaction Records List */}
      <div className="space-y-2">
        {filtered.map((tx) => (
          <div
            key={tx.id}
            className={`p-3 rounded-xl border transition-colors ${
              isDark
                ? 'bg-[#0E1526] border-slate-800 text-slate-100 hover:border-slate-700'
                : 'bg-white border-slate-200 text-slate-900 shadow-sm hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2.5">
                <div
                  className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs shrink-0 ${
                    tx.type === 'credit'
                      ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  {tx.type === 'credit' ? (
                    <ArrowDownLeft className="w-4 h-4" />
                  ) : (
                    <ArrowUpRight className="w-4 h-4" />
                  )}
                </div>
                <div>
                  <h4
                    className={`font-bold text-xs ${
                      isDark ? 'text-white' : 'text-slate-950'
                    }`}
                  >
                    {lang === 'en' ? tx.title : tx.hindiTitle}
                  </h4>
                  <div className="flex items-center gap-2 text-[10px] text-slate-500 mt-0.5">
                    <span>{tx.date}</span>
                    <span>•</span>
                    <span>{tx.category}</span>
                  </div>
                </div>
              </div>

              <div className="text-right">
                <span
                  className={`font-mono font-black text-xs sm:text-sm block ${
                    tx.type === 'credit'
                      ? 'text-emerald-600 dark:text-emerald-400'
                      : isDark
                      ? 'text-slate-200'
                      : 'text-slate-800'
                  }`}
                >
                  {tx.type === 'credit' ? '+' : '-'}₹{tx.amount.toLocaleString('en-IN')}
                </span>
                {tx.insightTag && (
                  <span
                    className={`inline-block text-[9px] font-semibold px-1.5 py-0.5 rounded border mt-0.5 ${
                      isDark
                        ? 'bg-slate-800 border-slate-700 text-slate-300'
                        : 'bg-slate-100 border-slate-200 text-slate-700'
                    }`}
                  >
                    {lang === 'en' ? tx.insightTag : tx.hindiInsightTag}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
