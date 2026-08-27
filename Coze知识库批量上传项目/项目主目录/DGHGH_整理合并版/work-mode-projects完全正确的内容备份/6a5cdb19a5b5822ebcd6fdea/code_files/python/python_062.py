import json

async def main(params):
    """
    自动代码生成器节点
    输入：用户用自然语言描述的需求
    输出：一段可直接在Coze代码节点中运行的完整Python代码
    """
    # 1. 接收来自上游的自然语言需求描述
    # 假设上游是一个“开始节点”或“LLM节点”，传递了一个叫 `user_requirement` 的变量
    requirement = params.get("user_requirement", "").strip()
    
    # 2. 解析需求并构建代码模板
    # 这里是一个智能解析示例，你可以根据需求扩展
    code_template = generate_code_from_requirement(requirement)
    
    # 3. 返回生成的完整代码
    # 注意：我们返回的是一个文本字符串，下游可以复制它
    return {
        "generated_python_code": code_template,
        "requirement_summary": f"已为您生成以下需求的代码：{requirement[:50]}..."  # 摘要
    }

def generate_code_from_requirement(req_text):
    """
    根据自然语言需求，生成对应的Coze代码节点Python代码。
    这是一个规则+模板引擎的示例，你可以无限扩展它。
    """
    
    # 预置的代码骨架（所有Coze代码节点都必须遵循此结构）
    code_skeleton = '''async def main(params):
    # ===================== 输入区 =====================
    # 以下变量名由系统自动推断，您可以根据需要修改
{input_code}
    # ===================== 核心逻辑区 =====================
    # 根据您的需求自动生成的逻辑
    try:
{core_logic_code}
    except Exception as e:
        error_msg = f"处理过程中出现错误: {{e}}"
        # ===================== 输出区 =====================
        return {{
            "status": "error",
            "message": error_msg,
            "processed_data": None
        }}
    
    # ===================== 输出区 =====================
    # 根据您的需求自动配置的输出
    return {{
{output_code}
    }}
'''
    
    # 基于简单的关键词识别来定制代码（这是一个基础示例，可升级为LLM驱动）
    input_code_lines = []
    core_logic_lines = []
    output_code_lines = []
    
    # 示例规则1：如果需求提到“计算”、“总和”、“平均”
    if any(word in req_text.lower() for word in ['计算', '总和', '平均', '加', '数字']):
        input_code_lines.append('    # 系统推断：可能需要处理数字列表')
        input_code_lines.append('    input_data = params.get("input_data", [])  # 建议上游传入列表')
        
        core_logic_lines.append('        # 自动生成的数学计算逻辑')
        core_logic_lines.append('        if isinstance(input_data, list) and all(isinstance(i, (int, float)) for i in input_data):')
        core_logic_lines.append('            total = sum(input_data)')
        core_logic_lines.append('            average = total / len(input_data) if len(input_data) > 0 else 0')
        core_logic_lines.append('            result_msg = f"计算完成。总和={total}, 平均={average:.2f}"')
        core_logic_lines.append('        else:')
        core_logic_lines.append('            result_msg = "输入数据格式有误，期望是数字列表。"')
        core_logic_lines.append('            total = average = 0')
        
        output_code_lines.append('        "status": "success",')
        output_code_lines.append('        "message": result_msg,')
        output_code_lines.append('        "total_sum": total,')
        output_code_lines.append('        "average_value": average,')
        output_code_lines.append('        "processed_data": input_data')
    
    # 示例规则2：如果需求提到“清理”、“去除空格”、“格式化”
    elif any(word in req_text.lower() for word in ['清理', '空格', '格式化', '文本', '清洗']):
        input_code_lines.append('    # 系统推断：需要处理文本字符串')
        input_code_lines.append('    raw_text = params.get("raw_text", "")')
        
        core_logic_lines.append('        # 自动生成的文本清洗逻辑')
        core_logic_lines.append('        cleaned_text = " ".join(raw_text.split())  # 去除多余空格')
        core_logic_lines.append('        cleaned_text = cleaned_text.strip()  # 去除首尾空格')
        core_logic_lines.append('        # 可在此添加更多清洗规则，如去除特殊字符等')
        
        output_code_lines.append('        "status": "success",')
        output_code_lines.append('        "original_text": raw_text,')
        output_code_lines.append('        "cleaned_text": cleaned_text,')
        output_code_lines.append('        "length_difference": len(raw_text) - len(cleaned_text)')
    
    # 默认情况：生成一个通用模板
    else:
        input_code_lines.append('    # 系统未识别到特定模式，生成通用输入接口')
        input_code_lines.append('    user_input = params.get("user_input", "")  # 请确保上游节点提供此变量')
        input_code_lines.append('    optional_data = params.get("optional_data", {})  # 可选的其他数据')
        
        core_logic_lines.append('        # 请在此处编写您的自定义核心逻辑')
        core_logic_lines.append('        # 这是一个占位符示例：将输入转为大写')
        core_logic_lines.append('        processed_result = user_input.upper()')
        core_logic_lines.append('        operation = "转换为大写"')
        
        output_code_lines.append('        "status": "success",')
        output_code_lines.append('        "operation_pe好的，我理解你的需求。你想实现的是：在Coze工作流中，通过一个自然语言输入框描述需求，然后自动生成一个可以“开箱即用”、完整填写好的代码节点（特别是第二步的核心代码）。

这个想法非常棒，它本身就是一种高阶自动化。下面我将为你构建这个 “自动生成代码节点”的系统。

🎯 系统设计蓝图

这个系统的核心是一个 “元代码节点” ：它接收你的自然语言需求，输出一段完整的、可以直接粘贴到另一个新代码节点IDE中的Python代码。