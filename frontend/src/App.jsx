import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { FinancialOverview } from './components/FinancialOverview';
import { GuardianSection } from './components/GuardianSection';
import { DecisionCard } from './components/DecisionCard';
import { ChatPanel } from './components/ChatPanel';
import { ShieldIcon } from './components/Icons';
import {
  fetchCustomers,
  fetchProfile,
  fetchGuardian,
  fetchRecommendation,
} from './api/client';

export function App() {
  const [customers, setCustomers] = useState([]);
  const [customersLoading, setCustomersLoading] = useState(true);
  const [customersError, setCustomersError] = useState(null);

  const [selectedCustomerId, setSelectedCustomerId] = useState(1);

  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileError, setProfileError] = useState(null);

  const [guardian, setGuardian] = useState(null);
  const [guardianLoading, setGuardianLoading] = useState(true);
  const [guardianError, setGuardianError] = useState(null);

  const [recommendation, setRecommendation] = useState(null);
  const [recommendationLoading, setRecommendationLoading] = useState(true);
  const [recommendationError, setRecommendationError] = useState(null);

  // Track current customer fetch sequence to avoid race conditions
  const currentFetchIdRef = useRef(0);

  // 1. Fetch available customers once on mount
  useEffect(() => {
    let isMounted = true;
    async function loadCustomers() {
      try {
        setCustomersLoading(true);
        setCustomersError(null);
        const data = await fetchCustomers();
        if (isMounted) {
          setCustomers(data);
          if (data && data.length > 0) {
            setSelectedCustomerId(data[0].id);
          }
        }
      } catch (err) {
        if (isMounted) {
          setCustomersError(err.message);
        }
      } finally {
        if (isMounted) {
          setCustomersLoading(false);
        }
      }
    }

    loadCustomers();
    return () => {
      isMounted = false;
    };
  }, []);

  // 2. Fetch customer-specific data when selectedCustomerId changes
  useEffect(() => {
    if (!selectedCustomerId) return;

    const fetchId = ++currentFetchIdRef.current;

    setProfileLoading(true);
    setProfileError(null);
    setGuardianLoading(true);
    setGuardianError(null);
    setRecommendationLoading(true);
    setRecommendationError(null);

    // Profile
    fetchProfile(selectedCustomerId)
      .then((data) => {
        if (fetchId === currentFetchIdRef.current) {
          setProfile(data);
          setProfileLoading(false);
        }
      })
      .catch((err) => {
        if (fetchId === currentFetchIdRef.current) {
          setProfileError(err.message);
          setProfileLoading(false);
        }
      });

    // Guardian
    fetchGuardian(selectedCustomerId)
      .then((data) => {
        if (fetchId === currentFetchIdRef.current) {
          setGuardian(data);
          setGuardianLoading(false);
        }
      })
      .catch((err) => {
        if (fetchId === currentFetchIdRef.current) {
          setGuardianError(err.message);
          setGuardianLoading(false);
        }
      });

    // Recommendation
    fetchRecommendation(selectedCustomerId)
      .then((data) => {
        if (fetchId === currentFetchIdRef.current) {
          setRecommendation(data);
          setRecommendationLoading(false);
        }
      })
      .catch((err) => {
        if (fetchId === currentFetchIdRef.current) {
          setRecommendationError(err.message);
          setRecommendationLoading(false);
        }
      });
  }, [selectedCustomerId]);

  const selectedCustomer = customers.find((c) => c.id === selectedCustomerId);

  return (
    <div className="app-container">
      <Header
        customers={customers}
        selectedCustomerId={selectedCustomerId}
        onSelectCustomer={(id) => setSelectedCustomerId(id)}
        loading={customersLoading}
      />

      {customersError && (
        <div className="error-banner" style={{ marginBottom: '1.75rem' }}>
          <span>Error loading customers: {customersError}</span>
        </div>
      )}

      <main className="dashboard-grid">
        {/* Top Hero Section: The Decision & Recommendation Engine Card */}
        <DecisionCard
          recommendationData={recommendation}
          loading={recommendationLoading}
          error={recommendationError}
        />

        {/* 2-Column Responsive Layout */}
        <div className="dashboard-main-columns">
          {/* Left Column: Guardian Protection Layer & Financial Overview */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {/* Financial Guardian Intelligence Layer */}
            <GuardianSection
              guardian={guardian}
              loading={guardianLoading}
              error={guardianError}
            />

            {/* Deterministic Financial Overview */}
            <FinancialOverview
              profile={profile}
              loading={profileLoading}
              error={profileError}
            />
          </div>

          {/* Right Column: Conversational AI Explanation Assistant */}
          <div>
            <ChatPanel
              key={selectedCustomerId} // Reset conversation when customer changes
              customerId={selectedCustomerId}
              customerName={selectedCustomer?.name}
            />
          </div>
        </div>
      </main>

      <footer className="safety-footer">
        <div className="safety-badge">
          <ShieldIcon className="w-3.5 h-3.5" style={{ color: 'var(--accent-green)' }} />
          <span>Responsible AI Banking Architecture</span>
        </div>
        <p>
          <strong>NeoBharat:</strong> Deterministic engines calculate & decide (Phase 1–3) •
          Safety gate validates semantics (Phase 4) • OpenAI explains (Phase 5) • Frontend displays (Phase 6).
        </p>
        <p style={{ marginTop: '0.35rem', color: 'var(--text-dim)' }}>
          Zero client-side financial calculations • No OpenAI API keys in browser • All decisions made server-side.
        </p>
      </footer>
    </div>
  );
}
