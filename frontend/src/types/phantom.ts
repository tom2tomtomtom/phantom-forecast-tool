// Phantom types matching backend models

export type Position = "bullish" | "bearish" | "neutral" | "avoid";
export type Conviction = "high" | "medium" | "low";

export interface PhantomSummary {
  investor_id: string;
  name: string;
  philosophy: string;
}

export interface PhantomMemory {
  context: string;
  decision: string;
  reasoning: string;
  outcome: string;
  lesson: string;
}

export interface PhantomDefinition {
  investor_id: string;
  name: string;
  era: string;
  philosophy: string;
  phantom_memories: PhantomMemory[];
  trigger_patterns: string[];
  blind_spots: string[];
  decision_framework: string[];
}

export interface PhantomAnalysis {
  phantom_id: string;
  phantom_name: string;
  position: Position;
  conviction: Conviction;
  reasoning: string;
  key_factors: string[];
  risks: string[];
  blind_spots_acknowledged: string[];
  timestamp: string;
}

export interface CouncilAnalysis {
  asset: string;
  analyses: PhantomAnalysis[];
  consensus: Position | null;
  disagreements: string[];
  timestamp: string;
}

export interface PhantomListResponse {
  phantoms: PhantomSummary[];
  total: number;
}

export interface AnalysisResponse {
  success: boolean;
  analysis?: PhantomAnalysis;
  error?: string;
}

export interface CouncilResponse {
  success: boolean;
  council?: CouncilAnalysis;
  error?: string;
}

export interface AnalysisRequest {
  asset: string;
  context?: string;
  phantom_ids?: string[];
}

// Quick Scan types
export interface QuickScanRequest {
  symbols: string[];
  include_context?: boolean;
}

export interface OpportunityResult {
  symbol: string;
  score: number;
  consensus_position: string | null;
  consensus_strength: string | null;
  high_conviction_count: number;
  total_phantoms: number;
  key_insight: string;
  bullish_phantoms: string[];
  bearish_phantoms: string[];
  market_context: string | null;
  // Price data from Finnhub
  current_price: number | null;
  price_change: number | null;
  price_change_pct: number | null;
  day_high: number | null;
  day_low: number | null;
}

export interface QuickScanResponse {
  opportunities: OpportunityResult[];
  symbols_scanned: number;
  average_score: number;
}

// Opportunity Storage types
export interface SaveOpportunityRequest {
  symbol: string;
  scan_id?: string;
  opportunity_score: number;
  consensus_position?: string;
  consensus_strength?: string;
  high_conviction_count: number;
  total_phantoms: number;
  bullish_phantoms: string[];
  bearish_phantoms: string[];
  key_insight: string;
  market_context?: string;
  price_at_scan?: number;
}

export interface SaveOpportunitiesResponse {
  success: boolean;
  scan_id: string;
  saved_count: number;
  message: string;
}

export interface StoredOpportunity {
  id: string;
  symbol: string;
  scan_id?: string;
  scanned_at?: string;
  opportunity_score: number;
  consensus_position?: string;
  consensus_strength?: string;
  high_conviction_count: number;
  total_phantoms: number;
  bullish_phantoms: string[];
  bearish_phantoms: string[];
  key_insight: string;
  market_context?: string;
  price_at_scan?: number;
  current_price?: number;
  price_change_pct?: number;
  created_at?: string;
}
