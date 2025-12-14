-- Opportunities table for storing scan results
-- Run this in Supabase SQL Editor or via migrations

CREATE TABLE IF NOT EXISTS opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Asset info
    symbol VARCHAR(10) NOT NULL,

    -- Scan metadata
    scan_id UUID,  -- Groups opportunities from same scan
    scanned_at TIMESTAMPTZ DEFAULT NOW(),

    -- Scoring
    opportunity_score DECIMAL(3,1) NOT NULL CHECK (opportunity_score >= 0 AND opportunity_score <= 10),

    -- Council analysis summary
    consensus_position VARCHAR(20),  -- bullish, bearish, neutral, null
    consensus_strength VARCHAR(20),  -- strong, weak, none
    high_conviction_count INTEGER DEFAULT 0,
    total_phantoms INTEGER DEFAULT 6,

    -- Phantom positions (stored as arrays)
    bullish_phantoms TEXT[],
    bearish_phantoms TEXT[],

    -- Insights
    key_insight TEXT NOT NULL,
    market_context TEXT,

    -- Full analysis (JSON for flexibility)
    full_analysis JSONB,  -- Complete council response if needed

    -- Market data at scan time
    price_at_scan DECIMAL(12,4),

    -- Performance tracking (updated later)
    current_price DECIMAL(12,4),
    price_change_pct DECIMAL(6,2),
    last_price_update TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_opportunities_symbol ON opportunities(symbol);
CREATE INDEX IF NOT EXISTS idx_opportunities_score ON opportunities(opportunity_score DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_scanned_at ON opportunities(scanned_at DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_scan_id ON opportunities(scan_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_consensus ON opportunities(consensus_position);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_opportunities_updated_at ON opportunities;
CREATE TRIGGER update_opportunities_updated_at
    BEFORE UPDATE ON opportunities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- View for recent top opportunities
CREATE OR REPLACE VIEW top_recent_opportunities AS
SELECT
    id,
    symbol,
    opportunity_score,
    consensus_position,
    key_insight,
    bullish_phantoms,
    bearish_phantoms,
    scanned_at,
    price_change_pct
FROM opportunities
WHERE scanned_at > NOW() - INTERVAL '7 days'
ORDER BY opportunity_score DESC, scanned_at DESC
LIMIT 50;

-- View for opportunity performance summary
CREATE OR REPLACE VIEW opportunity_performance AS
SELECT
    symbol,
    COUNT(*) as scan_count,
    AVG(opportunity_score) as avg_score,
    MAX(opportunity_score) as max_score,
    AVG(price_change_pct) FILTER (WHERE price_change_pct IS NOT NULL) as avg_return,
    MAX(scanned_at) as last_scanned
FROM opportunities
GROUP BY symbol
ORDER BY avg_score DESC;

-- Enable RLS (Row Level Security) - disabled for now, enable when adding auth
-- ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE opportunities IS 'Stores phantom council scan results for historical tracking';
COMMENT ON COLUMN opportunities.scan_id IS 'Groups multiple opportunities from the same scan batch';
COMMENT ON COLUMN opportunities.full_analysis IS 'Complete JSON of council analysis for detailed review';
