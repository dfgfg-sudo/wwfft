-- 存储Coze工作流ZIP文件的表结构
CREATE TABLE coze_workflow_archives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    zip_data BYTEA NOT NULL,              -- 原始ZIP二进制数据
    extracted_data JSONB,                 -- 解压后的结构化数据（可选）
    metadata JSONB DEFAULT '{}',
    
    -- 错误相关字段
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    error_types TEXT[] DEFAULT '{}',
    
    -- 修复相关字段
    is_fixed BOOLEAN DEFAULT FALSE,
    fix_history JSONB[] DEFAULT '{}',
    last_fixed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- 索引
    CONSTRAINT coze_workflow_archives_name_version_key UNIQUE (name, version)
);

-- 错误模式库（用于智能修复）
CREATE TABLE coze_error_patterns (
    id SERIAL PRIMARY KEY,
    error_signature TEXT UNIQUE NOT NULL,  -- 错误特征哈希
    error_type VARCHAR(100) NOT NULL,      -- 错误分类
    pattern TEXT NOT NULL,                  -- 错误模式（正则表达式）
    context TEXT,                           -- 错误上下文
    fix_template TEXT,                      -- 修复模板
    fix_script TEXT,                        -- Python修复脚本
    occurrence_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 修复历史记录
CREATE TABLE coze_fix_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES coze_workflow_archives(id),
    operation_type VARCHAR(50),            -- 'auto_fix', 'manual_fix', 'rollback'
    changes_applied JSONB,                  -- 应用的修改
    error_before TEXT,                      -- 修复前的错误
    status_after TEXT,                      -- 修复后的状态
    fix_duration_ms INTEGER,
    performed_by VARCHAR(100),              -- 'auto_fixer', 'admin', etc.
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- 创建GIN索引用于快速搜索
CREATE INDEX idx_coze_workflow_errors ON coze_workflow_archives USING gin(error_types);
CREATE INDEX idx_coze_workflow_extracted ON coze_workflow_archives USING gin(extracted_data);