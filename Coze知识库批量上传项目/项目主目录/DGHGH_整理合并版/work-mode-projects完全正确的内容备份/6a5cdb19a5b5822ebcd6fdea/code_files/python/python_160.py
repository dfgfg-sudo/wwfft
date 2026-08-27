# 在代码开头添加诊断
async def main(params):
    print(f"DEBUG: 收到的参数: {list(params.keys())}")
    print(f"DEBUG: 参数值: {params}")
    
    # 继续正常处理...