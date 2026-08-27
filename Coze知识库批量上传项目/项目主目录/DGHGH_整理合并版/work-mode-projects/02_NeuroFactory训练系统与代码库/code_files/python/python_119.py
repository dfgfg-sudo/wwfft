# scheduler.py - 定时运行修复
from apscheduler.schedulers.background import BackgroundScheduler

def scheduled_fix_job():
    fixer = CozeWorkflowFixer(db_params)
    
    # 只修复最近有错误的
    fixer.cur.execute("""
        UPDATE coze_workflows 
        SET error_count = 0 
        WHERE updated_at < NOW() - INTERVAL '1 hour'
        AND error_count > 0
    """)
    
    # 运行批量修复
    fixer.run_batch_fix(limit=20)

# 每30分钟运行一次
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_fix_job, 'interval', minutes=30)
scheduler.start()