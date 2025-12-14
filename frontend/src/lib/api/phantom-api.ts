// API client for Phantom Forecast Tool backend

import type {
  PhantomListResponse,
  PhantomSummary,
  PhantomDefinition,
  AnalysisResponse,
  CouncilResponse,
  AnalysisRequest,
  QuickScanRequest,
  QuickScanResponse,
  SaveOpportunityRequest,
  SaveOpportunitiesResponse,
  StoredOpportunity,
} from "@/types/phantom";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class PhantomAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async fetch<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.fetch("/health");
  }

  // List all phantoms
  async listPhantoms(): Promise<PhantomListResponse> {
    return this.fetch("/api/phantoms");
  }

  // Get phantom summary
  async getPhantom(phantomId: string): Promise<PhantomSummary> {
    return this.fetch(`/api/phantoms/${phantomId}`);
  }

  // Get full phantom definition
  async getPhantomFull(phantomId: string): Promise<PhantomDefinition> {
    return this.fetch(`/api/phantoms/${phantomId}/full`);
  }

  // Analyze with single phantom
  async analyzeWithPhantom(
    phantomId: string,
    asset: string,
    context?: string
  ): Promise<AnalysisResponse> {
    const params = new URLSearchParams({ asset });
    if (context) params.append("context", context);

    return this.fetch(`/api/phantoms/${phantomId}/analyze?${params}`, {
      method: "POST",
    });
  }

  // Analyze with full council
  async analyzeWithCouncil(request: AnalysisRequest): Promise<CouncilResponse> {
    return this.fetch("/api/phantoms/council/analyze", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // Quick scan watchlist
  async quickScan(request: QuickScanRequest): Promise<QuickScanResponse> {
    return this.fetch("/api/scan/quick", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // Save opportunities
  async saveOpportunities(opportunities: SaveOpportunityRequest[]): Promise<SaveOpportunitiesResponse> {
    return this.fetch("/api/opportunities/save", {
      method: "POST",
      body: JSON.stringify(opportunities),
    });
  }

  // Get recent opportunities
  async getRecentOpportunities(params?: {
    limit?: number;
    min_score?: number;
    days?: number;
  }): Promise<StoredOpportunity[]> {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set("limit", params.limit.toString());
    if (params?.min_score) searchParams.set("min_score", params.min_score.toString());
    if (params?.days) searchParams.set("days", params.days.toString());

    const query = searchParams.toString();
    return this.fetch(`/api/opportunities/recent${query ? `?${query}` : ""}`);
  }

  // Get top opportunities
  async getTopOpportunities(limit: number = 10, days: number = 7): Promise<StoredOpportunity[]> {
    return this.fetch(`/api/opportunities/top?limit=${limit}&days=${days}`);
  }

  // Get opportunities by symbol
  async getSymbolHistory(symbol: string, limit: number = 10): Promise<StoredOpportunity[]> {
    return this.fetch(`/api/opportunities/symbol/${symbol}?limit=${limit}`);
  }

  // Update prices for stored opportunities
  async updateOpportunityPrices(days: number = 7): Promise<{
    success: boolean;
    updated_count: number;
    symbols_checked: number;
    message: string;
  }> {
    return this.fetch(`/api/opportunities/update-prices?days=${days}`, {
      method: "POST",
    });
  }
}

// Export singleton instance
export const phantomApi = new PhantomAPI();

// Export class for testing
export { PhantomAPI };
