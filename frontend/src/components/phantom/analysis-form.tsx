"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface AnalysisFormProps {
  onSubmit: (asset: string, context?: string) => void;
  isLoading: boolean;
}

const popularAssets = [
  { symbol: "NVDA", name: "NVIDIA" },
  { symbol: "AAPL", name: "Apple" },
  { symbol: "GOOG", name: "Google" },
  { symbol: "MSFT", name: "Microsoft" },
  { symbol: "TSLA", name: "Tesla" },
  { symbol: "BTC", name: "Bitcoin" },
  { symbol: "META", name: "Meta" },
  { symbol: "AMZN", name: "Amazon" },
];

export function AnalysisForm({ onSubmit, isLoading }: AnalysisFormProps) {
  const [asset, setAsset] = useState("");
  const [context, setContext] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (asset.trim()) {
      onSubmit(asset.trim().toUpperCase(), context.trim() || undefined);
    }
  };

  const handleQuickSelect = (symbol: string) => {
    setAsset(symbol);
    onSubmit(symbol, context.trim() || undefined);
  };

  return (
    <Card className="bg-slate-900/50 border-slate-700">
      <CardHeader>
        <CardTitle className="text-xl text-slate-100">
          Summon the Phantom Council
        </CardTitle>
        <p className="text-sm text-slate-400">
          Enter an asset to receive analysis from 6 legendary investors
        </p>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex gap-2">
            <Input
              type="text"
              placeholder="Enter ticker symbol (e.g., AAPL, BTC)"
              value={asset}
              onChange={(e) => setAsset(e.target.value.toUpperCase())}
              className="flex-1 bg-slate-800 border-slate-600 text-slate-100 placeholder:text-slate-500"
              disabled={isLoading}
            />
            <Button
              type="submit"
              disabled={isLoading || !asset.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <span className="animate-spin">⏳</span> Analyzing...
                </span>
              ) : (
                "Analyze"
              )}
            </Button>
          </div>

          <div>
            <Input
              type="text"
              placeholder="Additional context (optional)"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              className="bg-slate-800 border-slate-600 text-slate-100 placeholder:text-slate-500"
              disabled={isLoading}
            />
          </div>

          {/* Quick Select */}
          <div>
            <p className="text-xs text-slate-500 mb-2">Quick select:</p>
            <div className="flex flex-wrap gap-2">
              {popularAssets.map((item) => (
                <Button
                  key={item.symbol}
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleQuickSelect(item.symbol)}
                  disabled={isLoading}
                  className="border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-slate-100"
                >
                  {item.symbol}
                </Button>
              ))}
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
