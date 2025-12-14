"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PhantomCard } from "./phantom-card";
import type { CouncilAnalysis, Position } from "@/types/phantom";

interface CouncilResultsProps {
  council: CouncilAnalysis;
}

const consensusColors: Record<Position | "none", string> = {
  bullish: "bg-green-500/20 text-green-300 border-green-500/50",
  bearish: "bg-red-500/20 text-red-300 border-red-500/50",
  neutral: "bg-yellow-500/20 text-yellow-300 border-yellow-500/50",
  avoid: "bg-gray-500/20 text-gray-300 border-gray-500/50",
  none: "bg-purple-500/20 text-purple-300 border-purple-500/50",
};

const consensusEmoji: Record<Position | "none", string> = {
  bullish: "📈",
  bearish: "📉",
  neutral: "➡️",
  avoid: "🚫",
  none: "⚔️",
};

export function CouncilResults({ council }: CouncilResultsProps) {
  const consensusKey = council.consensus || "none";

  // Count positions
  const positionCounts = council.analyses.reduce(
    (acc, a) => {
      acc[a.position] = (acc[a.position] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="space-y-6">
      {/* Summary Header */}
      <Card className="bg-gradient-to-r from-slate-900 to-slate-800 border-slate-600">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl font-bold text-white">
                Council Analysis: {council.asset}
              </CardTitle>
              <p className="text-slate-400 mt-1">
                {council.analyses.length} phantom perspectives
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-slate-400 mb-1">Consensus</p>
              <Badge
                className={`text-lg px-4 py-1 ${consensusColors[consensusKey]}`}
              >
                {consensusEmoji[consensusKey]}{" "}
                {council.consensus?.toUpperCase() || "DIVIDED"}
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Position Summary */}
          <div className="flex gap-4 mb-4">
            {Object.entries(positionCounts).map(([position, count]) => (
              <div
                key={position}
                className="flex items-center gap-2 text-sm text-slate-300"
              >
                <span className="font-medium">{count}x</span>
                <Badge
                  variant="outline"
                  className={consensusColors[position as Position]}
                >
                  {position}
                </Badge>
              </div>
            ))}
          </div>

          {/* Disagreements */}
          {council.disagreements.length > 0 && (
            <div className="border-t border-slate-700 pt-4 mt-4">
              <h4 className="text-sm font-medium text-slate-300 mb-2">
                Key Disagreements & Insights
              </h4>
              <ul className="space-y-2">
                {council.disagreements.map((disagreement, i) => (
                  <li
                    key={i}
                    className="text-sm text-slate-400 flex items-start gap-2"
                  >
                    <span className="text-purple-400">⚡</span>
                    {disagreement}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Individual Analyses */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {council.analyses.map((analysis) => (
          <PhantomCard key={analysis.phantom_id} analysis={analysis} />
        ))}
      </div>
    </div>
  );
}
