"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { PhantomAnalysis, Position, Conviction } from "@/types/phantom";

interface PhantomCardProps {
  analysis: PhantomAnalysis;
}

const positionColors: Record<Position, string> = {
  bullish: "bg-green-500/20 text-green-400 border-green-500/30",
  bearish: "bg-red-500/20 text-red-400 border-red-500/30",
  neutral: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  avoid: "bg-gray-500/20 text-gray-400 border-gray-500/30",
};

const convictionColors: Record<Conviction, string> = {
  high: "bg-purple-500/20 text-purple-400 border-purple-500/30",
  medium: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  low: "bg-slate-500/20 text-slate-400 border-slate-500/30",
};

const positionEmoji: Record<Position, string> = {
  bullish: "📈",
  bearish: "📉",
  neutral: "➡️",
  avoid: "🚫",
};

export function PhantomCard({ analysis }: PhantomCardProps) {
  return (
    <Card className="bg-slate-900/50 border-slate-700/50 hover:border-slate-600/50 transition-colors">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold text-slate-100">
            {analysis.phantom_name}
          </CardTitle>
          <div className="flex gap-2">
            <Badge className={positionColors[analysis.position]}>
              {positionEmoji[analysis.position]} {analysis.position.toUpperCase()}
            </Badge>
            <Badge className={convictionColors[analysis.conviction]}>
              {analysis.conviction.toUpperCase()}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Reasoning */}
        <div>
          <h4 className="text-sm font-medium text-slate-400 mb-1">Reasoning</h4>
          <p className="text-sm text-slate-300 leading-relaxed">
            {analysis.reasoning}
          </p>
        </div>

        {/* Key Factors */}
        {analysis.key_factors.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-slate-400 mb-2">Key Factors</h4>
            <ul className="space-y-1">
              {analysis.key_factors.map((factor, i) => (
                <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Risks */}
        {analysis.risks.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-slate-400 mb-2">Risks</h4>
            <ul className="space-y-1">
              {analysis.risks.map((risk, i) => (
                <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                  <span className="text-red-400 mt-1">⚠</span>
                  {risk}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Blind Spots */}
        {analysis.blind_spots_acknowledged.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-slate-400 mb-2">
              Acknowledged Blind Spots
            </h4>
            <ul className="space-y-1">
              {analysis.blind_spots_acknowledged.map((blind_spot, i) => (
                <li key={i} className="text-sm text-slate-400 italic flex items-start gap-2">
                  <span className="text-yellow-400 mt-1">👁</span>
                  {blind_spot}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
