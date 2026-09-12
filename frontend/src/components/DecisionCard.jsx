import React from 'react';
import { CheckCircleIcon, AlertTriangleIcon, InfoIcon, LockIcon, AlertCircleIcon, ShieldIcon } from './Icons';

export function DecisionCard({ recommendationData, loading, error }) {
  if (loading) {
    return (
      <div className="card decision-card">
        <div className="loading-indicator">
          <div className="spinner" />
          <span>Evaluating recommendation & credit safety gates...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card decision-card">
        <div className="error-banner">
          <AlertCircleIcon className="w-5 h-5" />
          <span>Failed to load recommendation: {error}</span>
        </div>
      </div>
    );
  }

  if (!recommendationData) {
    return null;
  }

  const { decision, recommendation = {}, policy_reasons = [], consumer_protection_metadata = {} } = recommendationData;

  const getDecisionBadge = () => {
    switch (decision) {
      case 'SUPPORT':
        return (
          <span className="badge badge-support" style={{ fontSize: '0.8125rem', padding: '0.35rem 0.875rem' }}>
            <ShieldIcon className="w-4 h-4" />
            <span>DECISION: SUPPORT</span>
          </span>
        );
      case 'RECOMMEND':
        return (
          <span className="badge badge-recommend" style={{ fontSize: '0.8125rem', padding: '0.35rem 0.875rem' }}>
            <CheckCircleIcon className="w-4 h-4" />
            <span>DECISION: RECOMMEND</span>
          </span>
        );
      case 'VERIFY':
        return (
          <span className="badge badge-verify" style={{ fontSize: '0.8125rem', padding: '0.35rem 0.875rem' }}>
            <AlertTriangleIcon className="w-4 h-4" />
            <span>DECISION: VERIFY</span>
          </span>
        );
      default:
        return <span className="badge">{decision}</span>;
    }
  };

  const getPhilosophyBanner = () => {
    if (decision === 'SUPPORT') {
      return (
        <div className="philosophy-banner SUPPORT">
          <ShieldIcon className="w-5 h-5" style={{ color: 'var(--accent-orange)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div style={{ fontSize: '0.9375rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '0.2rem' }}>
              AI That Chooses NOT to Sell — <strong>NeoBharat Chose Support Over Selling</strong>
            </div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
              Customer exhibits financial stress indicators. Commercial loan offers are locked to prioritize budgeting and payment resilience.
            </div>
          </div>
        </div>
      );
    }
    if (decision === 'RECOMMEND') {
      return (
        <div className="philosophy-banner RECOMMEND">
          <InfoIcon className="w-5 h-5" style={{ color: 'var(--accent-green)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div style={{ fontSize: '0.9375rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '0.2rem' }}>
              Disciplined Surplus Opportunity — <strong>Personalized Wealth Building</strong>
            </div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
              Verified monthly savings surplus qualifies customer for disciplined long-term wealth accumulation.
            </div>
          </div>
        </div>
      );
    }
    if (decision === 'VERIFY') {
      return (
        <div className="philosophy-banner VERIFY">
          <AlertTriangleIcon className="w-5 h-5" style={{ color: 'var(--accent-red)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div style={{ fontSize: '0.9375rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '0.2rem' }}>
              Proactive Safety Barrier — <strong>Unusual Activity Detected</strong>
            </div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
              Unusual transaction activity detected compared with historical baseline. Verify transaction with customer before taking action.
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <section className={`card decision-card ${decision}`} aria-labelledby="decision-card-title">
      <div className="card-header">
        <div className="card-title-group">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <h2 id="decision-card-title" className="card-title" style={{ fontSize: '1.375rem' }}>
                Decision & Recommendation Engine
              </h2>
              {getDecisionBadge()}
            </div>
            <p className="card-subtitle">
              Phase 3 Deterministic Engine determination • Governed by safety gates & affordability
            </p>
          </div>
        </div>

        {consumer_protection_metadata.predatory_lending_blocked && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.35rem 0.75rem',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(255, 104, 104, 0.15)',
            border: '1px solid rgba(255, 104, 104, 0.4)',
            fontSize: '0.75rem',
            color: 'var(--accent-red)',
            fontWeight: 700,
          }}>
            <LockIcon className="w-3.5 h-3.5" />
            <span>Predatory Lending Blocked</span>
          </div>
        )}
      </div>

      {getPhilosophyBanner()}

      <div className="decision-details-box">
        <div className="decision-action-title">
          <span>Action:</span>
          <span style={{ color: decision === 'SUPPORT' ? 'var(--accent-orange)' : decision === 'RECOMMEND' ? 'var(--accent-green)' : 'var(--accent-red)' }}>
            {recommendation.action ? recommendation.action.replace(/_/g, ' ') : 'None'}
          </span>
        </div>

        {recommendation.suitability_rationale && (
          <p className="decision-rationale">
            {recommendation.suitability_rationale}
          </p>
        )}

        {/* Product Box (if product exists, e.g. Priya) */}
        {recommendation.product_name && (
          <div className="product-box">
            <div className="product-box-title">{recommendation.product_name}</div>
            {recommendation.illustrative_terms && (
              <div className="product-box-terms">{recommendation.illustrative_terms}</div>
            )}
            {recommendation.risk_disclosure && (
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '0.5rem', fontStyle: 'italic' }}>
                {recommendation.risk_disclosure}
              </div>
            )}
          </div>
        )}

        {/* Supportive Guidance (if present, e.g. Rahul / Arjun) */}
        {recommendation.supportive_guidance && (
          <div className="product-box" style={{ background: 'rgba(7, 13, 27, 0.6)', borderColor: 'rgba(255, 255, 255, 0.1)' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)' }}>
              Supportive Intervention: <span style={{ color: '#FFFFFF' }}>{recommendation.supportive_guidance.action?.replace(/_/g, ' ')}</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Priority: <strong style={{ color: 'var(--accent-orange)' }}>{recommendation.supportive_guidance.priority}</strong>
            </div>
          </div>
        )}
      </div>

      {/* Policy Reasons Audit Trail */}
      {Array.isArray(policy_reasons) && policy_reasons.length > 0 && (
        <div style={{ marginTop: '1.25rem', paddingTop: '0.875rem', borderTop: '1px solid var(--border-subtle)' }}>
          <span style={{ fontSize: '0.6875rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>
            Safety Gate Rules Triggered ({policy_reasons.length})
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem', marginTop: '0.4rem' }}>
            {policy_reasons.map((p, idx) => (
              <div key={idx} style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                • <strong style={{ color: '#FFFFFF' }}>{p.code}:</strong> {p.description}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
