-- Схема базы данных тендеров

CREATE TABLE IF NOT EXISTS tenders (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    law TEXT NOT NULL,  -- '44-ФЗ' or '223-ФЗ'
    customer TEXT,
    amount INTEGER,  -- НМЦ в рублях
    region TEXT,
    deadline TEXT,  -- ISO 8601 или понятный формат
    link TEXT UNIQUE,
    description TEXT,
    fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fetched_at ON tenders(fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_amount ON tenders(amount DESC);
CREATE INDEX IF NOT EXISTS idx_law ON tenders(law);
