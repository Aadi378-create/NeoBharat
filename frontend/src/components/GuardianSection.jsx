import React from 'react';
import { ShieldIcon, AlertTriangleIcon, CheckCircleIcon, AlertCircleIcon } from './Icons';

export function GuardianSection({ guardian, loading, error }) {
  if (loading) {
    return (
      <div className="card">
        <div className="loading-indicator">
          <div className="spinner" />
          <span>Evaluating Guardian protection layers...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error-banner">
          <AlertCircleIcon className="w-5 h-5" />
          <span>Failed to load Guardian status: {error}</span>
        </div>
      </div>
    );
  }

  if (!guardian) {
    return null;
  }

  const { status, classification, scores = {}, explanation = {}, recommended_intervention = {} } = guardian;

  const getStatusBadge = () => {
    switch (status) {
      case 'NO_ACTION':
        return (
          <span className="badge badge-healthy">
            <CheckCircleIcon className="w-3.5 h-3.5" />
            <span>NO ACTION NEEDED</span>
          </span>
        );
      case 'ATTENTION_NEEDED':
        return (
          <span className="badge badge-attention">
            <AlertTriangleIcon className="w-3.5 h-3.5" />
            <span>ATTENTION NEEDED</span>
          </span>
        );
      case 'URGENT_ACTION':
        return (
          <span className="badge badge-urgent">
            <AlertTriangleIcon className="w-3.5 h-3.5" />
            <span>URGENT ACTION</span>
          </span>
        );
      default:
        return <span className="badge">{status}</span>;
    }
  };

  const getHeroClass = () => {
    if (status === 'NO_ACTION') return 'healthy';
    if (status === 'ATTENTION_NEEDED') return 'attention';
    if (status === 'URGENT_ACTION') return 'urgent';
    return '';
  };

  const primaryClassification = classification?.primary || 'UNKNOWN';

  return (
    <section className={`card guardian-hero ${getHeroClass()}`} aria-labelledby="guardian-section-title">
      <div className="card-header">
        <div className="card-title-group">
          <div className="brand-icon" style={{ width: 40, height: 40, background: 'rgba(2, 132, 199, 0.2)', border: '1px solid rgba(82, 151, 255, 0.4)' }}>
            <ShieldIcon className="w-5 h-5" style={{ color: 'var(--accent-blue)' }} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', flexWrap: 'wrap' }}>
              <h2 id="guardian-section-title" className="card-title">Financial Guardian</h2>
              {getStatusBadge()}
            </div>
            <p className="card-subtitle">Watching for changes that may need your attention.</p>
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '0.6875rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>
            Primary Classification
          </span>
          <div style={{ fontSize: '0.9375rem', fontWeight: 800, color: '#FFFFFF', marginTop: '0.125rem' }}>
            {primaryClassification.replace(/_/g, ' ')}
          </div>
        </div>
      </div>

      {/* 4 Deterministic Guardian Scores */}
      <div className="guardian-scores-grid">
        <div className="score-card">
          <div className="score-num" style={{ color: scores.financial_stress_score >= 60 ? 'var(--accent-orange)' : 'var(--text-primary)' }}>
            {scores.financial_stress_score ?? '—'}
          </div>
          <div className="score-name">Financial Stress</div>
        </div>

        <div className="score-card">
          <div className="score-num" style={{ color: scores.payment_risk_score >= 60 ? 'var(--accent-orange)' : 'var(--text-primary)' }}>
            {scores.payment_risk_score ?? '—'}
          </div>
          <div className="score-name">Payment Risk</div>
        </div>

        <div className="score-card">
          <div className="score-num" style={{ color: scores.fraud_score >= 65 ? 'var(--accent-red)' : 'var(--text-primary)' }}>
            {scores.fraud_score ?? '—'}
          </div>
          <div className="score-name">Fraud / Anomaly</div>
        </div>

        <div className="score-card">
          <div className="score-num" style={{ color: scores.behaviour_change_score >= 60 ? 'var(--accent-gold)' : 'var(--text-primary)' }}>
            {scores.behaviour_change_score ?? '—'}
          </div>
          <div className="score-name">Behaviour Shift</div>
        </div>
      </div>

      {/* Recommended Intervention */}
      {recommended_intervention?.action && recommended_intervention.action !== 'NONE' && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.625rem',
          padding: '0.625rem 0.875rem',
          background: 'rgba(16, 29, 51, 0.8)',
          border: '1px solid var(--border-card)',
          borderRadius: 'var(--radius-sm)',
          margin: '0.75rem 0',
          fontSize: '0.8125rem'
        }}>
          <span style={{ fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
            Recommended Intervention:
          </span>
          <span style={{ fontWeight: 700, color: 'var(--accent-orange)' }}>
            {recommended_intervention.action.replace(/_/g, ' ')}
          </span>
        </div>
      )}

      {/* Guardian Explanation & Factors */}
      {explanation && (
        <div className="guardian-explanation">
          {explanation.summary && (
            <p className="guardian-summary">{explanation.summary}</p>
          )}

          {Array.isArray(explanation.factors) && explanation.factors.length > 0 && (
            <div className="factors-list">
              {explanation.factors.map((f, idx) => (
                <span
                  key={idx}
                  className={`factor-tag ${f.impact === 'NEGATIVE' ? 'negative' : 'neutral'}`}
                >
                  <strong style={{ color: '#FFFFFF' }}>{f.factor}:</strong> {f.value}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
