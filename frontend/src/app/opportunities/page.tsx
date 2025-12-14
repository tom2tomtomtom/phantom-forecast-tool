"use client";

import { useState, useEffect } from "react";
import { phantomApi } from "@/lib/api/phantom-api";
import type { StoredOpportunity } from "@/types/phantom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

function getScoreBadgeVariant(score: number): "default" | "secondary" | "destructive" | "outline" {
  if (score >= 7) return "default";
  if (score >= 5) return "secondary";
  return "destructive";
}

function formatDate(dateString: string | undefined): string {
  if (!dateString) return "Unknown";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatPrice(price: number | null | undefined): string {
  if (price == null) return "—";
  return `$${price.toFixed(2)}`;
}

function OpportunityRow({ opportunity }: { opportunity: StoredOpportunity }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card className="bg-zinc-900 border-zinc-800 hover:border-zinc-700 transition-colors">
      <CardContent className="py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-xl font-bold text-white w-20">{opportunity.symbol}</span>
            <Badge variant={getScoreBadgeVariant(opportunity.opportunity_score)} className="text-lg px-3">
              {opportunity.opportunity_score.toFixed(1)}
            </Badge>
            {opportunity.consensus_position && (
              <Badge
                variant="outline"
                className={
                  opportunity.consensus_position === "bullish"
                    ? "border-green-500 text-green-500"
                    : opportunity.consensus_position === "bearish"
                    ? "border-red-500 text-red-500"
                    : "border-zinc-500 text-zinc-500"
                }
              >
                {opportunity.consensus_position}
              </Badge>
            )}
            <span className="text-sm text-zinc-500">
              {opportunity.high_conviction_count}/{opportunity.total_phantoms} high conviction
            </span>
          </div>
          <div className="flex items-center gap-4">
            {opportunity.price_change_pct !== null && opportunity.price_change_pct !== undefined && (
              <Badge
                variant="outline"
                className={
                  opportunity.price_change_pct >= 0
                    ? "border-green-500 text-green-500"
                    : "border-red-500 text-red-500"
                }
              >
                {opportunity.price_change_pct >= 0 ? "+" : ""}
                {opportunity.price_change_pct.toFixed(1)}%
              </Badge>
            )}
            <span className="text-xs text-zinc-500">{formatDate(opportunity.scanned_at)}</span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setExpanded(!expanded)}
              className="text-zinc-400"
            >
              {expanded ? "Less" : "More"}
            </Button>
          </div>
        </div>

        {expanded && (
          <div className="mt-4 pt-4 border-t border-zinc-800">
            <p className="text-zinc-300 mb-3">{opportunity.key_insight}</p>

            {/* Price tracking */}
            {opportunity.price_at_scan && (
              <div className="flex gap-6 mb-3 text-sm">
                <div>
                  <span className="text-zinc-500">Price at Scan: </span>
                  <span className="text-white">{formatPrice(opportunity.price_at_scan)}</span>
                </div>
                {opportunity.current_price && (
                  <div>
                    <span className="text-zinc-500">Current: </span>
                    <span className="text-white">{formatPrice(opportunity.current_price)}</span>
                  </div>
                )}
              </div>
            )}

            <div className="flex flex-wrap gap-4 text-sm">
              {opportunity.bullish_phantoms && opportunity.bullish_phantoms.length > 0 && (
                <div>
                  <span className="text-zinc-500">Bullish: </span>
                  {opportunity.bullish_phantoms.map((p) => (
                    <Badge key={p} variant="outline" className="border-green-700 text-green-400 text-xs ml-1">
                      {p}
                    </Badge>
                  ))}
                </div>
              )}
              {opportunity.bearish_phantoms && opportunity.bearish_phantoms.length > 0 && (
                <div>
                  <span className="text-zinc-500">Bearish: </span>
                  {opportunity.bearish_phantoms.map((p) => (
                    <Badge key={p} variant="outline" className="border-red-700 text-red-400 text-xs ml-1">
                      {p}
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {opportunity.market_context && (
              <div className="mt-3 p-3 bg-zinc-800 rounded-lg">
                <p className="text-sm text-zinc-400">{opportunity.market_context}</p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<StoredOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingPrices, setUpdatingPrices] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "bullish" | "bearish">("all");
  const [minScore, setMinScore] = useState(0);
  const [days, setDays] = useState(7);

  const fetchOpportunities = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await phantomApi.getRecentOpportunities({
        limit: 50,
        min_score: minScore,
        days: days,
      });

      // Apply client-side filter for consensus
      let filtered = data;
      if (filter !== "all") {
        filtered = data.filter((o) => o.consensus_position === filter);
      }

      setOpportunities(filtered);
    } catch (err) {
      console.error("Failed to fetch opportunities:", err);
      setError(err instanceof Error ? err.message : "Failed to load opportunities");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOpportunities();
  }, [minScore, days]);

  useEffect(() => {
    // Re-filter when filter changes (client-side)
    if (filter !== "all") {
      phantomApi.getRecentOpportunities({ limit: 50, min_score: minScore, days }).then((data) => {
        setOpportunities(data.filter((o) => o.consensus_position === filter));
      });
    } else {
      fetchOpportunities();
    }
  }, [filter]);

  const handleUpdatePrices = async () => {
    setUpdatingPrices(true);
    setError(null);
    try {
      const result = await phantomApi.updateOpportunityPrices(days);
      if (result.success) {
        // Refresh to show updated prices
        await fetchOpportunities();
      }
    } catch (err) {
      console.error("Failed to update prices:", err);
      setError(err instanceof Error ? err.message : "Failed to update prices");
    } finally {
      setUpdatingPrices(false);
    }
  };

  const stats = {
    total: opportunities.length,
    avgScore: opportunities.length > 0
      ? (opportunities.reduce((sum, o) => sum + o.opportunity_score, 0) / opportunities.length).toFixed(1)
      : "0",
    bullish: opportunities.filter((o) => o.consensus_position === "bullish").length,
    bearish: opportunities.filter((o) => o.consensus_position === "bearish").length,
  };

  return (
    <main className="min-h-screen bg-black text-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Saved Opportunities</h1>
          <p className="text-zinc-400">
            Historical phantom council analyses and their outcomes.
          </p>
        </div>

        {/* Filters */}
        <Card className="bg-zinc-900 border-zinc-800 mb-6">
          <CardContent className="py-4">
            <div className="flex flex-wrap items-center gap-4">
              {/* Consensus Filter */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-zinc-400">Consensus:</span>
                <div className="flex gap-1">
                  {(["all", "bullish", "bearish"] as const).map((f) => (
                    <Button
                      key={f}
                      type="button"
                      variant={filter === f ? "default" : "outline"}
                      size="sm"
                      onClick={() => setFilter(f)}
                      className={filter === f ? "" : "border-zinc-700"}
                    >
                      {f.charAt(0).toUpperCase() + f.slice(1)}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Min Score Filter */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-zinc-400">Min Score:</span>
                <select
                  value={minScore}
                  onChange={(e) => setMinScore(Number(e.target.value))}
                  className="bg-zinc-800 border border-zinc-700 rounded px-2 py-1 text-sm"
                >
                  <option value={0}>Any</option>
                  <option value={5}>5+</option>
                  <option value={6}>6+</option>
                  <option value={7}>7+</option>
                  <option value={8}>8+</option>
                </select>
              </div>

              {/* Days Filter */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-zinc-400">Period:</span>
                <select
                  value={days}
                  onChange={(e) => setDays(Number(e.target.value))}
                  className="bg-zinc-800 border border-zinc-700 rounded px-2 py-1 text-sm"
                >
                  <option value={1}>Today</option>
                  <option value={7}>Last 7 days</option>
                  <option value={30}>Last 30 days</option>
                  <option value={90}>Last 90 days</option>
                </select>
              </div>

              {/* Refresh */}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={fetchOpportunities}
                className="border-zinc-700"
              >
                Refresh
              </Button>

              {/* Update Prices */}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleUpdatePrices}
                disabled={updatingPrices}
                className="border-zinc-700"
              >
                {updatingPrices ? "Updating..." : "Update Prices"}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Stats Summary */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <Card className="bg-zinc-900 border-zinc-800">
            <CardContent className="py-4 text-center">
              <div className="text-2xl font-bold text-white">{stats.total}</div>
              <div className="text-xs text-zinc-500">Total</div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900 border-zinc-800">
            <CardContent className="py-4 text-center">
              <div className="text-2xl font-bold text-white">{stats.avgScore}</div>
              <div className="text-xs text-zinc-500">Avg Score</div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900 border-zinc-800">
            <CardContent className="py-4 text-center">
              <div className="text-2xl font-bold text-green-500">{stats.bullish}</div>
              <div className="text-xs text-zinc-500">Bullish</div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900 border-zinc-800">
            <CardContent className="py-4 text-center">
              <div className="text-2xl font-bold text-red-500">{stats.bearish}</div>
              <div className="text-xs text-zinc-500">Bearish</div>
            </CardContent>
          </Card>
        </div>

        {/* Error State */}
        {error && (
          <Card className="bg-red-900/20 border-red-800 mb-6">
            <CardContent className="py-4">
              <p className="text-red-400">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Loading State */}
        {loading && (
          <Card className="bg-zinc-900 border-zinc-800 mb-6">
            <CardContent className="py-8 text-center">
              <div className="animate-pulse text-zinc-400">Loading opportunities...</div>
            </CardContent>
          </Card>
        )}

        {/* Opportunities List */}
        {!loading && opportunities.length > 0 && (
          <div className="space-y-3">
            {opportunities.map((opp) => (
              <OpportunityRow key={opp.id} opportunity={opp} />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && opportunities.length === 0 && !error && (
          <Card className="bg-zinc-900 border-zinc-800">
            <CardContent className="py-12 text-center">
              <p className="text-zinc-400 text-lg mb-4">No saved opportunities yet</p>
              <a href="/quick-scan">
                <Button className="bg-blue-600 hover:bg-blue-700">
                  Run a Quick Scan
                </Button>
              </a>
            </CardContent>
          </Card>
        )}

        {/* Navigation */}
        <div className="mt-8 flex justify-center gap-4">
          <a href="/quick-scan" className="text-blue-400 hover:text-blue-300">
            Quick Scan
          </a>
          <span className="text-zinc-600">|</span>
          <a href="/" className="text-zinc-400 hover:text-white">
            Council Analysis
          </a>
        </div>
      </div>
    </main>
  );
}
