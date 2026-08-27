# 添加性能监控
import time

async def main(params):
    start_time = time.time()
    
    # 处理逻辑...
    
    end_time = time.time()
    return {
        "result": processed_data,
        "performance": {
            "execution_time_ms": (end_time - start_time) * 1000
        }
    }