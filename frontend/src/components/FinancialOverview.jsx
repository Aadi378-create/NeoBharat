import React from 'react';
import { TrendingUpIcon, TrendingDownIcon, MinusIcon, AlertCircleIcon } from './Icons';

function formatCurrency(amount) {
  if (amount === undefined || amount === null) return '—';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

export function FinancialOverview({ profile, loading, error }) {
  if (loading) {
    return (
      <div className="card">
        <div className="loading-indicator">
          <div className="spinner" />
          <span>Loading financial profile metrics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error-banner">
          <AlertCircleIcon className="w-5 h-5" />
          <span>Failed to load financial profile: {error}</span>
        </div>
      </div>
    );
  }

  if (!profile) {
    return null;
  }

  const getTrendIcon = (trend) => {
    if (trend === 'INCREASING') return <TrendingUpIcon className="w-3.5 h-3.5" />;
    if (trend === 'DECLINING' || trend === 'DECREASING') return <TrendingDownIcon className="w-3.5 h-3.5" />;
    return <MinusIcon className="w-3.5 h-3.5" />;
  };

  const getTrendColor = (trend, isExpense = false) => {
    if (trend === 'INCREASING') return isExpense ? 'var(--accent-orange)' : 'var(--accent-green)';
    if (trend === 'DECLINING' || trend === 'DECREASING') return isExpense ? 'var(--accent-green)' : 'var(--accent-orange)';
    return 'var(--text-muted)';
  };

  const isNegativeSavings = typeof profile.estimated_savings === 'number' && profile.estimated_savings < 0;

  return (
    <section className="card" aria-labelledby="financial-overview-title">
      <div className="card-header">
        <div className="card-title-group">
          <div>
            <h2 id="financial-overview-title" className="card-title">Financial Overview</h2>
            <p className="card-subtitle">Deterministic metrics computed from verified transaction records</p>
          </div>
        </div>
      </div>

      <div className="metrics-grid">
        {/* Income */}
        <div className="metric-card">
          <span className="metric-label">Monthly Income</span>
          <span className="metric-value">{formatCurrency(profile.income)}</span>
          <span className="metric-sub" style={{ color: 'var(--text-muted)' }}>
            Verified salary credits
          </span>
        </div>

        {/* Monthly Spending */}
        <div className="metric-card">
          <span className="metric-label">Monthly Spending</span>
          <span className="metric-value">{formatCurrency(profile.monthly_spending)}</span>
          <span className="metric-sub" style={{ color: getTrendColor(profile.spending_trend, true) }}>
            {getTrendIcon(profile.spending_trend)}
            <span>
              {profile.spending_trend}
              {typeof profile.spending_change_pct === 'number' && profile.spending_change_pct !== 0
                ? ` (${profile.spending_change_pct > 0 ? '+' : ''}${profile.spending_change_pct.toFixed(1)}%)`
                : ''}
            </span>
          </span>
        </div>

        {/* Estimated Savings */}
        <div className="metric-card" style={isNegativeSavings ? { borderColor: 'rgba(255, 104, 104, 0.4)', background: 'rgba(255, 104, 104, 0.05)' } : {}}>
          <span className="metric-label">Estimated Savings</span>
          <span className="metric-value" style={{ color: isNegativeSavings ? 'var(--accent-red)' : 'var(--text-primary)' }}>
            {formatCurrency(profile.estimated_savings)}
          </span>
          <span className="metric-sub" style={{ color: getTrendColor(profile.savings_trend, false) }}>
            {getTrendIcon(profile.savings_trend)}
            <span>{profile.savings_trend} buffer</span>
          </span>
        </div>

        {/* Current EMI */}
        <div className="metric-card">
          <span className="metric-label">Monthly EMI</span>
          <span className="metric-value">{formatCurrency(profile.emi)}</span>
          <span className="metric-sub" style={{ color: 'var(--text-muted)' }}>
            Active loan obligations
          </span>
        </div>

        {/* EMI Ratio */}
        <div className="metric-card">
          <span className="metric-label">EMI Burden Ratio</span>
          <span className="metric-value">
            {profile.emi_ratio !== undefined ? `${profile.emi_ratio.toFixed(1)}%` : '—'}
          </span>
          <span className="metric-sub" style={{ color: profile.emi_ratio > 35 ? 'var(--accent-red)' : 'var(--accent-green)' }}>
            {profile.emi_ratio > 35 ? 'Above 35% threshold' : 'Within safe debt ceiling'}
          </span>
        </div>

        {/* Expense Breakdown */}
        <div className="metric-card">
          <span className="metric-label">Fixed vs Discretionary</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', marginTop: '0.25rem' }}>
            <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Fixed: {formatCurrency(profile.fixed_expenses)}
            </span>
            <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-muted)' }}>
              Discretionary: {formatCurrency(profile.discretionary_spending)}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
