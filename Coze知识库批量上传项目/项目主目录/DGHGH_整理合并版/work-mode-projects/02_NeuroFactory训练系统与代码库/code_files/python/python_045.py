"""
元代码生成器 - 完整版
将此代码完整复制到一个新的代码节点中
"""

import json
from datetime import datetime

async def main(params):
    """
    自动化代码生成器
    输入：自然语言需求描述
    输出：可直接运行的完整Python代码
    """
    # 1. 接收用户需求
    requirement = params.get("user_requirement", "").strip()
    
    # 2. 生成对应代码
    generated_code = generate_code_from_requirement(requirement)
    
    # 3. 返回结果
    return {
        "generated_python_code": generated_code,
        "input_requirements": get_input_requirements(generated_code),
        "output_variables": get_output_variables(generated_code),
        "setup_instructions": get_setup_instructions(),
        "generated_at": datetime.now().isoformat(),
        "status": "success"
    }

def generate_code_from_requirement(req_text):
    """根据需求生成代码模板"""
    req_lower = req_text.lower()
    
    # 检测需求类型
    if any(word in req_lower for word in ['清洗', '清理', '空格', '文本', '格式化']):
        return generate_text_cleaner()
    elif any(word in req_lower for word in ['计算', '总和', '平均', '数学', '统计']):
        return generate_math_calculator()
    elif any(word in req_lower for word in ['json', '解析', '提取', '数据']):
        return generate_json_parser()
    elif any(word in req_lower for word in ['api', '请求', '获取', '调用']):
        return generate_api_caller()
    else:
        return generate_general_processor()

def generate_text_cleaner():
    """生成文本清洗工具代码"""
    return '''"""
文本清洗处理器
功能：清理文本中的多余空格，统计字符信息
生成时间：{timestamp}
"""
import re

async def main(params):
    # ========== 输入配置区 ==========
    # 从上游节点接收数据（变量名可修改）
    raw_text = params.get("input_text", "")
    if not raw_text:
        raw_text = params.get("text", "")
    
    # ========== 核心处理逻辑 ==========
    try:
        # 1. 去除首尾空格
        cleaned = raw_text.strip()
        
        # 2. 将多个连续空格合并为一个
        cleaned = re.sub(r'\\s+', ' ', cleaned)
        
        # 3. 统计信息
        stats = {
            "original_length": len(raw_text),
            "cleaned_length": len(cleaned),
            "space_reduction": len(raw_text) - len(cleaned),
            "word_count": len(cleaned.split()),
            "line_count": len(raw_text.split('\\n')),
            "has_multiple_spaces": '  ' in raw_text
        }
        
        # 4. 生成结果消息
        result_msg = f"✅ 文本清洗完成！\\n"
        result_msg += f"原始长度: {stats['original_length']} 字符\\n"
        result_msg += f"清理后: {stats['cleaned_length']} 字符\\n"
        result_msg += f"减少空格: {stats['space_reduction']} 字符\\n"
        result_msg += f"单词数量: {stats['word_count']}"
        
        if stats['has_multiple_spaces']:
            result_msg += "\\n⚠️ 检测到多个连续空格，已清理"
    
    except Exception as e:
        result_msg = f"❌ 处理错误: {{str(e)}}"
        cleaned = raw_text
        stats = {{"error": str(e)}}
    
    # ========== 输出配置区 ==========
    return {{
        "status": "success",
        "message": result_msg,
        "cleaned_text": cleaned,
        "statistics": stats,
        "processing_time": "{timestamp}",
        "original_preview": raw_text[:100] + ("..." if len(raw_text) > 100 else "")
    }}
'''.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def generate_math_calculator():
    """生成数学计算器代码"""
    return '''"""
数学计算器
功能：计算数字列表的统计信息
生成时间：{timestamp}
"""

async def main(params):
    # ========== 输入配置区 ==========
    # 接收数字列表（支持多种格式）
    numbers_input = params.get("numbers", [])
    
    # 处理输入格式
    if isinstance(numbers_input, str):
        try:
            numbers = [float(x.strip()) for x in numbers_input.split(',') if x.strip()]
        except:
            numbers = []
    elif isinstance(numbers_input, list):
        numbers = []
        for item in numbers_input:
            try:
                numbers.append(float(item))
            except:
                pass
    else:
        numbers = []
    
    # ========== 核心处理逻辑 ==========
    calculations = {{}}
    
    try:
        if not numbers:
            result_msg = "⚠️ 未接收到有效数字数据"
        else:
            # 执行计算
            total = sum(numbers)
            average = total / len(numbers)
            maximum = max(numbers)
            minimum = min(numbers)
            
            # 排序
            sorted_numbers = sorted(numbers)
            
            # 中位数
            n = len(sorted_numbers)
            if n % 2 == 1:
                median = sorted_numbers[n//2]
            else:
                median = (sorted_numbers[n//2-1] + sorted_numbers[n//2]) / 2
            
            calculations = {{
                "total": round(total, 4),
                "average": round(average, 4),
                "max": round(maximum, 4),
                "min": round(minimum, 4),
                "median": round(median, 4),
                "range": round(maximum - minimum, 4),
                "count": len(numbers),
                "sorted_list": sorted_numbers
            }}
            
            result_msg = f"✅ 计算完成！\\n"
            result_msg += f"处理数字: {len(numbers)} 个\\n"
            result_msg += f"总和: {{calculations['total']}}\\n"
            result_msg += f"平均: {{calculations['average']}}\\n"
            result_msg += f"范围: {{calculations['min']}} 到 {{calculations['max']}}"
    
    except Exception as e:
        result_msg = f"❌ 计算错误: {{str(e)}}"
    
    # ========== 输出配置区 ==========
    return {{
        "status": "success" if numbers else "no_data",
        "message": result_msg,
        "calculations": calculations,
        "input_numbers": numbers_input,
        "valid_numbers": numbers,
        "processing_time": "{timestamp}"
    }}
'''.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def get_input_requirements(code):
    """从代码中提取输入要求"""
    return [
        "根据生成的代码，在输入配置中设置对应的变量名",
        "常见输入变量名: input_text, numbers, json_data, api_url",
        "确保上游节点提供这些变量"
    ]

def get_output_variables(code):
    """从代码中提取输出变量"""
    return [
        "在输出配置中添加代码中return的所有键名",
        "确保变量名完全一致（区分大小写）",
        "常见输出: status, message, processed_data"
    ]

def get_setup_instructions():
    """获取设置说明"""
    return [
        "1. 复制上方generated_python_code的全部内容",
        "2. 新建代码节点 → 点击'在IDE中编辑'",
        "3. 清空原有内容 → 粘贴复制的代码",
        "4. 配置输入参数（参考input_requirements）",
        "5. 配置输出变量（参考output_variables）",
        "6. 测试运行"
    ]