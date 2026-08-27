-- 1. 修复连接配置错误（批量更新数据库连接字符串）
UPDATE coze_workflows 
SET definition = jsonb_set(
    definition,
    '{nodes,?,config,connection}',
    '"postgresql://user:pass@new-host:5432/dbname"'
)
WHERE definition->'nodes' @? '$[*].type ? (@ == "postgres")'
AND definition->'nodes' @? '$[*].config.connection ? (@ like "%old-host%")';

-- 2. 修复SQL语法错误（添加缺失的分号）
WITH problematic_workflows AS (
    SELECT id, definition,
           jsonb_array_elements(definition->'nodes') as node
    FROM coze_workflows
    WHERE definition::text LIKE '%SELECT * FROM%'
    AND definition::text NOT LIKE '%;%'
)
UPDATE coze_workflows wf
SET definition = jsonb_set(
    wf.definition,
    path,
    to_jsonb(replace(node::text, 'SELECT * FROM', 'SELECT * FROM') || ';')
)
FROM problematic_workflows pf
WHERE wf.id = pf.id;

-- 3. 修复变量映射缺失问题
UPDATE coze_workflows
SET definition = jsonb_set(
    definition,
    '{nodes,?,config,inputMapping}',
    '{"$param1": "{{input.param1}}", "$param2": "{{input.param2}}"}'
)
WHERE definition->'nodes' @? '$[*].type ? (@ == "postgres")'
AND NOT definition->'nodes' @? '$[*].config ? (exists(@.inputMapping))';

-- 4. 重置错误计数并标记为已修复
UPDATE coze_workflows 
SET error_count = 0,
    config = jsonb_set(
        config,
        '{last_fixed}',
        to_jsonb(CURRENT_TIMESTAMP)
    )
WHERE error_count > 0;