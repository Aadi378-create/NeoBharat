export type Language = 'en' | 'hi';
export type ThemeMode = 'light' | 'dark';
export type ActiveTab = 'dashboard' | 'sakhi' | 'stress-guard' | 'passbook';

export type PersonaId = 'ramesh' | 'priya' | 'sunil';

export interface PersonaProfile {
  id: PersonaId;
  name: string;
  hindiName: string;
  avatarInitials: string;
  phone?: string;
  bankName?: string;
  occupation: string;
  hindiOccupation: string;
  location: string;
  hindiLocation: string;
  accountNumber: string;
  upiId: string;
  monthlyIncome: number;
  monthlyExpense: number;
  accountBalance: number;
  creditHealthScore: number; // 0-100
  lifeStageSignal: string;
  hindiLifeStageSignal: string;
  primaryNeed: string;
  hindiPrimaryNeed: string;
  recommendedProduct: HyperPersonalizedProduct;
  recentTransactions: AccountTransaction[];
}

export interface FrequentPayee {
  id: string;
  name: string;
  shortName: string;
  category: 'Supplier' | 'Utility' | 'Family' | 'Test Scam';
  emoji: string;
  vpa: string;
  phone?: string;
  defaultAmount?: number;
  isScam?: boolean;
  scamDetails?: {
    riskLevel: 'HIGH' | 'CRITICAL';
    flaggedCount: number;
    reason: string;
    hindiReason: string;
  };
}

export interface HyperPersonalizedProduct {
  id: string;
  productType: 'working_capital' | 'micro_equipment' | 'kisan_credit';
  title: string;
  hindiTitle: string;
  categoryBadge: string;
  hindiCategoryBadge: string;
  amountOrCover: string;
  tenure: string;
  hindiTenure: string;
  rateOrCost: string;
  hindiRateOrCost: string;
  monthlyCommitment: string;
  whyRecommended: {
    dataPointsAnalyzed: string[];
    hindiDataPointsAnalyzed: string[];
    aiTriggerSummary: string;
    hindiAiTriggerSummary: string;
    confidenceScore: number;
  };
  keyFactsStatement: {
    apr: string;
    processingFee: string;
    prepaymentPenalty: string;
    disbursalTime: string;
    rbiDirectUrl: string;
  };
}

export interface AccountTransaction {
  id: string;
  date: string;
  title: string;
  hindiTitle: string;
  amount: number;
  type: 'credit' | 'debit';
  category: string;
  insightTag?: string;
  hindiInsightTag?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'sakhi';
  text: string;
  hindiText?: string;
  timestamp: string;
  suggestedActions?: { label: string; hindiLabel: string; actionId: string }[];
  audioText?: string;
  stepCard?: {
    stepNumber: number;
    title: string;
    hindiTitle: string;
    details: string;
    hindiDetails: string;
    status: 'completed' | 'in_progress' | 'upcoming';
  };
}
