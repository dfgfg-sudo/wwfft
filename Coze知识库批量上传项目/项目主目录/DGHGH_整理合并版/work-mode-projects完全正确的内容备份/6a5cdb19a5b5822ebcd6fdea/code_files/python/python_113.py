async def main(params):
    # 1. 从params字典中获取输入参数（参数名在第一步配置）
    input_text = params.get("input_text", "") # 例如从上游LLM节点来的文本
    number_list = params.get("numbers", [])   # 例如接收到一个数组

    # 2. 在此处编写你的核心处理逻辑（这是需要你主要修改的部分）
    # 示例：计算平均数并生成报告
    if number_list:
        average = sum(number_list) / len(number_list)
        result_text = f"分析完成。共{len(number_list)}个数，平均值为{average:.2f}。"
    else:
        result_text = "未接收到有效数据。"

    # 3. 将需要输出的结果封装成字典返回（键名需与第三步的输出配置匹配）
    return {
        "analysis_result": result_text,
        "calculated_average": average if number_list else None
    }