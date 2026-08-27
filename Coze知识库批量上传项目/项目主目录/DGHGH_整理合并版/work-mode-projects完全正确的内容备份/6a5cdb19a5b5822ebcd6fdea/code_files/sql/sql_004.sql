-- 修复历史记录表
CREATE TABLE coze_fix_history (
    id SERIAL PRIMARY KEY,
    workflow_id UUID REFERENCES coze_workflows(id),
    fixes_applied JSONB,
    fixed_at TIMESTAMP DEFAULT NOW(),
    fixed_by VARCHAR(100),
    notes TEXT
);

-- 错误模式统计表
CREATE TABLE coze_error_patterns (
    id SERIAL PRIMARY KEY,
    error_type VARCHAR(100),
    pattern TEXT,
    fix_sql TEXT,
    occurrence_count INTEGER DEFAULT 0,
    last_occurred TIMESTAMP
);