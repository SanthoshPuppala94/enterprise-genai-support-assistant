CREATE TABLE IF NOT EXISTS letter_batches (
    batch_id TEXT PRIMARY KEY,
    template_code TEXT NOT NULL,
    status TEXT NOT NULL,
    error_code TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mock_customers (
    customer_id TEXT PRIMARY KEY,
    segment TEXT NOT NULL,
    communication_preference TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id TEXT PRIMARY KEY,
    response_style TEXT DEFAULT 'concise',
    preferred_agent TEXT DEFAULT '',
    preferred_detail_level TEXT DEFAULT 'medium'
);

