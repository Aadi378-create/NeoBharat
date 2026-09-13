import { PersonaProfile, AccountTransaction, HyperPersonalizedProduct } from '../types';
import { getCustomer, getProfile, getGuardian, getRecommendation, getTransactions } from './api';

export async function fetchDashboardData(customerId: number | string) {
  const [customer, profile, guardian, recommendation, transactions] = await Promise.all([
    getCustomer(customerId),
    getProfile(customerId),
    getGuardian(customerId),
    getRecommendation(customerId),
    getTransactions(customerId)
  ]);
  return { customer, profile, guardian, recommendation, transactions };
}

export function toPersona(backendData: any): PersonaProfile {
  const { customer, profile, guardian, recommendation, transactions } = backendData;
  const isHindi = false;

  const decision = recommendation?.decision || 'SUPPORT';
  const surplus = profile?.estimated_savings || 0;
  
  // Mapping product based on decision
  let product: HyperPersonalizedProduct = {
    id: 'product-null',
    productType: 'working_capital',
    title: 'Financial Review',
    hindiTitle: 'वित्तीय समीक्षा',
    categoryBadge: decision,
    hindiCategoryBadge: decision,
    amountOrCover: '',
    tenure: '',
    hindiTenure: '',
    rateOrCost: '',
    hindiRateOrCost: '',
    monthlyCommitment: '',
    whyRecommended: {
      dataPointsAnalyzed: [],
      hindiDataPointsAnalyzed: [],
      aiTriggerSummary: '',
      hindiAiTriggerSummary: '',
      confidenceScore: 100,
    },
    keyFactsStatement: {
      apr: '',
      processingFee: '',
      prepaymentPenalty: '',
      disbursalTime: '',
      rbiDirectUrl: 'https://www.rbi.org.in/',
    }
  };

  if (decision === 'RECOMMEND') {
    product = {
      ...product,
      id: 'sip-offer',
      productType: 'working_capital',
      title: 'Micro-SIP Wealth Builder',
      hindiTitle: 'माइक्रो-एसआईपी',
      categoryBadge: 'RECOMMENDED',
      hindiCategoryBadge: 'सुझाया गया',
      amountOrCover: '₹500',
      tenure: '12 Months',
      hindiTenure: '12 महीने',
      rateOrCost: 'No fees',
      hindiRateOrCost: 'कोई शुल्क नहीं',
      monthlyCommitment: '₹500/month',
      whyRecommended: {
        dataPointsAnalyzed: ['High savings surplus', 'Zero debt'],
        hindiDataPointsAnalyzed: ['उच्च बचत अधिशेष', 'शून्य ऋण'],
        aiTriggerSummary: 'High savings surplus & zero debt detected',
        hindiAiTriggerSummary: 'उच्च बचत अधिशेष और शून्य ऋण का पता चला',
        confidenceScore: 98,
      },
    };
  } else if (decision === 'SUPPORT') {
    product = {
      ...product,
      id: 'support-offer',
      productType: 'working_capital',
      title: 'Debt Relief Support',
      hindiTitle: 'ऋण राहत सहायता',
      categoryBadge: 'SUPPORT',
      hindiCategoryBadge: 'सहायता',
      amountOrCover: 'Review EMI',
      tenure: '30 min',
      hindiTenure: '30 मिनट',
      rateOrCost: 'Free',
      hindiRateOrCost: 'निःशुल्क',
      monthlyCommitment: 'Flexible',
      whyRecommended: {
        dataPointsAnalyzed: ['High EMI burden', 'Low savings'],
        hindiDataPointsAnalyzed: ['उच्च ईएमआई बोझ', 'कम बचत'],
        aiTriggerSummary: 'Help manage current EMI commitments',
        hindiAiTriggerSummary: 'वर्तमान ईएमआई को प्रबंधित करने में मदद',
        confidenceScore: 95,
      },
    };
  } else if (decision === 'VERIFY') {
    product = {
      ...product,
      id: 'verify-offer',
      productType: 'working_capital',
      title: 'Security Verification',
      hindiTitle: 'सुरक्षा सत्यापन',
      categoryBadge: 'VERIFY',
      hindiCategoryBadge: 'सत्यापन',
      amountOrCover: 'Action Required',
      tenure: 'Urgent',
      hindiTenure: 'ज़रूरी',
      rateOrCost: 'Free',
      hindiRateOrCost: 'निःशुल्क',
      monthlyCommitment: 'None',
      whyRecommended: {
        dataPointsAnalyzed: ['Anomalous transaction', 'Location mismatch'],
        hindiDataPointsAnalyzed: ['संदिग्ध लेन-देन', 'स्थान बेमेल'],
        aiTriggerSummary: 'Anomalous transaction detected',
        hindiAiTriggerSummary: 'संदिग्ध लेन-देन का पता चला',
        confidenceScore: 99,
      },
    };
  }

  const mappedTxns: AccountTransaction[] = (transactions || []).map((t: any, i: number) => ({
    id: `tx-${t.id || i}`,
    title: t.merchant || 'UPI Transfer',
    hindiTitle: t.merchant || 'यूपीआई ट्रांसफर',
    date: t.timestamp ? new Date(t.timestamp).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }) : 'Recent',
    amount: Number(t.amount),
    type: t.type === 'CREDIT' ? 'credit' : 'debit',
    category: t.category,
    isFlagged: Boolean(t.is_flagged || (t.amount >= 50000 && t.type === 'DEBIT')),
  }));

  const name = customer?.name || `Customer ${customer?.id}`;
  const firstInitial = name.charAt(0).toUpperCase();

  return {
    id: customer?.id?.toString() as any, // Cast to any to bypass PersonaId literal typing
    name: name,
    hindiName: name, // We could map if needed
    avatarInitials: firstInitial,
    phone: customer?.phone || '+91 98XXX XXXXX',
    bankName: 'Bharat State Bank',
    occupation: 'Citizen',
    hindiOccupation: 'नागरिक',
    location: 'India',
    hindiLocation: 'भारत',
    accountNumber: `XXXX-${customer?.id?.toString().padStart(4, '0')}`,
    upiId: `${name.toLowerCase().replace(/\s/g, '')}@bharat`,
    monthlyIncome: profile?.income ?? customer?.monthly_income ?? 0,
    monthlyExpense: profile?.monthly_spending ?? 0,
    accountBalance: profile?.estimated_savings ?? 0,
    creditHealthScore: guardian?.scores?.financial_health_score ?? guardian?.scores?.financial_stress_score ?? 0,
    lifeStageSignal: `Guardian: ${guardian?.status || 'Unknown'}`,
    hindiLifeStageSignal: `गार्जियन: ${guardian?.status || 'अज्ञात'}`,
    primaryNeed: `Decision: ${decision}`,
    hindiPrimaryNeed: `निर्णय: ${decision}`,
    recommendedProduct: product,
    recentTransactions: mappedTxns,
  };
}
