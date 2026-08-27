-- 示例表结构
CREATE TABLE coze_workflows (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    definition JSONB,           -- 工作流定义（JSON格式）
    config JSONB,              -- 配置信息
    version INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    error_count INTEGER DEFAULT 0
);

CREATE TABLE coze_executions (
    id UUID PRIMARY KEY,
    workflow_id UUID REFERENCES coze_workflows(id),
    status VARCHAR(50),
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);