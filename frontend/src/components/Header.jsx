import React from 'react';
import { ShieldIcon, UserIcon } from './Icons';

export function Header({ customers, selectedCustomerId, onSelectCustomer, loading }) {
  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-icon">
          <ShieldIcon className="w-6 h-6" />
        </div>
        <div className="brand-title-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <h1 className="brand-title">
              NEO<span className="gradient-text">BHARAT</span>
            </h1>
            <span className="hackout-badge">HackOut'26 • DAIICT</span>
          </div>
          <p className="brand-tagline">
            Your bank that understands you, not just your transactions.
          </p>
        </div>
      </div>

      <div className="customer-selector" role="group" aria-label="Customer Persona Switcher">
        <span className="customer-selector-label">Customer Persona</span>
        {loading && !customers.length ? (
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', padding: '0 0.5rem' }}>
            Loading...
          </span>
        ) : (
          customers.map((c) => {
            const isActive = c.id === selectedCustomerId;
            return (
              <button
                key={c.id}
                type="button"
                className={`customer-tab ${isActive ? 'active' : ''}`}
                onClick={() => onSelectCustomer(c.id)}
                aria-pressed={isActive}
              >
                <UserIcon className="w-3.5 h-3.5" />
                <span>{c.name}</span>
                <span className="customer-pill">ID {c.id}</span>
              </button>
            );
          })
        )}
      </div>
    </header>
  );
}
