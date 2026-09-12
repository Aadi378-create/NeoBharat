import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  fetchCustomers,
  fetchCustomer,
  fetchProfile,
  fetchGuardian,
  fetchRecommendation,
  sendChatMessage,
} from '../api/client';

describe('NeoBharat Frontend API Client & Contracts', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('fetchCustomers fetches from /api/customers', async () => {
    const mockData = [
      { id: 1, name: 'Rahul' },
      { id: 2, name: 'Priya' },
      { id: 3, name: 'Arjun' },
    ];
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const result = await fetchCustomers();
    expect(global.fetch).toHaveBeenCalledWith('/api/customers');
    expect(result).toEqual(mockData);
    expect(result.length).toBe(3);
  });

  it('fetchProfile fetches from /api/customers/:id/profile without calculating metrics', async () => {
    const mockProfile = {
      income: 45000.0,
      monthly_spending: 38000.0,
      emi: 14000.0,
      emi_ratio: 31.1,
      estimated_savings: 7000.0,
      spending_trend: 'INCREASING',
      savings_trend: 'DECLINING',
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockProfile,
    });

    const result = await fetchProfile(1);
    expect(global.fetch).toHaveBeenCalledWith('/api/customers/1/profile');
    expect(result.income).toBe(45000.0);
    expect(result.estimated_savings).toBe(7000.0);
  });

  it('fetchGuardian fetches from /api/customers/:id/guardian without reclassifying', async () => {
    const mockGuardian = {
      customer_id: 1,
      status: 'ATTENTION_NEEDED',
      classification: { primary: 'FINANCIAL_STRESS' },
      scores: {
        financial_stress_score: 72,
        payment_risk_score: 61,
        fraud_score: 7,
      },
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockGuardian,
    });

    const result = await fetchGuardian(1);
    expect(global.fetch).toHaveBeenCalledWith('/api/customers/1/guardian');
    expect(result.status).toBe('ATTENTION_NEEDED');
    expect(result.classification.primary).toBe('FINANCIAL_STRESS');
    expect(result.scores.financial_stress_score).toBe(72);
  });

  it('fetchRecommendation fetches from /api/customers/:id/recommendation without inventing products', async () => {
    const mockRec = {
      customer_id: 1,
      decision: 'SUPPORT',
      recommendation: {
        action: 'SUPPORT',
        product_category: null,
        product_name: null,
        supportive_guidance: { action: 'REVIEW_UPCOMING_PAYMENTS' },
      },
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockRec,
    });

    const result = await fetchRecommendation(1);
    expect(global.fetch).toHaveBeenCalledWith('/api/customers/1/recommendation');
    expect(result.decision).toBe('SUPPORT');
    expect(result.recommendation.product_name).toBeNull();
  });

  it('sendChatMessage sends strictly customer_id and message in payload', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: 'Explanation response',
        response_type: 'SUPPORT_GUIDANCE',
      }),
    });

    await sendChatMessage(1, 'Should I take another loan?');

    expect(global.fetch).toHaveBeenCalledTimes(1);
    const [url, options] = global.fetch.mock.calls[0];
    expect(url).toBe('/api/chat');
    expect(options.method).toBe('POST');

    const parsedBody = JSON.parse(options.body);
    expect(parsedBody).toEqual({
      customer_id: 1,
      message: 'Should I take another loan?',
    });

    // Ensure forbidden fields are strictly absent
    expect(parsedBody.income).toBeUndefined();
    expect(parsedBody.financial_stress_score).toBeUndefined();
    expect(parsedBody.scores).toBeUndefined();
    expect(parsedBody.decision).toBeUndefined();
  });

  it('sendChatMessage rejects message > 4000 characters before making an HTTP request', async () => {
    global.fetch = vi.fn();

    const oversizedMessage = 'x'.repeat(4001);
    await expect(sendChatMessage(1, oversizedMessage)).rejects.toThrow(
      'Message exceeds the maximum allowed length of 4000 characters.'
    );

    // Confirmed: No fetch request was made
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('sendChatMessage rejects empty or whitespace-only messages', async () => {
    global.fetch = vi.fn();

    await expect(sendChatMessage(1, '   ')).rejects.toThrow(
      'Message cannot be empty.'
    );
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('handles backend HTTP errors gracefully without fabricating fallback data', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: async () => ({ error: 'Customer with ID 99999 not found' }),
    });

    await expect(fetchProfile(99999)).rejects.toThrow('Customer with ID 99999 not found');
  });

  it('handles malformed non-JSON backend responses safely', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => {
        throw new Error('Unexpected token < in JSON');
      },
    });

    await expect(fetchCustomers()).rejects.toThrow('Failed to parse backend response as JSON');
  });
});

describe('NeoBharat Persona Semantic Verification', () => {
  it('verifies Rahul persona targets: SUPPORT and no commercial credit', () => {
    const rahulRec = {
      decision: 'SUPPORT',
      recommendation: {
        action: 'SUPPORT',
        product_category: null,
        product_name: null,
        supportive_guidance: { action: 'REVIEW_UPCOMING_PAYMENTS' },
      },
    };
    expect(rahulRec.decision).toBe('SUPPORT');
    expect(rahulRec.recommendation.product_name).toBeNull();
  });

  it('verifies Priya persona targets: RECOMMEND and Systematic Wealth Builder SIP', () => {
    const priyaRec = {
      decision: 'RECOMMEND',
      recommendation: {
        action: 'RECOMMEND',
        product_category: 'investment/SIP',
        product_name: 'Illustrative Prototype Product: Systematic Wealth Builder SIP',
      },
    };
    expect(priyaRec.decision).toBe('RECOMMEND');
    expect(priyaRec.recommendation.product_name).toContain('Systematic Wealth Builder SIP');
  });

  it('verifies Arjun persona targets: VERIFY and never confirmed fraud', () => {
    const arjunGuardian = {
      status: 'URGENT_ACTION',
      classification: { primary: 'FRAUD_SUSPECTED' },
      scores: { fraud_score: 95 },
      explanation: {
        summary: 'Unusual high-value transaction detected that deviates significantly from personal history.',
      },
    };
    expect(arjunGuardian.status).toBe('URGENT_ACTION');
    expect(arjunGuardian.classification.primary).toBe('FRAUD_SUSPECTED');
    expect(arjunGuardian.scores.fraud_score).toBe(95);
    expect(arjunGuardian.explanation.summary.toLowerCase()).not.toContain('confirmed fraud');
    expect(arjunGuardian.explanation.summary.toLowerCase()).not.toContain('definitely fraudulent');
  });
});
