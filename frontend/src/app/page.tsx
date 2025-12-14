"use client";

import { useState } from "react";
import { AnalysisForm, CouncilResults } from "@/components/phantom";
import { phantomApi } from "@/lib/api/phantom-api";
import type { CouncilAnalysis } from "@/types/phantom";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [council, setCouncil] = useState<CouncilAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (asset: string, context?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await phantomApi.analyzeWithCouncil({ asset, context });

      if (response.success && response.council) {
        setCouncil(response.council);
      } else {
        setError(response.error || "Analysis failed");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">
                👻 Phantom Forecast
              </h1>
              <p className="text-sm text-slate-400">
                Pluralistic Strategic Intelligence
              </p>
            </div>
            <div className="flex items-center gap-4">
              <a
                href="/quick-scan"
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                Quick Scan
              </a>
              <a
                href="/opportunities"
                className="text-sm text-green-400 hover:text-green-300 transition-colors"
              >
                Saved
              </a>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">Powered by</span>
                <span className="text-xs font-medium text-slate-300">
                  Claude AI
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Hero Section */}
          <div className="text-center py-8">
            <h2 className="text-4xl font-bold text-white mb-4">
              The Phantom Council
            </h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Six legendary investors analyze your asset through their unique
              strategic lenses. See where they agree, where they disagree, and
              why.
            </p>
            <div className="flex justify-center gap-4 mt-6 text-sm text-slate-500">
              <span>📈 Buffett</span>
              <span>🧠 Munger</span>
              <span>🔍 Burry</span>
              <span>🌊 Dalio</span>
              <span>⚡ Ackman</span>
              <span>🏪 Lynch</span>
            </div>
          </div>

          {/* Analysis Form */}
          <AnalysisForm onSubmit={handleAnalyze} isLoading={isLoading} />

          {/* Loading State */}
          {isLoading && (
            <div className="text-center py-12">
              <div className="inline-flex items-center gap-3 text-slate-300">
                <div className="animate-spin h-6 w-6 border-2 border-blue-500 border-t-transparent rounded-full" />
                <span className="text-lg">
                  Summoning the phantom council...
                </span>
              </div>
              <p className="text-sm text-slate-500 mt-2">
                Each phantom is analyzing independently (this may take 15-30
                seconds)
              </p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-center">
              <p className="text-red-400">{error}</p>
              <p className="text-sm text-slate-500 mt-2">
                Make sure the backend is running on{" "}
                {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
              </p>
            </div>
          )}

          {/* Results */}
          {council && !isLoading && <CouncilResults council={council} />}

          {/* Empty State */}
          {!council && !isLoading && !error && (
            <div className="text-center py-16 text-slate-500">
              <p className="text-6xl mb-4">👻</p>
              <p className="text-lg">
                Enter a ticker symbol above to summon the council
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-16">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-sm text-slate-500">
            Phantom Forecast Tool - Experimental AI Market Intelligence
          </p>
          <p className="text-center text-xs text-slate-600 mt-1">
            Not financial advice. Strategic disagreement is the goal.
          </p>
        </div>
      </footer>
    </div>
  );
}
