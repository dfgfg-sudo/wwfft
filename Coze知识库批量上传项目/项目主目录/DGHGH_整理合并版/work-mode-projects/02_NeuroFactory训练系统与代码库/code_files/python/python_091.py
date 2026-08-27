import re

async def main(params):
    # 1. 接收来自工作流上游的输入数据（变量名user_query与第一步配置对应）
    user_query = params.get("user_query", "").strip()
    
    # 2. 在此处编写你的【自定义逻辑核心】（这是你可以自由发挥的部分）
    # 以下是一个基于规则和关键词的工单分类逻辑示例，你可以替换成任何你的业务逻辑
    
    # 初始化输出变量
    issue_type = "其他"
    urgency = "低"
    recommended_dept = "客服中心"
    
    # 自定义分类规则字典（完全可根据你的需求增删改）
    category_keywords = {
        "账单疑问": ["扣费", "账单", "金额", "支付", "退款", "涨价"],
        "技术故障": ["无法登录", "打不开", "错误代码", "闪退", "卡顿", "连接失败"],
        "账号问题": ["修改密码", "注销账号", "账号被盗", "更换手机号", "绑定"]
    }
    
    # 紧急程度判断规则
    urgency_indicators = ["急", "尽快", "立刻", "马上", "崩溃", "不能用", "严重影响"]
    
    # ---- 核心逻辑开始：分析用户问题 ----
    # 2.1 判断问题类型
    for category, keywords in category_keywords.items():
        if any(keyword in user_query for keyword in keywords):
            issue_type = category
            break
    
    # 2.2 判断紧急程度
    if any(indicator in user_query for indicator in urgency_indicators):
        urgency = "高"
        recommended_dept = "技术支持部"  # 紧急工单升级路由
    elif issue_type == "技术故障":
        urgency = "中"
        recommended_dept = "技术部"
    elif issue_type == "账单疑问":
        recommended_dept = "财务部"
        
    # 2.3 （示例）可以在此处添加更复杂的逻辑，例如：
    # - 调用一个内部的API来查询知识库
    # - 进行情感分析，将用户愤怒的反馈标记为高紧急度
    # - 对查询进行向量化并与历史工单匹配
    
    # 3. 将处理结果打包成字典返回（键名将作为输出变量名）
    return {
        "original_query": user_query,  # 原始问题（可选输出）
        "identified_issue_type": issue_type,
        "assessed_urgency": urgency,
        "recommended_department": recommended_dept,
        # 可以附加一个结构化的处理建议
        "suggestion": f"该问题已识别为【{issue_type}】，紧急程度【{urgency}】，建议转交【{recommended_dept}】处理。"
    }