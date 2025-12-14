"use client";

import { useState } from "react";
import { phantomApi } from "@/lib/api/phantom-api";
import type { QuickScanResponse, OpportunityResult } from "@/types/phantom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

const PRESET_WATCHLISTS = {
  "Mag 7": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"],
  "Value Picks": ["BRK.B", "JPM", "JNJ", "PG", "KO"],
  "Growth Tech": ["PLTR", "SNOW", "CRWD", "NET", "DDOG"],
  "Dividend Kings": ["O", "T", "VZ", "IBM", "MMM"],
};

function getScoreColor(score: number): string {
  if (score >= 8) return "bg-green-500";
  if (score >= 6) return "bg-yellow-500";
  if (score >= 4) return "bg-orange-500";
  return "bg-red-500";
}

function getScoreBadgeVariant(score: number): "default" | "secondary" | "destructive" | "outline" {
  if (score >= 7) return "default";
  if (score >= 5) return "secondary";
  return "destructive";
}

function formatPrice(price: number | null | undefined): string {
  if (price == null) return "—";
  return `$${price.toFixed(2)}`;
}

function formatPriceChange(change: number | null | undefined, pct: number | null | undefined): string {
  if (change == null || pct == null) return "";
  const sign = change >= 0 ? "+" : "";
  return `${sign}${change.toFixed(2)} (${sign}${pct.toFixed(2)}%)`;
}

function OpportunityCard({ opportunity }: { opportunity: OpportunityResult }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card className="bg-zinc-900 border-zinc-800 hover:border-zinc-700 transition-colors">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl font-bold text-white">{opportunity.symbol}</span>
            {opportunity.current_price && (
              <div className="flex items-center gap-2">
                <span className="text-lg text-zinc-200">{formatPrice(opportunity.current_price)}</span>
                <span className={`text-sm ${(opportunity.price_change ?? 0) >= 0 ? "text-green-400" : "text-red-400"}`}>
                  {formatPriceChange(opportunity.price_change, opportunity.price_change_pct)}
                </span>
              </div>
            )}
            <Badge variant={getScoreBadgeVariant(opportunity.score)} className="text-lg px-3 py-1">
              {opportunity.score.toFixed(1)}
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            {opportunity.consensus_position && (
              <Badge variant="outline" className={
                opportunity.consensus_position === "bullish" ? "border-green-500 text-green-500" :
                opportunity.consensus_position === "bearish" ? "border-red-500 text-red-500" :
                "border-zinc-500 text-zinc-500"
              }>
                {opportunity.consensus_position}
              </Badge>
            )}
            <Badge variant="outline" className="border-zinc-600">
              {opportunity.high_conviction_count}/{opportunity.total_phantoms} high conviction
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-zinc-300 mb-3">{opportunity.key_insight}</p>

        {/* Day Range */}
        {opportunity.day_low && opportunity.day_high && (
          <div className="text-xs text-zinc-500 mb-3">
            Day Range: {formatPrice(opportunity.day_low)} - {formatPrice(opportunity.day_high)}
          </div>
        )}

        <div className="flex flex-wrap gap-2 mb-3">
          {opportunity.bullish_phantoms.length > 0 && (
            <div className="flex items-center gap-1">
              <span className="text-xs text-zinc-500">Bullish:</span>
              {opportunity.bullish_phantoms.map((p) => (
                <Badge key={p} variant="outline" className="border-green-700 text-green-400 text-xs">
                  {p}
                </Badge>
              ))}
            </div>
          )}
          {opportunity.bearish_phantoms.length > 0 && (
            <div className="flex items-center gap-1">
              <span className="text-xs text-zinc-500">Bearish:</span>
              {opportunity.bearish_phantoms.map((p) => (
                <Badge key={p} variant="outline" className="border-red-700 text-red-400 text-xs">
                  {p}
                </Badge>
              ))}
            </div>
          )}
        </div>

        {opportunity.market_context && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setExpanded(!expanded)}
            className="text-zinc-400 hover:text-white p-0"
          >
            {expanded ? "Hide context" : "Show market context"}
          </Button>
        )}

        {expanded && opportunity.market_context && (
          <div className="mt-3 p-3 bg-zinc-800 rounded-lg">
            <p className="text-sm text-zinc-400">{opportunity.market_context}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function QuickScanPage() {
  const [symbols, setSymbols] = useState("");
  const [results, setResults] = useState<QuickScanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [includeContext, setIncludeContext] = useState(true);

  const handleScan = async (symbolList?: string[]) => {
    console.log("handleScan called", { symbolList, symbols });

    const symbolsToScan = symbolList || symbols
      .toUpperCase()
      .split(/[\s,]+/)
      .filter((s) => s.length > 0);

    console.log("Symbols to scan:", symbolsToScan);

    if (symbolsToScan.length === 0) {
      setError("Enter at least one symbol");
      return;
    }

    if (symbolsToScan.length > 20) {
      setError("Maximum 20 symbols per scan");
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);
    setSaved(false);

    try {
      console.log("Making API call...");
      const response = await phantomApi.quickScan({
        symbols: symbolsToScan,
        include_context: includeContext,
      });
      console.log("API response:", response);
      setResults(response);
    } catch (err) {
      console.error("Scan error:", err);
      setError(err instanceof Error ? err.message : "Scan failed");
    } finally {
      setLoading(false);
    }
  };

  const handlePresetClick = (preset: string[]) => {
    setSymbols(preset.join(", "));
    handleScan(preset);
  };

  const handleSave = async () => {
    if (!results || results.opportunities.length === 0) return;

    setSaving(true);
    try {
      const opportunitiesToSave = results.opportunities.map((opp) => ({
        symbol: opp.symbol,
        opportunity_score: opp.score,
        consensus_position: opp.consensus_position || undefined,
        consensus_strength: opp.consensus_strength || undefined,
        high_conviction_count: opp.high_conviction_count,
        total_phantoms: opp.total_phantoms,
        bullish_phantoms: opp.bullish_phantoms,
        bearish_phantoms: opp.bearish_phantoms,
        key_insight: opp.key_insight,
        market_context: opp.market_context || undefined,
        price_at_scan: opp.current_price || undefined,
      }));

      const response = await phantomApi.saveOpportunities(opportunitiesToSave);
      if (response.success) {
        setSaved(true);
      } else {
        setError("Failed to save opportunities");
      }
    } catch (err) {
      console.error("Save error:", err);
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="min-h-screen bg-black text-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Quick Scan</h1>
            <p className="text-zinc-400">
              Scan your watchlist with the phantom council. Get scored opportunities ranked by strategic signal strength.
            </p>
          </div>
          <div className="flex gap-4">
            <a href="/opportunities" className="text-green-400 hover:text-green-300">
              View Saved
            </a>
            <a href="/" className="text-zinc-400 hover:text-white">
              Council
            </a>
          </div>
        </div>

        {/* Input Section */}
        <Card className="bg-zinc-900 border-zinc-800 mb-6">
          <CardHeader>
            <CardTitle>Watchlist Scanner</CardTitle>
            <CardDescription>
              Enter symbols separated by commas or spaces, or select a preset watchlist
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={(e) => { e.preventDefault(); handleScan(); }}>
              <div className="flex gap-3 mb-4">
                <Input
                  value={symbols}
                  onChange={(e) => setSymbols(e.target.value)}
                  placeholder="AAPL, MSFT, NVDA, TSLA..."
                  className="bg-zinc-800 border-zinc-700 text-white flex-1"
                />
                <Button
                  type="submit"
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 min-w-[120px]"
                >
                  {loading ? "Scanning..." : "Scan"}
                </Button>
              </div>
            </form>

            {/* Preset Watchlists */}
            <div className="flex flex-wrap gap-2 mb-4">
              <span className="text-sm text-zinc-500 mr-2">Presets:</span>
              {Object.entries(PRESET_WATCHLISTS).map(([name, list]) => (
                <Button
                  key={name}
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handlePresetClick(list)}
                  disabled={loading}
                  className="border-zinc-700 hover:border-zinc-500"
                >
                  {name}
                </Button>
              ))}
            </div>

            {/* Options */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="includeContext"
                checked={includeContext}
                onChange={(e) => setIncludeContext(e.target.checked)}
                className="rounded bg-zinc-800 border-zinc-700"
              />
              <label htmlFor="includeContext" className="text-sm text-zinc-400">
                Include market context (Perplexity) - adds ~5s per symbol
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Error Display */}
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
            <CardContent className="py-12 text-center">
              <div className="animate-pulse">
                <div className="text-xl text-zinc-400 mb-2">Analyzing in parallel...</div>
                <div className="text-sm text-zinc-500 mb-1">
                  6 phantoms × {symbols.split(/[\s,]+/).filter(s => s).length || 1} symbols = {6 * (symbols.split(/[\s,]+/).filter(s => s).length || 1)} AI calls running simultaneously
                </div>
                <div className="text-xs text-zinc-600">
                  {includeContext ? "With market context (~20-30s)" : "Without context (~15-20s)"}
                </div>
                <div className="mt-4 flex justify-center gap-2">
                  {[...Array(6)].map((_, i) => (
                    <div
                      key={i}
                      className="w-3 h-3 rounded-full bg-blue-500 animate-bounce"
                      style={{ animationDelay: `${i * 0.1}s` }}
                    />
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results */}
        {results && !loading && (
          <div>
            {/* Summary */}
            <Card className="bg-zinc-900 border-zinc-800 mb-6">
              <CardContent className="py-4">
                <div className="flex justify-between items-center">
                  <div>
                    <span className="text-zinc-400">Scanned </span>
                    <span className="text-white font-bold">{results.symbols_scanned} symbols</span>
                    <span className="text-zinc-400 ml-4">Average Score: </span>
                    <Badge variant={getScoreBadgeVariant(results.average_score)}>
                      {results.average_score.toFixed(1)}
                    </Badge>
                  </div>
                  <div>
                    {saved ? (
                      <Badge className="bg-green-600">Saved!</Badge>
                    ) : (
                      <Button
                        type="button"
                        onClick={handleSave}
                        disabled={saving}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        {saving ? "Saving..." : "Save Results"}
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Opportunity Cards */}
            <div className="space-y-4">
              {results.opportunities.map((opp) => (
                <OpportunityCard key={opp.symbol} opportunity={opp} />
              ))}
            </div>

            {results.opportunities.length === 0 && (
              <Card className="bg-zinc-900 border-zinc-800">
                <CardContent className="py-8 text-center">
                  <p className="text-zinc-400">No opportunities found</p>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Score Legend */}
        {!loading && !results && (
          <Card className="bg-zinc-900 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-lg">Scoring Guide</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <Badge className="bg-green-500 mb-1">9-10</Badge>
                  <p className="text-zinc-400">High-conviction consensus</p>
                </div>
                <div>
                  <Badge className="bg-yellow-500 mb-1">7-8</Badge>
                  <p className="text-zinc-400">Strategic disagreement</p>
                </div>
                <div>
                  <Badge className="bg-orange-500 mb-1">5-6</Badge>
                  <p className="text-zinc-400">Mixed signals</p>
                </div>
                <div>
                  <Badge className="bg-red-500 mb-1">1-4</Badge>
                  <p className="text-zinc-400">Weak or avoid</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Navigation */}
        <div className="mt-8 flex justify-center gap-4">
          <a href="/opportunities" className="text-green-400 hover:text-green-300">
            View Saved Opportunities
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
