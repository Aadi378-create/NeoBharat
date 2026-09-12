import React from 'react';
import { CheckCircleIcon, AlertTriangleIcon, InfoIcon, LockIcon, AlertCircleIcon } from './Icons';

export function DecisionCard({ recommendationData, loading, error }) {
  if (loading) {
    return (
      <div className="card">
        <div className="loading-indicator">
          <div className="spinner" />
          <span>Evaluating recommendation & credit safety gates...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
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

  const getBadge = () => {
    switch (decision) {
      case 'SUPPORT':
        return <span className="badge badge-support">SUPPORT OUTCOME</span>;
      case 'RECOMMEND':
        return <span className="badge badge-recommend">RECOMMENDATION READY</span>;
      case 'VERIFY':
        return <span className="badge badge-verify">VERIFICATION REQUIRED</span>;
      default:
        return <span className="badge">{decision}</span>;
    }
  };

  const getPhilosophyBanner = () => {
    if (decision === 'SUPPORT') {
      return (
        <div className="philosophy-banner SUPPORT">
          <CheckCircleIcon className="w-5 h-5" />
          <span>NeoBharat chose support over selling. Commercial credit is locked to protect customer health.</span>
        </div>
      );
    }
    if (decision === 'RECOMMEND') {
      return (
        <div className="philosophy-banner RECOMMEND">
          <InfoIcon className="w-5 h-5" />
          <span>Pre-evaluated for long-term wealth building based on verified surplus.</span>
        </div>
      );
    }
    if (decision === 'VERIFY') {
      return (
        <div className="philosophy-banner VERIFY">
          <AlertTriangleIcon className="w-5 h-5" />
          <span>Unusual activity detected — verify before taking action. No commercial products offered.</span>
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
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <h2 id="decision-card-title" className="card-title">Decision & Recommendations</h2>
              {getBadge()}
            </div>
            <p className="card-subtitle">Authoritative determination produced exclusively by deterministic engine</p>
          </div>
        </div>

        {consumer_protection_metadata.predatory_lending_blocked && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.75rem', color: '#b91c1c', fontWeight: 600 }}>
            <LockIcon className="w-3.5 h-3.5" />
            <span>Predatory Lending Blocked</span>
          </div>
        )}
      </div>

      {getPhilosophyBanner()}

      <div className="decision-details-box">
        <div className="decision-action-title">
          Action: {recommendation.action ? recommendation.action.replace(/_/g, ' ') : 'None'}
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
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '0.375rem', fontStyle: 'italic' }}>
                {recommendation.risk_disclosure}
              </div>
            )}
          </div>
        )}

        {/* Supportive Guidance (if present, e.g. Rahul / Arjun) */}
        {recommendation.supportive_guidance && (
          <div className="product-box" style={{ background: '#f8fafc', borderColor: '#cbd5e1' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
              Supportive Intervention: {recommendation.supportive_guidance.action?.replace(/_/g, ' ')}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Priority: {recommendation.supportive_guidance.priority}
            </div>
          </div>
        )}
      </div>

      {/* Policy Reasons Audit Trail */}
      {Array.isArray(policy_reasons) && policy_reasons.length > 0 && (
        <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border)' }}>
          <span style={{ fontSize: '0.6875rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            Policy Rules Triggered ({policy_reasons.length})
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem', marginTop: '0.375rem' }}>
            {policy_reasons.map((p, idx) => (
              <div key={idx} style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                • <strong>{p.code}:</strong> {p.description}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
