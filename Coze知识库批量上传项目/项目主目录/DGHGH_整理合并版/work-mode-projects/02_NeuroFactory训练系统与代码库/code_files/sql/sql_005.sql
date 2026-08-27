-- 查看修复统计
   SELECT 
    DATE(fixed_at) as fix_date,
    COUNT(*) as workflows_fixed,
    ARRAY_AGG(DISTINCT fixed_by) as fixers
   FROM coze_fix_history
   GROUP BY DATE(fixed_at)
   ORDER BY fix_date DESC;