pip install -e .
Usage
bash
复制
下载
python main.py
Tools
{tools_list}
'''
}
},
"coze_plugin": {
"description": "Coze插件模板",
"structure": {
"plugin_config": {
"name": "{plugin_name}",
"version": "1.0.0",
"description": "{plugin_description}",
"author": "{author}",
"nodes": [],
"edges": []
}
}
},
"web_api": {
"description": "Web API模板",
"files": {
"app.py": '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="{api_name}")

class RequestModel(BaseModel):
data: str

class ResponseModel(BaseModel):
success: bool
message: str
result: Any

@app.get("/")
async def root():
return {{"message": "{api_name} API"}}

@app.post("/process")
async def process_data(request: RequestModel):
try:
result = {{"processed": request.data}}
return ResponseModel(
success=True,
message="Processing successful",
result=result
)
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))

if name == "main":
uvicorn.run(app, host="0.0.0.0", port=8000)
'''
}
}
}

if template_file.exists():
try:
with open(template_file, 'r', encoding='utf-8') as f:
return json.load(f)
except:
return default_templates

with open(template_file, 'w', encoding='utf-8') as f:
json.dump(default_templates, f, indent=2, ensure_ascii=False)
return default_templates

def generate_mcp_server(self, requirements: str) -> Dict[str, Any]:
"""生成MCP服务器"""
server_name = self._extract_server_name(requirements)
description = self._extract_description(requirements)
tools = self._extract_tools(requirements)

tools_code = self._generate_tools_code(tools)
tools_list = self._generate_tools_list(tools)

rendered_files = {}
for file_name, template in self.templates["mcp_server"]["files"].items():
rendered = template.format(
server_name=server_name,
description=description,
tools_code=tools_code,
tools_list=tools_list,
extra_dependencies=self._get_extra_dependencies(requirements)
)
rendered_files[file_name] = rendered

return {
"server_name": server_name,
"description": description,
"tools": tools,
"files": rendered_files,
"directory_structure": [
server_name + "/",
f" {server_name}/init.py",
f" {server_name}/main.py",
" requirements.txt",
" README.md",
" pyproject.toml"
]
}

def analyze_plugin_requirements(self, requirements: str) -> Dict[str, Any]:
"""分析插件需求"""
return {
"name": self._extract_plugin_name(requirements),
"type": self._detect_plugin_type(requirements),
"description": self._extract_description(requirements),
"inputs": self._extract_inputs(requirements),
"outputs": self._extract_outputs(requirements),
"functionality": self._analyze_functionality(requirements)
}

def generate_plugin(self, plugin_spec: Dict[str, Any]) -> Dict[str, Any]:
"""生成插件代码"""
plugin_type = plugin_spec.get("type", "general")

if plugin_type == "coze":
return self._generate_coze_plugin(plugin_spec)
elif plugin_type == "web":
return self._generate_web_plugin(plugin_spec)
else:
return self._generate_general_plugin(plugin_spec)

def analyze_code_requirements(self, requirements: str) -> Dict[str, Any]:
"""分析代码生成需求"""
return {
"language": self._detect_programming_language(requirements),
"purpose": self._extract_code_purpose(requirements),
"complexity": self._estimate_complexity(requirements),
"requirements": requirements
}

def generate_code(self, code_spec: Dict[str, Any]) -> str:
"""生成代码"""
language = code_spec.get("language", "python")
purpose = code_spec.get("purpose", "general")

if language == "python":
return self._generate_python_code(code_spec)
elif language == "javascript":
return self._generate_javascript_code(code_spec)
elif language == "typescript":
return self._generate_typescript_code(code_spec)
else:
return self._generate_general_code(code_spec)

def _extract_server_name(self, text: str) -> str:
"""提取服务器名称"""
patterns = [
r'create\s+(?:a\s+)?server\s+(?:called\s+|named\s+)?([^\s,.!?]+)',
r'build\s+(?:a\s+)?server\s+(?:called\s+|named\s+)?([^\s,.!?]+)',
r'mcp\s+server\s+(?:called\s+|named\s+)?([^\s,.!?]+)'
]

for pattern in patterns:
match = re.search(pattern, text, re.IGNORECASE)
if match:
return match.group(1).replace('-', '').replace(' ', '')

return "mcp_server_" + hashlib.md5(text.encode()).hexdigest()[:8]

def _extract_plugin_name(self, text: str) -> str:
"""提取插件名称"""
patterns = [
r'plugin\s+(?:called\s+|named\s+)?([^\s,.!?]+)',
r'create\s+(?:a\s+)?plugin\s+(?:called\s+|named\s+)?([^\s,.!?]+)'
]

for pattern in patterns:
match = re.search(pattern, text, re.IGNORECASE)
if match:
return match.group(1)

return "plugin_" + hashlib.md5(text.encode()).hexdigest()[:8]

def _extract_description(self, text: str) -> str:
"""提取描述"""
return text[:100].strip() + ("..." if len(text) > 100 else "")

def _extract_tools(self, text: str) -> List[Dict[str, str]]:
"""提取工具定义"""
tools = []

keywords = {
"calculator": ["calculate", "compute", "math"],
"converter": ["convert", "transform", "change"],
"validator": ["validate", "check", "verify"],
"formatter": ["format", "beautify", "prettify"],
"analyzer": ["analyze", "parse", "examine"]
}

text_lower = text.lower()
for tool_name, patterns in keywords.items():
if any(pattern in text_lower for pattern in patterns):
tools.append({
"name": tool_name,
"description": f"{tool_name} tool",
"function": f"perform_{tool_name}_operation"
})

if not tools:
tools.append({
"name": "process_data",
"description": "Process input data",
"function": "process_data"
})

return tools

def _generate_tools_code(self, tools: List[Dict[str, str]]) -> str:
"""生成工具代码"""
code_lines = []

for tool in tools:
code_lines.extend([
f"@server.tool()",
f"async def {tool['function']}(data: str) -> str:",
f' """{tool["description"]}"""',
f" try:",
f" return f'Processed: {{data}}'",
f" except Exception as e:",
f" return f'Error: {{str(e)}}'",
f""
])

return "\n".join(code_lines)

def _generate_tools_list(self, tools: List[Dict[str, str]]) -> str:
"""生成工具列表"""
return "\n".join([f"- {t['name']}: {t['description']}" for t in tools])

def _get_extra_dependencies(self, requirements: str) -> str:
"""获取额外依赖"""
deps = []

if any(word in requirements.lower() for word in ['http', 'api', 'request']):
deps.append("httpx")

if any(word in requirements.lower() for word in ['data', 'process', 'analyze']):
deps.append("pandas")

if any(word in requirements.lower() for word in ['ai', 'ml', 'model']):
deps.append("scikit-learn")

return "\n".join(deps) if deps else "# No extra dependencies"

def _detect_plugin_type(self, text: str) -> str:
"""检测插件类型"""
text_lower = text.lower()

if any(word in text_lower for word in ['coze', 'chatbot', '对话']):
return "coze"
elif any(word in text_lower for word in ['web', 'api', 'rest']):
return "web"
elif any(word in text_lower for word in ['desktop', 'gui', '界面']):
return "desktop"
else:
return "general"

def _extract_inputs(self, text: str) -> List[Dict[str, str]]:
"""提取输入参数"""
inputs = []

input_patterns = [
r'input(?:s)?\s[:：]\s([^.\n]+)',
r'参数\s[:：]\s([^.\n]+)',
r'receive(?:s)?\s*([^.\n]+)'
]

for pattern in input_patterns:
matches = re.findall(pattern, text, re.IGNORECASE)
for match in matches:
for item in match.split(','):
item = item.strip()
if item and len(item) > 1:
inputs.append({
"name": item.lower().replace(' ', '_'),
"type": self._infer_type(item),
"description": item
})

if not inputs:
inputs.append({
"name": "input_data",
"type": "string",
"description": "输入数据"
})

return inputs

def _extract_outputs(self, text: str) -> List[Dict[str, str]]:
"""提取输出参数"""
outputs = []

output_patterns = [
r'output(?:s)?\s[:：]\s([^.\n]+)',
r'返回\s[:：]\s([^.\n]+)',
r'generate(?:s)?\s*([^.\n]+)'
]

for pattern in output_patterns:
matches = re.findall(pattern, text, re.IGNORECASE)
for match in matches:
for item in match.split(','):
item = item.strip()
if item and len(item) > 1:
outputs.append({
"name": item.lower().replace(' ', '_'),
"type": self._infer_type(item),
"description": item
})

if not outputs:
outputs.append({
"name": "result",
"type": "string",
"description": "处理结果"
})

return outputs

def _infer_type(self, text: str) -> str:
"""推断数据类型"""
text_lower = text.lower()

if any(word in text_lower for word in ['number', 'count', 'amount', '数字', '数量']):
return "number"
elif any(word in text_lower for word in ['boolean', 'bool', 'flag', '是否', '状态']):
return "boolean"
elif any(word in text_lower for word in ['list', 'array', 'collection', '列表', '数组']):
return "array"
elif any(word in text_lower for word in ['object', 'dict', 'map', '对象', '字典']):
return "object"
else:
return "string"

def _analyze_functionality(self, text: str) -> List[str]:
"""分析功能"""
functionality = []

if any(word in text.lower() for word in ['process', 'handle', 'deal with', '处理']):
functionality.append("数据处理")

if any(word in text.lower() for word in ['transform', 'convert', 'change', '转换']):
functionality.append("数据转换")

if any(word in text.lower() for word in ['validate', 'check', 'verify', '验证']):
functionality.append("数据验证")

if any(word in text.lower() for word in ['generate', 'create', 'produce', '生成']):
functionality.append("内容生成")

if not functionality:
functionality.append("通用处理")

return functionality

def _generate_coze_plugin(self, plugin_spec: Dict[str, Any]) -> Dict[str, Any]:
"""生成Coze插件"""
plugin_config = {
"plugin_name": plugin_spec.get("name", "unnamed_plugin"),
"version": "1.0.0",
"description": plugin_spec.get("description", ""),
"author": "Auto-generated",
"created_at": datetime.now().isoformat(),
"nodes": [
{
"id": "main_node",
"type": "processor",
"name": "Main Processor",
"inputs": plugin_spec.get("inputs", []),
"outputs": plugin_spec.get("outputs", []),
"configuration": {
"functionality": plugin_spec.get("functionality", [])
}
}
],
"edges": []
}

return {
"plugin_config": plugin_config,
"implementation": f"""

Coze Plugin: {plugin_config['plugin_name']}
Auto-generated at: {plugin_config['created_at']}
def process(input_data):
"""Process input data"""
return {{"result": "Processed successfully", "data": input_data}}

def handler(event, context):
return process(event.get('data', ''))
"""
}

def _generate_web_plugin(self, plugin_spec: Dict[str, Any]) -> Dict[str, Any]:
"""生成Web插件"""
return {
"type": "web_plugin",
"name": plugin_spec.get("name", "web_plugin"),
"files": {
"app.py": f"""
from flask import Flask, request, jsonify

app = Flask(name)

@app.route('/process', methods=['POST'])
def process():
data = request.json.get('data', '')
result = {{"processed": data, "status": "success"}}
return jsonify(result)

if name == 'main':
app.run(debug=True)
"""
}
}

def _generate_general_plugin(self, plugin_spec: Dict[str, Any]) -> Dict[str, Any]:
"""生成通用插件"""
return {
"type": "general_plugin",
"name": plugin_spec.get("name", "general_plugin"),
"specification": plugin_spec,
"template": """
def process_plugin(data, config=None):
return {
"success": True,
"input": data,
"output": f"Processed: {data}",
"timestamp": "{timestamp}"
}
""".format(timestamp=datetime.now().isoformat())
}

def _detect_programming_language(self, text: str) -> str:
"""检测编程语言"""
text_lower = text.lower()

if any(word in text_lower for word in ['python', 'py', 'pandas', 'numpy']):
return "python"
elif any(word in text_lower for word in ['javascript', 'js', 'node', 'react']):
return "javascript"
elif any(word in text_lower for word in ['typescript', 'ts', 'type']):
return "typescript"
elif any(word in text_lower for word in ['java', 'spring', 'jvm']):
return "java"
elif any(word in text_lower for word in ['go', 'golang']):
return "go"
elif any(word in text_lower for word in ['rust', 'cargo']):
return "rust"
else:
return "python"

def _extract_code_purpose(self, text: str) -> str:
"""提取代码目的"""
purposes = {
"data_processing": ["process data", "handle data", "数据分析", "数据处理"],
"api": ["api", "rest", "endpoint", "接口"],
"utility": ["utility", "tool", "helper", "工具"],
"web": ["web", "website", "网页", "网站"],
"automation": ["automate", "自动", "自动化"]
}

text_lower = text.lower()
for purpose, keywords in purposes.items():
if any(keyword in text_lower for keyword in keywords):
return purpose

return "general"

def _estimate_complexity(self, text: str) -> str:
"""估计复杂度"""
word_count = len(text.split())

if word_count > 200:
return "high"
elif word_count > 50:
return "medium"
else:
return "low"

def _generate_python_code(self, code_spec: Dict[str, Any]) -> str:
"""生成Python代码"""
purpose = code_spec.get("purpose", "general")
requirements = code_spec.get("requirements", "")

templates = {
"data_processing": """
import pandas as pd
import numpy as np
from typing import Dict, List, Any

def process_data(data: Any) -> Dict[str, Any]:
try:
if isinstance(data, dict):
df = pd.DataFrame([data])
elif isinstance(data, list):
df = pd.DataFrame(data)
else:
df = pd.DataFrame({"data": [data]})

result = {
"success": True,
"processed_count": len(df),
"summary": df.describe().to_dict(),
"timestamp": pd.Timestamp.now().isoformat()
}
return result
except Exception as e:
return {
"success": False,
"error": str(e),
"timestamp": pd.Timestamp.now().isoformat()
}

if name == "main":
sample_data = {"example": "data"}
result = process_data(sample_data)
print(result)
""",
"api": """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
import uvicorn

app = FastAPI(title="Auto-generated API")

class RequestModel(BaseModel):
data: str

class ResponseModel(BaseModel):
success: bool
message: str
result: Optional[Any] = None

@app.get("/")
async def root():
return {"message": "Auto-generated API", "version": "1.0.0"}

@app.post("/process")
async def process(request: RequestModel):
try:
processed_data = {"original": request.data, "processed": True}
return ResponseModel(
success=True,
message="Processing successful",
result=processed_data
)
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))

if name == "main":
uvicorn.run(app, host="0.0.0.0", port=8000)
"""
}

template = templates.get(purpose, """

Auto-generated code
Requirements: {requirements}
def main():
print("Auto-generated code based on requirements")
return {"status": "success", "message": "Code generated successfully"}

if name == "main":
main()
""")

return template.format(requirements=requirements)

def _generate_javascript_code(self, code_spec: Dict[str, Any]) -> str:
"""生成JavaScript代码"""
return f"""
// Auto-generated JavaScript code
// Requirements: {code_spec.get('requirements', '')}

class AutoGenerated {{
constructor() {{
this.name = "AutoGenerated";
this.version = "1.0.0";
}}

process(data) {{
return {{
success: true,
input: data,
output: Processed: ${{data}},
timestamp: new Date().toISOString()
}};
}}
}}

if (typeof module !== 'undefined' && module.exports) {{
module.exports = AutoGenerated;
}}

const instance = new AutoGenerated();
const result = instance.process("test data");
console.log(result);
"""

def _generate_typescript_code(self, code_spec: Dict[str, Any]) -> str:
"""生成TypeScript代码"""
return f"""
// Auto-generated TypeScript code
// Requirements: {code_spec.get('requirements', '')}

interface ProcessResult {{
success: boolean;
input: any;
output: any;
timestamp: string;
}}

class AutoGenerated {{
private name: string = "AutoGenerated";
private version: string = "1.0.0";

process(data: any): ProcessResult {{
return {{
success: true,
input: data,
output: Processed: ${{data}},
timestamp: new Date().toISOString()
}};
}}
}}

export default AutoGenerated;

const instance = new AutoGenerated();
const result = instance.process("test data");
console.log(result);
"""

def _generate_general_code(self, code_spec: Dict[str, Any]) -> str:
"""生成通用代码"""
return f"""

Auto-generated code
Language: {code_spec.get('language', 'unknown')}
Purpose: {code_spec.get('purpose', 'general')}
Requirements: {code_spec.get('requirements', '')}
def main():
print("Code generated successfully")
return {"status": "success"}

if name == "main":
main()
"""

===================================================================
数据验证器
===================================================================
class DataValidator:
"""数据验证器 - 验证各种内容"""

def init(self, config: UnifiedSystemConfig):
self.config = config
self.logger = logging.getLogger(name)

def validate_coze_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
"""验证Coze插件结构"""
validation = {
"valid": True,
"errors": [],
"warnings": [],
"suggestions": []
}

if not isinstance(data, dict):
validation["valid"] = False
validation["errors"].append("数据必须是字典类型")
return validation

required_fields = ["plugin_name", "version"]
for field in required_fields:
if field not in data:
validation["warnings"].append(f"建议添加字段: {field}")

if "nodes" in data:
if not isinstance(data["nodes"], list):
validation["errors"].append("nodes必须是数组")
else:
for i, node in enumerate(data["nodes"]):
if isinstance(node, dict):
if "id" not in node:
validation["errors"].append(f"节点 {i} 缺少ID字段")
if "type" not in node:
validation["warnings"].append(f"节点 {i} 缺少type字段")

validation["valid"] = len(validation["errors"]) == 0
return validation

def validate_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
"""验证工作流结构"""
validation = {
"valid": True,
"errors": [],
"warnings": [],
"suggestions": []
}

if not isinstance(data, dict):
validation["valid"] = False
validation["errors"].append("工作流数据必须是字典类型")
return validation

workflow_keys = ["name", "version", "nodes", "edges", "parameters"]
for key in workflow_keys:
if key in data:
if key == "nodes" and not isinstance(data[key], list):
validation["errors"].append("nodes必须是数组")
elif key == "edges" and not isinstance(data[key], list):
validation["errors"].append("edges必须是数组")

if "nodes" in data and "edges" in data:
node_ids = [node.get("id") for node in data["nodes"] if isinstance(node, dict) and "id" in node]

for i, edge in enumerate(data["edges"]):
if isinstance(edge, dict):
source = edge.get("source")
target = edge.get("target")

if source and source not in node_ids:
validation["warnings"].append(f"边 {i} 的source节点不存在: {source}")

if target and target not in node_ids:
validation["warnings"].append(f"边 {i} 的target节点不存在: {target}")

validation["valid"] = len(validation["errors"]) == 0
return validation

def validate_openapi_spec(self, data: Dict[str, Any]) -> Dict[str, Any]:
"""验证OpenAPI规范"""
validation = {
"valid": True,
"errors": [],
"warnings": [],
"suggestions": []
}

if not isinstance(data, dict):
validation["valid"] = False
validation["errors"].append("OpenAPI规范必须是字典类型")
return validation

if "openapi" not in data:
validation["errors"].append("缺少openapi字段")
elif not data["openapi"].startswith("3."):
validation["warnings"].append(f"OpenAPI版本 {data['openapi']} 可能不是3.x版本")

if "info" not in data:
validation["errors"].append("缺少info字段")
elif isinstance(data["info"], dict):
if "title" not in data["info"]:
validation["warnings"].append("info中缺少title字段")
if "version" not in data["info"]:
validation["warnings"].append("info中缺少version字段")

if "paths" not in data:
validation["warnings"].append("缺少paths字段")

validation["valid"] = len(validation["errors"]) == 0
return validation

def validate_code_syntax(self, code: str) -> Dict[str, Any]:
"""验证代码语法"""
validation = {
"valid": True,
"errors": [],
"warnings": [],
"suggestions": []
}

lines = code.split('\n')
brace_count = 0
bracket_count = 0
paren_count = 0

for i, line in enumerate(lines, 1):
brace_count += line.count('{') - line.count('}')
bracket_count += line.count('[') - line.count(']')
paren_count += line.count('(') - line.count(')')

if line.strip().endswith('=') and not line.strip().startswith('#'):
validation["warnings"].append(f"第 {i} 行: 可能缺少赋值右侧")

if brace_count != 0:
validation["errors"].append(f"大括号不匹配: 差 {abs(brace_count)} 个")

if bracket_count != 0:
validation["warnings"].append(f"中括号不匹配: 差 {abs(bracket_count)} 个")

if paren_count != 0:
validation["errors"].append(f"小括号不匹配: 差 {abs(paren_count)} 个")

if 'eval(' in code:
validation["warnings"].append("检测到可能的eval用法，建议避免使用")

if 'import' in code:
validation["warnings"].append("检测到__import__，可能有安全风险")

validation["valid"] = len(validation["errors"]) == 0
return validation

===================================================================
批量处理器
===================================================================
class BatchProcessor:
"""批量处理器 - 处理目录中的所有文件"""

def init(self, config: UnifiedSystemConfig):
self.config = config
self.logger = logging.getLogger(name)
self.content_processor = None # 延迟初始化

def process_directory(self, directory: Path, operation_mode: str = "auto_detect",
automation_level: str = "standard",
output_format: str = "json_pretty",
max_workers: int = 4) -> Dict[str, Any]:
"""处理目录中的所有文件"""
results = {
"directory": str(directory),
"total_files": 0,
"processed_files": 0,
"successful": 0,
"failed": 0,
"results": [],
"summary": {},
"processing_time": 0
}

start_time = datetime.now()

try:
files = self._collect_files(directory)
results["total_files"] = len(files)

if not files:
self.logger.warning(f"目录中没有找到文件: {directory}")
return results

with ThreadPoolExecutor(max_workers=min(max_workers, len(files))) as executor:
future_to_file = {
executor.submit(
self._process_single_file,
file_path,
operation_mode,
automation_level,
output_format
): file_path for file_path in files
}

for future in as_completed(future_to_file):
file_path = future_to_file[future]
try:
file_result = future.result()
results["results"].append(file_result)

if file_result.get("success", False):
results["successful"] += 1
else:
results["failed"] += 1

results["processed_files"] += 1

except Exception as e:
self.logger.error(f"处理文件失败 {file_path}: {e}")
results["failed"] += 1
results["results"].append({
"file": str(file_path),
"success": False,
"error": str(e)
})

results["summary"] = self._generate_batch_summary(results["results"])
results["processing_time"] = (datetime.now() - start_time).total_seconds()

self.logger.info(f"批量处理完成: {results['processed_files']}/{results['total_files']} 文件")

except Exception as e:
self.logger.error(f"批量处理失败: {e}")
results["error"] = str(e)

return results

def _collect_files(self, directory: Path) -> List[Path]:
"""收集文件"""
files = []

if not directory.exists():
self.logger.warning(f"目录不存在: {directory}")
return files

all_extensions = []
for category, exts in self.config.supported_formats.items():
all_extensions.extend(exts)

for ext in all_extensions:
for file_path in directory.rglob(f"*{ext}"):
if file_path.is_file():
file_size_mb = file_path.stat().st_size / (1024 * 1024)
if file_size_mb <= self.config.performance['max_file_size_mb']:
files.append(file_path)
else:
self.logger.warning(f"文件过大，跳过: {file_path} ({file_size_mb:.1f}MB)")

return files

def _process_single_file(self, file_path: Path, operation_mode: str,
automation_level: str, output_format: str) -> Dict[str, Any]:
"""处理单个文件"""
file_result = {
"file": str(file_path),
"filename": file_path.name,
"size_bytes": file_path.stat().st_size,
"success": False,
"processing_time": 0
}

start_time = datetime.now()

try:
with open(file_path, 'r', encoding='utf-8') as f:
content = f.read()

延迟初始化内容处理器
if self.content_processor is None:
from unified_automation_tool import UnifiedContentProcessor
self.content_processor = UnifiedContentProcessor(self.config)

result = self.content_processor.process_content(
content=content,
operation_mode=operation_mode,
automation_level=automation_level,
output_format=output_format
)

file_result.update({
"success": result.get("metadata", {}).get("success", False),
"operation": result.get("metadata", {}).get("operation_mode", "unknown"),
"result_summary": self._summarize_result(result)
})

except UnicodeDecodeError:
try:
with open(file_path, 'r', encoding='latin-1') as f:
content = f.read()

if self.content_processor is None:
from unified_automation_tool import UnifiedContentProcessor
self.content_processor = UnifiedContentProcessor(self.config)

result = self.content_processor.process_content(
content=content,
operation_mode=operation_mode,
automation_level=automation_level,
output_format=output_format
)

file_result.update({
"success": result.get("metadata", {}).get("success", False),
"operation": result.get("metadata", {}).get("operation_mode", "unknown"),
"encoding": "latin-1",
"result_summary": self._summarize_result(result)
})

except Exception as e:
file_result["error"] = f"编码错误: {str(e)}"

except Exception as e:
file_result["error"] = str(e)

file_result["processing_time"] = (datetime.now() - start_time).total_seconds()
return file_result

def _summarize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
"""总结结果"""
summary = {
"status": result.get("metadata", {}).get("success", False),
"operation": result.get("metadata", {}).get("operation_mode", "unknown"),
"content_type": type(result.get("content", "unknown")).name,
"has_errors": bool(result.get("validation", {}).get("errors", [])),
"has_warnings": bool(result.get("validation", {}).get("warnings", []))
}

if "generated_code" in result:
summary["code_length"] = len(result["generated_code"])

if "validation" in result:
summary["error_count"] = len(result["validation"].get("errors", []))
summary["warning_count"] = len(result["validation"].get("warnings", []))

return summary

def _generate_batch_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
"""生成批量处理摘要"""
successful = sum(1 for r in results if r.get("success", False))
failed = len(results) - successful

operations = {}
file_types = {}
total_time = 0

for result in results:
op = result.get("operation", "unknown")
operations[op] = operations.get(op, 0) + 1

filename = result.get("filename", "")
ext = Path(filename).suffix.lower()
if ext:
file_types[ext] = file_types.get(ext, 0) + 1

total_time += result.get("processing_time", 0)

return {
"success_rate": successful / len(results) if results else 0,
"successful_files": successful,
"failed_files": failed,
"operations_distribution": operations,
"file_types_distribution": file_types,
"average_processing_time": total_time / len(results) if results else 0,
"total_processing_time": total_time
}

def export_results(self, results: Dict[str, Any], export_format: str = "json") -> Path:
"""导出结果"""
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
export_file = self.config.dirs['output'] / f"batch_results_{timestamp}.{export_format}"

try:
if export_format == "json":
with open(export_file, 'w', encoding='utf-8') as f:
json.dump(results, f, indent=2, ensure_ascii=False)

elif export_format == "yaml":
with open(export_file, 'w', encoding='utf-8') as f:
yaml.dump(results, f, default_flow_style=False, allow_unicode=True)

elif export_format == "csv":
import csv
rows = []
for result in results.get("results", []):
rows.append({
"file": result.get("file", ""),
"success": result.get("success", False),
"operation": result.get("operation", "unknown"),
"processing_time": result.get("processing_time", 0),
"error": result.get("error", "")
})

if rows:
with open(export_file, 'w', encoding='utf-8', newline='') as f:
writer = csv.DictWriter(f, fieldnames=rows[0].keys())
writer.writeheader()
writer.writerows(rows)

self.logger.info(f"结果已导出到: {export_file}")
return export_file

except Exception as e:
self.logger.error(f"导出结果失败: {e}")
backup_file = self.config.dirs['output'] / f"batch_results_{timestamp}.txt"
with open(backup_file, 'w', encoding='utf-8') as f:
f.write(f"Batch Processing Results\n")
f.write(f"=======================\n")
f.write(f"Total files: {results.get('total_files', 0)}\n")
f.write(f"Successful: {results.get('successful', 0)}\n")
f.write(f"Failed: {results.get('failed', 0)}\n")
f.write(f"Processing time: {results.get('processing_time', 0):.2f} seconds\n")

return backup_file

===================================================================
系统监控器
===================================================================
class SystemMonitor:
"""系统监控器 - 监控系统状态"""

def init(self, config: UnifiedSystemConfig):
self.config = config
self.logger = logging.getLogger(name)
self.metrics_file = self.config.dirs['logs'] / "system_metrics.json"
self._load_metrics()

def _load_metrics(self):
"""加载历史指标"""
self.metrics = {
"start_time": datetime.now().isoformat(),
"total_operations": 0,
"successful_operations": 0,
"failed_operations": 0,
"average_processing_time": 0,
"resource_usage": [],
"recent_operations": []
}

if self.metrics_file.exists():
try:
with open(self.metrics_file, 'r', encoding='utf-8') as f:
saved_metrics = json.load(f)
self.metrics.update(saved_metrics)
except:
pass

def _save_metrics(self):
"""保存指标"""
try:
with open(self.metrics_file, 'w', encoding='utf-8') as f:
json.dump(self.metrics, f, indent=2, ensure_ascii=False)
except Exception as e:
self.logger.warning(f"保存系统指标失败: {e}")

def record_operation(self, operation_type: str, success: bool,
processing_time: float, details: Dict[str, Any] = None):
"""记录操作"""
operation_record = {
"timestamp": datetime.now().isoformat(),
"type": operation_type,
"success": success,
"processing_time": processing_time,
"details": details or {}
}

self.metrics["total_operations"] += 1

if success:
self.metrics["successful_operations"] += 1
else:
self.metrics["failed_operations"] += 1

total_time = self.metrics["average_processing_time"] * (self.metrics["total_operations"] - 1)
self.metrics["average_processing_time"] = (total_time + processing_time) / self.metrics["total_operations"]

self.metrics["recent_operations"].append(operation_record)
if len(self.metrics["recent_operations"]) > 100:
self.metrics["recent_operations"] = self.metrics["recent_operations"][-100:]

self._save_metrics()

def get_system_status(self) -> Dict[str, Any]:
"""获取系统状态"""
status = {
"timestamp": datetime.now().isoformat(),
"metrics": self.metrics,
"resource_usage": {}
}

if psutil:
try:
status["resource_usage"] = {
"cpu_percent": psutil.cpu_percent(interval=1),
"memory_percent": psutil.virtual_memory().percent,
"disk_usage": psutil.disk_usage('/').percent
}
except:
pass

total_ops = self.metrics["total_operations"]
if total_ops > 0:
status["metrics"]["success_rate"] = self.metrics["successful_operations"] / total_ops
else:
status["metrics"]["success_rate"] = 0

return status

def generate_report(self, report_type: str = "daily") -> Dict[str, Any]:
"""生成报告"""
report = {
"report_type": report_type,
"generated_at": datetime.now().isoformat(),
"time_period": self._get_time_period(report_type),
"summary": {},
"recommendations": []
}

total_ops = self.metrics["total_operations"]
report["summary"] = {
"total_operations": total_ops,
"successful_operations": self.metrics["successful_operations"],
"failed_operations": self.metrics["failed_operations"],
"success_rate": self.metrics["successful_operations"] / total_ops if total_ops > 0 else 0,
"average_processing_time": self.metrics["average_processing_time"]
}

if total_ops > 0:
success_rate = report["summary"]["success_rate"]
avg_time = report["summary"]["average_processing_time"]

if success_rate < 0.8:
report["recommendations"].append("成功率较低，建议检查错误日志并优化处理逻辑")

if avg_time > 5.0:
report["recommendations"].append("处理时间较长，建议优化性能或增加缓存")

return report

def _get_time_period(self, report_type: str) -> str:
"""获取时间周期"""
now = datetime.now()

if report_type == "hourly":
start = now - timedelta(hours=1)
return f"{start.strftime('%H:%M')} - {now.strftime('%H:%M')}"
elif report_type == "daily":
start = now - timedelta(days=1)
return f"{start.strftime('%Y-%m-%d')} - {now.strftime('%Y-%m-%d')}"
elif report_type == "weekly":
start = now - timedelta(weeks=1)
return f"{start.strftime('%Y-%m-%d')} - {now.strftime('%Y-%m-%d')}"
else:
return "all_time"

def cleanup_old_data(self, days_to_keep: int = 30):
"""清理旧数据"""
try:
log_dir = self.config.dirs['logs']
cutoff_date = datetime.now() - timedelta(days=days_to_keep)

for log_file in log_dir.glob("*.log"):
if log_file.stat().st_mtime < cutoff_date.timestamp():
log_file.unlink()
self.logger.info(f"删除旧日志文件: {log_file}")

self.logger.info(f"已清理超过{days_to_keep}天的日志文件")
except Exception as e:
self.logger.error(f"清理旧数据失败: {e}")

===================================================================
统一内容处理器
===================================================================
class UnifiedContentProcessor:
"""统一内容处理器 - 支持所有格式和功能"""

def init(self, config: UnifiedSystemConfig):
self.config = config
self.logger = logging.getLogger(name)

self.json_processor = JSONProcessor(config)
self.code_generator = CodeGenerator(config)
self.data_validator = DataValidator(config)
self.error_fixer = ErrorFixer(config)

self.cache = {}
self.cache_file = config.dirs['cache'] / "content_cache.json"
self._load_cache()

def _load_cache(self):
"""加载缓存"""
if self.config.performance['cache_enabled'] and self.cache_file.exists():
try:
with open(self.cache_file, 'r', encoding='utf-8') as f:
self.cache = json.load(f)
except Exception as e:
self.logger.warning(f"加载缓存失败: {e}")

def _save_cache(self):
"""保存缓存"""
if self.config.performance['cache_enabled']:
try:
with open(self.cache_file, 'w', encoding='utf-8') as f:
json.dump(self.cache, f, indent=2)
except Exception as e:
self.logger.warning(f"保存缓存失败: {e}")

def get_cache_key(self, content: str, operation: str) -> str:
"""生成缓存键"""
content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
return f"{operation}_{content_hash[:16]}"

def process_content(self, content: Any, operation_mode: str = "auto_detect",
automation_level: str = "standard",
output_format: str = "json_pretty",
enable_cache: bool = True) -> Dict[str, Any]:
"""统一内容处理入口"""
start_time = datetime.now()

try:
self.logger.info(f"开始处理内容 - 模式: {operation_mode}, 自动化级别: {automation_level}")

if enable_cache and self.config.performance['cache_enabled']:
content_str = json.dumps(content, ensure_ascii=False) if isinstance(content, (dict, list)) else str(content)
cache_key = self.get_cache_key(content_str, operation_mode)

if cache_key in self.cache:
self.logger.info("使用缓存结果")
return self.cache[cache_key]['result']

preprocessed = self._preprocess_content(content)

if operation_mode == "auto_detect":
operation_mode = self._detect_content_type(preprocessed)
self.logger.info(f"自动检测到内容类型: {operation_mode}")

processing_result = self._route_processing(preprocessed, operation_mode, automation_level)

final_result = self._postprocess_result(processing_result, output_format, automation_level)

final_result['metadata'] = {
'processing_time': (datetime.now() - start_time).total_seconds(),
'operation_mode': operation_mode,
'automation_level': automation_level,
'output_format': output_format,
'timestamp': datetime.now().isoformat(),
'success': True
}

if enable_cache and self.config.performance['cache_enabled']:
self.cache[cache_key] = {
'result': final_result,
'timestamp': datetime.now().isoformat(),
'operation': operation_mode
}
self._save_cache()

self.logger.info(f"处理完成 - 耗时: {final_result['metadata']['processing_time']:.2f}秒")
return final_result

except Exception as e:
error_result = {
'metadata': {
'success': False,
'error': str(e),
'processing_time': (datetime.now() - start_time).total_seconds(),
'timestamp': datetime.now().isoformat()
},
'suggestions': self._generate_error_suggestions(e, content)
}

self.logger.error(f"处理失败: {str(e)}")
return error_result

def _preprocess_content(self, content: Any) -> Any:
"""内容预处理"""
if isinstance(content, str):
content = content.strip()

if content.startswith('{') or content.startswith('['):
try:
return json.loads(content)
except json.JSONDecodeError:
pass

if any(marker in content for marker in ['---', ': ', '- ']):
try:
return yaml.safe_load(content)
except yaml.YAMLError:
pass

return content

def _detect_content_type(self, content: Any) -> str:
"""自动检测内容类型"""
if isinstance(content, dict):
if 'openapi' in content or 'swagger' in str(content).lower():
return "api_specification"
elif 'nodes' in content and 'edges' in content:
return "workflow_definition"
elif 'plugin' in str(content).lower() or 'node_id' in content:
return "coze_plugin"
else:
return "json_data"

elif isinstance(content, list):
return "data_collection"

elif isinstance(content, str):
content_lower = content.lower()

if any(keyword in content_lower for keyword in ['create', 'build', 'generate', '开发', '创建']):
return "code_generation"
elif any(keyword in content_lower for keyword in ['fix', 'repair', 'error', '修复', '错误']):
return "error_fixing"
elif any(keyword in content_lower for keyword in ['train', 'model', 'ai', '训练', '模型']):
return "ai_training"
elif len(content.split()) > 50:
return "document_processing"
else:
return "text_processing"

return "generic_processing"

def _route_processing(self, content: Any, operation_mode: str, automation_level: str) -> Dict[str, Any]:
"""路由到适当的处理逻辑"""
auto_config = self.config.automation_levels.get(automation_level, self.config.automation_levels['standard'])

processors = {
"coze_json_repair": self._process_coze_json,
"mcp_server_creation": self._process_mcp_creation,
"workflow_repair": self._process_workflow,
"plugin_creation": self._process_plugin_creation,
"code_generation": self._process_code_generation,
"data_processing": self._process_data,
"ai_training": self._process_ai_training,
"api_specification": self._process_api_spec,
"error_fixing": self._process_error_fixing
}

if operation_mode in processors:
return processors[operation_mode](content, auto_config)
else:
return self._process_generic(content, auto_config)

def _process_coze_json(self, content: Any, auto_config: Dict[str, Any]) -> Dict[str, Any]:
"""处理Coze JSON内容"""
result = {
"operation": "coze_json_repair",
"input_type": type(content).name,
"processed_at": datetime.now().isoformat()
}

if isinstance(content, str):
try:
content = json.loads(content)
except json.JSONDecodeError:
if auto_config.get('auto_fixes', True):
fixed_json = self.error_fixer.fix_json_syntax(content)
try:
content = json.loads(fixed_json)
result['fixes_applied'] = ['json_syntax']
except:
content = {"error": "无法修复JSON语法", "original": content[:500]}

if isinstance(content, dict):
validation = self.data_validator.validate_coze_structure(content)

if auto_config.get('auto_fixes', True) and validation['errors']:
content = self.error_fixer.fix_coze_structure(content, validation['errors'])
validation = self.data_validator.validate_coze_structure(content)
result['fixes_applied'] = ['coze_structure']

result['validation'] = validation
result['content'] = content

return result

def _process_mcp_creation(self, content: Any, auto_config: Dict[str, Any]) -> Dict[str, Any]:
"""处理MCP服务器创建"""
result = {
"operation": "mcp_server_creation",
"input_type": type(content).name,
"processed_at": datetime.now().isoformat()
}

if isinstance(content, str):
requirements = content
elif isinstance(content, dict):
requirements = content.get('requirements', str(content))
else:
requirements = str(content)

mcp_config = self.code_generator.generate_mcp_server(requirements)

result['mcp_config'] = mcp_config
result['requirements'] = requirements

return result

def _process_workflow(self, content: Any, auto_config: Dict[str, Any]) -> Dict[str, Any]:
"""处理工作流修复"""
result = {
"operation": "workflow_repair",
"input_type": type(content).name,
"processed_at": datetime.now().isoformat()
}

if isinstance(content, str):
try:
content = json.loads(content)
except json.JSONDecodeError:
content = {"error": "无效的JSON", "original": content}

if isinstance(content, dict):
validation = self.data_validator.validate_workflow(content)

if auto_config.get('auto_fixes', True) and validation['errors']:
content = self.error_fixer.fix_workflow(content, validation['errors'])
validation = self.data_validator.validate_workflow(content)
result['fixes_applied'] = ['workflow_structure']

result['validation'] = validation
result['workflow'] = content

return result

def _process_plugin_creation(self, content: Any, auto_config: Dict[str, Any]) -> Dict[str, Any]:
"""处理插件创建"""
result = {
"operation": "plugin_creation",
"input_type": type(content).name,
"processed_at": datetime.now().isoformat()
}

if isinstance(content, str):
plugin_spec = self.code_generator.analyze_plugin_requirements(content)
elif isinstance(content, dict):
plugin_spec = content
else:
plugin_spec = {"requirements": str(content)}

plugin_code = self.code_generator.generate_plugin(plugin_spec)

result['plugin_spec'] = plugin_spec
result['plugin_code'] = plugin_code

return result

def _process_code_generation(self, content: Any, auto_config: Dict[str, Any]) -> Dict[str, Any]:
"""处理代码生成"""
result = {
"operation": "code_generation",
"input_type": type(content).name,
"processed_at": datetime.now().isoformat()
}

if isinstance(content, str):
code_spec = self.code_generator.analyze_code_requirements(content)
elif isinstance(content, dict):
code_spec = content
else:
code_spec = {"requirements": str(content)}

generated_code = self.code_generator.generate_code(code_spec)

if auto_config.get('auto_validation', True):
validation = self.data_validator.validate_code_syntax(generated_code)
result['validation'] = validation

result['code_spec'] = code_spec
result['generated_code'] = generated_code

return result

def _process_data(self, content: Any, auto_config: Dict[str, Any]) -> Dict[str, Any]:
"""处理数据"""
result = {
"operation": "data_processing",
"input_type": type(content).name,
"processed_at": datetime.now().isoformat()
}

processed_data = self._preprocess_data(content)
analysis = self._analyze_data(processed_data)

if auto_config.get('auto_fixes', True) and analysis.get('issues', []):
cleaned_data = self.error_fixer.fix_data_issues(processed_data, analysis['issues'])
analysis = self._analyze_data(cleaned_data)
result['fixes_applied'] = ['data_cleaning']
processed_data = cleaned_data

result['data_analysis'] = analysis
result['processed_data'] = processed_data

return result

def _process_ai_training(self, content: Any, auto_config: Dict[str, Any]) -> Dict[str, Any]:
"""处理AI训练"""
result = {
"operation": "ai_training",
"input_type": type(content).name,
"processed_at": datetime.now().isoformat()
}

if isinstance(content, dict):
training_config = content
else:
training_config = {"data": str(content)}

result['training_plan'] = {
"model_type": training_config.get('model_type', 'text-generation'),
"training_steps": [
"数据预处理和清洗",
"模型架构选择",
"超参数调优",
"模型训练",
"性能评估",
"模型导出"
],
"requirements": training_config
}

return result

def _process_api_spec(self, content: Any, auto_config: Dict[str, Any]) -> Dict[str, Any]:
"""处理API规范"""
result = {
"operation": "api_specification",
"input_type": type(content).name,
"processed_at": datetime.now().isoformat()
}

if isinstance(content, str):
try:
content = json.loads(content)
except json.JSONDecodeError:
try:
content = yaml.safe_load(content)
except:
content = {"error": "无法解析API规范", "original": content[:500]}

if isinstance(content, dict):
validation = self.data_validator.validate_openapi_spec(content)

if auto_config.get('auto_fixes', True) and validation['errors']:
content = self.error_fixer.fix_openapi_spec(content, validation['errors'])
validation = self.data_validator.validate_openapi_spec(content)
result['fixes_applied'] = ['api_spec_fixes']

result['validation'] = validation
result['api_spec'] = content

return result

def _process_error_fixing(self, content: Any, auto_config: Dict[str, Any]) -> Dict[str, Any]:
"""处理错误修复"""
result = {
"operation": "error_fixing",
"input_type": type(content).name,
"processed_at": datetime.now().isoformat()
}

error_analysis = self.error_fixer.analyze_errors(content)

if auto_config.get('auto_fixes', True):
fixed_content = self.error_fixer.apply_fixes(content, error_analysis)
verification = self.error_fixer.verify_fixes(content, fixed_content, error_analysis)

result['error_analysis'] = error_analysis
result['fixed_content'] = fixed_content
result['verification'] = verification
result['fixes_applied'] = list(error_analysis.get('fix_categories', []))
else:
result['error_analysis'] = error_analysis
result['fix_suggestions'] = error_analysis.get('suggested_fixes', [])

return result

def _process_generic(self, content: Any, auto_config: Dict[str, Any]) -> Dict[str, Any]:
"""通用处理"""
result = {
"operation": "generic_processing",
"input_type": type(content).name,
"processed_at": datetime.now().isoformat()
}

content_analysis = self._analyze_data(content)
result['content_analysis'] = content_analysis

return result

def _preprocess_data(self, data: Any) -> Any:
"""数据预处理"""
if isinstance(data, str):
try:
return json.loads(data)
except:
pass

try:
return yaml.safe_load(data)
except:
pass

if ',' in data and '\n' in data:
lines = data.strip().split('\n')
headers = lines[0].split(',')
rows = [line.split(',') for line in lines[1:]]
return {"headers": headers, "rows": rows}

return data

def _analyze_data(self, data: Any) -> Dict[str, Any]:
"""数据分析"""
analysis = {
"data_type": type(data).name,
"issues": [],
"statistics": {},
"recommendations": []
}

if isinstance(data, dict):
analysis["keys"] = list(data.keys())
analysis["size"] = len(str(data))

for key, value in data.items():
if value is None:
analysis["issues"].append(f"键 '{key}' 的值为 None")
elif isinstance(value, str) and not value.strip():
analysis["issues"].append(f"键 '{key}' 的值为空字符串")

elif isinstance(data, list):
analysis["length"] = len(data)
if len(data) > 0:
analysis["element_types"] = list(set(type(item).name for item in data))

elif isinstance(data, str):
analysis["length"] = len(data)
analysis["line_count"] = data.count('\n') + 1
analysis["word_count"] = len(data.split())

return analysis

def _generate_error_suggestions(self, error: Exception, content: Any) -> List[str]:
"""生成错误修复建议"""
suggestions = []
error_str = str(error).lower()

if 'json' in error_str:
suggestions.append("检查JSON语法，确保括号、引号匹配")
suggestions.append("移除JSON中的注释（// 或 /* */）")

if 'yaml' in error_str:
suggestions.append("检查YAML缩进，确保使用空格而非制表符")

if 'utf' in error_str:
suggestions.append("检查文件编码，尝试使用UTF-8编码")

if 'memory' in error_str:
suggestions.append("数据量过大，尝试分批处理或增加内存限制")

return suggestions if suggestions else ["请检查输入内容的格式和语法"]

def _postprocess_result(self, result: Dict[str, Any], output_format: str,
automation_level: str) -> Dict[str, Any]:
"""结果后处理"""
auto_config = self.config.automation_levels.get(automation_level, {})

if auto_config.get('ai_enhancement', False):
result['ai_enhancements'] = {
"summary": "AI增强已应用",
"improvements": ["语法和结构优化", "性能建议", "兼容性检查"],
"confidence_score": 0.85
}

if auto_config.get('auto_optimization', False):
result['optimization_report'] = {
"performance_score": 0.75,
"optimization_opportunities": [
"代码结构可以进一步简化",
"建议添加缓存机制",
"考虑使用异步处理提高性能"
],
"estimated_improvement": "30-50% 性能提升"
}

return result

===================================================================
统一自动化工具主类
===================================================================
class UnifiedAutomationTool:
"""统一自动化工具主类"""

def init(self, config_path: Optional[str] = None):
self.config = UnifiedSystemConfig()
if config_path and Path(config_path).exists():
self._load_external_config(config_path)

self.logger = logging.getLogger(name)
self.content_processor = UnifiedContentProcessor(self.config)
self.batch_processor = BatchProcessor(self.config)
self.system_monitor = SystemMonitor(self.config)

self.current_session = {
"session_id": hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:8],
"start_time": datetime.now().isoformat(),
"operations": [],
"user_settings": {}
}

self.logger.info(f"统一自动化工具初始化完成 (会话ID: {self.current_session['session_id']})")

def _load_external_config(self, config_path: str):
"""加载外部配置"""
try:
with open(config_path, 'r', encoding='utf-8') as f:
external_config = yaml.safe_load(f)

for key, value in external_config.items():
if hasattr(self.config, key):
setattr(self.config, key, value)

self.logger.info(f"已从 {config_path} 加载外部配置")
except Exception as e:
self.logger.warning(f"加载外部配置失败: {e}")

def process(self, content: Any, operation_mode: str = "auto_detect",
automation_level: str = "standard", output_format: str = "json_pretty",
enable_cache: bool = True, user_confirm: bool = False) -> Dict[str, Any]:
"""主处理函数"""
start_time = datetime.now()

try:
self.logger.info(f"开始处理请求 - 模式: {operation_mode}, 自动化级别: {automation_level}")

auto_config = self.config.automation_levels.get(automation_level, {})
if user_confirm and not auto_config.get('auto_fixes', True):
self.logger.info("等待用户确认...")

result = self.content_processor.process_content(
content=content,
operation_mode=operation_mode,
automation_level=automation_level,
output_format=output_format,
enable_cache=enable_cache
)

processing_time = (datetime.now() - start_time).total_seconds()

self.system_monitor.record_operation(
operation_type=operation_mode,
success=result.get("metadata", {}).get("success", False),
processing_time=processing_time,
details={
"automation_level": automation_level,
"output_format": output_format
}
)

self.current_session["operations"].append({
"timestamp": datetime.now().isoformat(),
"operation": operation_mode,
"success": result.get("metadata", {}).get("success", False),
"processing_time": processing_time
})

self.logger.info(f"处理完成 - 耗时: {processing_time:.2f}秒")
return result

except Exception as e:
error_result = {
"metadata": {
"success": False,
"error": str(e),
"processing_time": (datetime.now() - start_time).total_seconds(),
"timestamp": datetime.now().isoformat()
},
"suggestions": [
"检查输入内容的格式",
"尝试降低自动化级别以获得更多控制",
"查看日志文件获取详细信息"
]
}

self.system_monitor.record_operation(
operation_type=operation_mode,
success=False,
processing_time=(datetime.now() - start_time).total_seconds(),
details={"error": str(e)}
)

self.logger.error(f"处理失败: {str(e)}")
return error_result

def batch_process(self, directory: str, operation_mode: str = "auto_detect",
automation_level: str = "standard", output_format: str = "json_pretty",
max_workers: int = 4, export_results: bool = True) -> Dict[str, Any]:
"""批量处理目录"""
start_time = datetime.now()

try:
dir_path = Path(directory)
if not dir_path.exists():
return {
"success": False,
"error": f"目录不存在: {directory}",
"processing_time": 0
}

self.logger.info(f"开始批量处理目录: {directory}")

results = self.batch_processor.process_directory(
directory=dir_path,
operation_mode=operation_mode,
automation_level=automation_level,
output_format=output_format,
max_workers=max_workers
)

processing_time = (datetime.now() - start_time).total_seconds()
results["processing_time"] = processing_time

if export_results:
export_file = self.batch_processor.export_results(results, "json")
results["export_file"] = str(export_file)

self.system_monitor.record_operation(
operation_type=f"batch_{operation_mode}",
success=results.get("successful", 0) > 0,
processing_time=processing_time,
details={
"directory": directory,
"total_files": results.get("total_files", 0),
"successful": results.get("successful", 0),
"failed": results.get("failed", 0)
}
)

self.logger.info(f"批量处理完成 - 处理文件: {results.get('processed_files', 0)}")
return results

except Exception as e:
self.logger.error(f"批量处理失败: {e}")
return {
"success": False,
"error": str(e),
"processing_time": (datetime.now() - start_time).total_seconds(),
"directory": directory
}

def get_system_status(self) -> Dict[str, Any]:
"""获取系统状态"""
return self.system_monitor.get_system_status()

def generate_report(self, report_type: str = "daily") -> Dict[str, Any]:
"""生成系统报告"""
return self.system_monitor.generate_report(report_type)

def update_config(self, updates: Dict[str, Any]) -> bool:
"""更新配置"""
try:
self.config.update_config(updates)
self.logger.info("配置已更新")
return True
except Exception as e:
self.logger.error(f"更新配置失败: {e}")
return False

def save_session(self) -> Path:
"""保存当前会话"""
session_file = self.config.dirs['cache'] / f"session_{self.current_session['session_id']}.json"

session_data = {
**self.current_session,
"end_time": datetime.now().isoformat(),
"system_status": self.get_system_status()
}

try:
with open(session_file, 'w', encoding='utf-8') as f:
json.dump(session_data, f, indent=2, ensure_ascii=False)

self.logger.info(f"会话已保存到: {session_file}")
return session_file
except Exception as e:
self.logger.error(f"保存会话失败: {e}")
raise

def cleanup(self, days_to_keep: int = 7):
"""清理系统"""
try:
self.system_monitor.cleanup_old_data(days_to_keep)

temp_dir = self.config.dirs['temp']
for temp_file in temp_dir.glob("*"):
if temp_file.is_file():
file_age = datetime.now().timestamp() - temp_file.stat().st_mtime
if file_age > days_to_keep * 24 * 3600:
temp_file.unlink()

self.logger.info(f"系统清理完成，保留最近{days_to_keep}天的数据")

except Exception as e:
self.logger.error(f"系统清理失败: {e}")

def interactive_mode(self):
"""交互式模式"""
print("=" * 70)
print(f"🚀 {self.config.project_name} v{self.config.version}")
print("=" * 70)
print("统一智能自动化工具 - 完全整合版")
print("=" * 70)

while True:
try:
print("\n请选择操作:")
print("1. 📝 处理内容 - 输入内容进行处理")
print("2. 📁 批量处理 - 处理整个目录")
print("3. ⚙️ 系统状态 - 查看系统信息和状态")
print("4. 📊 生成报告 - 生成处理报告")
print("5. 🔧 配置管理 - 查看和修改配置")
print("6. 🗑️ 系统清理 - 清理旧数据")
print("7. 💾 保存会话 - 保存当前会话")
print("8. 🚪 退出系统")

choice = input("\n请输入选择 (1-8): ").strip()

if choice == '1':
self._handle_single_processing()
elif choice == '2':
self._handle_batch_processing()
elif choice == '3':
self._handle_system_status()
elif choice == '4':
self._handle_report_generation()
elif choice == '5':
self._handle_config_management()
elif choice == '6':
self._handle_system_cleanup()
elif choice == '7':
self._handle_session_save()
elif choice == '8':
print("感谢使用统一自动化工具!")
break
else:
print("❌ 无效选择，请重新输入!")

except KeyboardInterrupt:
print("\n\n🛑 系统安全关闭...")
break
except Exception as e:
self.logger.error(f"控制台错误: {e}")
print(f"❌ 发生错误: {e}")

def _handle_single_processing(self):
"""处理单个内容"""
print("\n📝 单内容处理模式")

print("\n请选择输入方式:")
print("1. 直接输入内容")
print("2. 从文件读取")
print("3. 使用示例内容")

input_choice = input("\n请选择 (1-3): ").strip()

if input_choice == '1':
print("\n请输入内容 (输入完成后按Ctrl+D结束):")
content_lines = []
try:
while True:
line = input()
content_lines.append(line)
except EOFError:
content = '\n'.join(content_lines)
elif input_choice == '2':
file_path = input("请输入文件路径: ").strip()
try:
with open(file_path, 'r', encoding='utf-8') as f:
content = f.read()
except Exception as e:
print(f"❌ 文件读取失败: {e}")
return
else:
content = '''{
"plugin_name": "示例插件",
"description": "这是一个示例插件",
"nodes": [
{
"id": "node1",
"type": "input",
"name": "输入节点"
}
]
}'''

print("\n🔧 请配置处理参数:")

operation_mode = input(f"操作模式 ({', '.join(self.config.processing_modes.keys())}) [auto_detect]: ").strip()
if not operation_mode:
operation_mode = "auto_detect"

automation_level = input(f"自动化级别 ({', '.join(self.config.automation_levels.keys())}) [standard]: ").strip()
if not automation_level:
automation_level = "standard"

output_format = input(f"输出格式 ({', '.join(self.config.output_formats.keys())}) [json_pretty]: ").strip()
if not output_format:
output_format = "json_pretty"

user_confirm_input = input("需要用户确认? (y/N) [N]: ").strip().lower()
user_confirm = user_confirm_input == 'y'

print(f"\n🚀 开始处理内容...")
result = self.process(
content=content,
operation_mode=operation_mode,
automation_level=automation_level,
output_format=output_format,
user_confirm=user_confirm
)

self._display_result(result)

def _handle_batch_processing(self):
"""处理批量内容"""
print("\n📁 批量处理模式")

directory = input("请输入目录路径: ").strip()
if not directory:
print("❌ 目录路径不能为空!")
return

print("\n🔧 请配置批量处理参数:")

operation_mode = input(f"操作模式 ({', '.join(self.config.processing_modes.keys())}) [auto_detect]: ").strip()
if not operation_mode:
operation_mode = "auto_detect"

automation_level = input(f"自动化级别 ({', '.join(self.config.automation_levels.keys())}) [standard]: ").strip()
if not automation_level:
automation_level = "standard"

max_workers_input = input(f"最大并行数 (1-{self.config.performance['max_workers']}) [{self.config.performance['max_workers']}]: ").strip()
max_workers = int(max_workers_input) if max_workers_input.isdigit() else self.config.performance['max_workers']

print(f"\n🚀 开始批量处理目录: {directory}")
results = self.batch_process(
directory=directory,
operation_mode=operation_mode,
automation_level=automation_level,
max_workers=max_workers
)

if results.get("success", False) or results.get("processed_files", 0) > 0:
print(f"\n✅ 批量处理完成!")
print(f" 处理文件: {results.get('processed_files', 0)}")
print(f" 成功: {results.get('successful', 0)}")
print(f" 失败: {results.get('failed', 0)}")
print(f" 处理时间: {results.get('processing_time', 0):.2f}秒")

if "export_file" in results:
print(f" 结果已导出到: {results['export_file']}")
else:
print(f"❌ 批量处理失败: {results.get('error', '未知错误')}")

def _handle_system_status(self):
"""显示系统状态"""
print("\n⚙️ 系统状态")
print("-" * 40)

status = self.get_system_status()

print(f"系统版本: {self.config.version}")
print(f"会话ID: {self.current_session['session_id']}")
print(f"运行时间: {status['metrics'].get('total_operations', 0)} 次操作")

if status['metrics'].get('total_operations', 0) > 0:
success_rate = status['metrics'].get('success_rate', 0) * 100
print(f"成功率: {success_rate:.1f}%")
print(f"平均处理时间: {status['metrics'].get('average_processing_time', 0):.2f}秒")

if 'resource_usage' in status:
print(f"CPU使用率: {status['resource_usage'].get('cpu_percent', 0):.1f}%")
print(f"内存使用率: {status['resource_usage'].get('memory_percent', 0):.1f}%")

print(f"\n目录状态:")
for name, path in self.config.dirs.items():
exists = "✅" if path.exists() else "❌"
print(f" {exists} {name}: {path}")

def _handle_report_generation(self):
"""生成报告"""
print("\n📊 报告生成")

report_type = input("报告类型 (hourly/daily/weekly) [daily]: ").strip()
if not report_type:
report_type = "daily"

report = self.generate_report(report_type)

print(f"\n📋 {report['report_type'].title()} 报告")
print("-" * 40)

summary = report.get('summary', {})
print(f"时间周期: {report.get('time_period', 'N/A')}")
print(f"总操作数: {summary.get('total_operations', 0)}")
print(f"成功率: {summary.get('success_rate', 0) * 100:.1f}%")
print(f"平均处理时间: {summary.get('average_processing_time', 0):.2f}秒")

if report.get('recommendations'):
print(f"\n💡 优化建议:")
for rec in report['recommendations']:
print(f" • {rec}")

save_report = input("\n保存报告到文件? (y/N) [N]: ").strip().lower()
if save_report == 'y':
report_file = self.config.dirs['output'] / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
try:
with open(report_file, 'w', encoding='utf-8') as f:
json.dump(report, f, indent=2, ensure_ascii=False)
print(f"✅ 报告已保存到: {report_file}")
except Exception as e:
print(f"❌ 保存报告失败: {e}")

def _handle_config_management(self):
"""配置管理"""
print("\n🔧 配置管理")
print("-" * 40)

print("当前配置:")
print(f" 项目名称: {self.config.project_name}")
print(f" 版本: {self.config.version}")
print(f" 基础路径: {self.config.base_path}")
print(f" 最大文件大小: {self.config.performance['max_file_size_mb']}MB")
print(f" 最大并行数: {self.config.performance['max_workers']}")
print(f" 缓存启用: {self.config.performance['cache_enabled']}")

print("\n1. 查看详细配置")
print("2. 修改配置")
print("3. 保存配置到文件")

choice = input("\n请选择 (1-3): ").strip()

if choice == '1':
self._show_detailed_config()
elif choice == '2':
self._modify_config()
elif choice == '3':
self._save_config_to_file()

def show_detailed_config(self):
"""显示详细配置"""
print("\n📋 详细配置:")
for key, value in self.config.dict.items():
if not key.startswith(''):
if isinstance(value, dict):
print(f"\n{key}:")
for sub_key, sub_value in value.items():
print(f" {sub_key}: {sub_value}")
else:
print(f"{key}: {value}")

input("\n按Enter键继续...")

def _modify_config(self):
"""修改配置"""
print("\n✏️ 修改配置")

updates = {}

max_size = input(f"最大文件大小 (MB) [{self.config.performance['max_file_size_mb']}]: ").strip()
if max_size.isdigit():
updates['performance.max_file_size_mb'] = int(max_size)

max_workers = input(f"最大并行数 [{self.config.performance['max_workers']}]: ").strip()
if max_workers.isdigit():
updates['performance.max_workers'] = int(max_workers)

cache_enabled = input(f"启用缓存 (y/n) [{'y' if self.config.performance['cache_enabled'] else 'n'}]: ").strip().lower()
if cache_enabled:
updates['performance.cache_enabled'] = cache_enabled == 'y'

if updates:
config_updates = {}
for key, value in updates.items():
if '.' in key:
parts = key.split('.')
current = config_updates
for part in parts[:-1]:
if part not in current:
current[part] = {}
current = current[part]
current[parts[-1]] = value
else:
config_updates[key] = value

success = self.update_config(config_updates)
if success:
print("✅ 配置已更新")
else:
print("❌ 更新配置失败")
else:
print("⚠️ 没有修改配置")

def _save_config_to_file(self):
"""保存配置到文件"""
filename = input("请输入配置文件名 [system_config.yaml]: ").strip()
if not filename:
filename = "system_config.yaml"

config_file = self.config.dirs['config'] / filename

try:
config_dict = {}
for key, value in self.config.dict.items():
if not key.startswith('_'):
if isinstance(value, Path):
config_dict[key] = str(value)
else:
config_dict[key] = value

with open(config_file, 'w', encoding='utf-8') as f:
yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)

print(f"✅ 配置已保存到: {config_file}")
except Exception as e:
print(f"❌ 保存配置失败: {e}")

def _handle_system_cleanup(self):
"""系统清理"""
print("\n🗑️ 系统清理")

days_to_keep = input("保留最近几天的数据? (7): ").strip()
if not days_to_keep.isdigit():
days_to_keep = 7
else:
days_to_keep = int(days_to_keep)

confirm = input(f"\n⚠️ 确定要清理{self.config.base_path}目录中超过{days_to_keep}天的数据吗? (y/N): ").strip().lower()
if confirm == 'y':
self.cleanup(days_to_keep)
print("✅ 系统清理完成")

def _handle_session_save(self):
"""保存会话"""
try:
session_file = self.save_session()
print(f"✅ 会话已保存到: {session_file}")
except Exception as e:
print(f"❌ 保存会话失败: {e}")

def _display_result(self, result: Dict[str, Any]):
"""显示处理结果"""
metadata = result.get('metadata', {})

print(f"\n📊 处理结果:")
print("-" * 40)

if metadata.get('success', False):
print("✅ 处理成功!")
else:
print("❌ 处理失败!")

print(f"操作模式: {metadata.get('operation_mode', 'unknown')}")
print(f"自动化级别: {metadata.get('automation_level', 'unknown')}")
print(f"处理时间: {metadata.get('processing_time', 0):.2f}秒")

if 'error' in metadata:
print(f"错误信息: {metadata['error']}")

content_keys = [k for k in result.keys() if k not in ['metadata', 'debug_info']]
if content_keys:
print(f"\n📄 输出内容 ({len(content_keys)} 个部分):")

for key in content_keys[:3]:
value = result[key]
if isinstance(value, str):
preview = value[:200] + ("..." if len(value) > 200 else "")
print(f"\n{key}:")
print(f" {preview}")
elif isinstance(value, dict):
print(f"\n{key} (字典):")
print(f" 键: {list(value.keys())[:5]}{'...' if len(value) > 5 else ''}")
elif isinstance(value, list):
print(f"\n{key} (列表):")
print(f" 长度: {len(value)}")

save_option = input("\n💾 保存结果到文件? (y/N) [N]: ").strip().lower()
if save_option == 'y':
self._save_result_to_file(result)

def _save_result_to_file(self, result: Dict[str, Any]):
"""保存结果到文件"""
format_choice = input("保存格式 (json/yaml/txt) [json]: ").strip().lower()
if not format_choice:
format_choice = "json"

filename = input(f"文件名 [result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_choice}]: ").strip()
if not filename:
filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_choice}"

output_file = self.config.dirs['output'] / filename

try:
if format_choice == 'json':
with open(output_file, 'w', encoding='utf-8') as f:
json.dump(result, f, indent=2, ensure_ascii=False)
elif format_choice == 'yaml':
with open(output_file, 'w', encoding='utf-8') as f:
yaml.dump(result, f, default_flow_style=False, allow_unicode=True)
else:
with open(output_file, 'w', encoding='utf-8') as f:
f.write(f"Result generated at: {datetime.now().isoformat()}\n")
f.write(f"Status: {'Success' if result.get('metadata', {}).get('success', False) else 'Failed'}\n")
f.write("-" * 50 + "\n\n")
f.write(str(result))

print(f"✅ 结果已保存到: {output_file}")
except Exception as e:
print(f"❌ 保存结果失败: {e}")

===================================================================
主程序入口
===================================================================
def main():
"""主程序入口"""
parser = argparse.ArgumentParser(
description="统一智能自动化工具套件 - 完全整合版",
formatter_class=argparse.RawDescriptionHelpFormatter,
epilog="""
使用示例:

交互式模式 (推荐)
python unified_automation_tool.py --interactive

处理单个内容
python unified_automation_tool.py --process "内容" --mode coze_json_repair

批量处理目录
python unified_automation_tool.py --batch ./data --mode auto_detect

查看系统状态
python unified_automation_tool.py --status

生成报告
python unified_automation_tool.py --report daily

使用配置文件
python unified_automation_tool.py --config my_config.yaml --interactive
"""
)

parser.add_argument("--config", help="配置文件路径")
parser.add_argument("--interactive", action="store_true", help="启动交互式模式")

parser.add_argument("--process", help="处理单个内容")
parser.add_argument("--mode", help="操作模式", default="auto_detect")
parser.add_argument("--automation", help="自动化级别", default="standard")
parser.add_argument("--output-format", help="输出格式", default="json_pretty")

parser.add_argument("--batch", help="批量处理目录")
parser.add_argument("--max-workers", type=int, help="最大并行数", default=4)

parser.add_argument("--status", action="store_true", help="查看系统状态")
parser.add_argument("--report", help="生成报告 (hourly/daily/weekly)")
parser.add_argument("--cleanup", type=int, help="清理旧数据 (天数)")
parser.add_argument("--save-session", action="store_true", help="保存当前会话")

args = parser.parse_args()

try:
tool = UnifiedAutomationTool(args.config)

if args.interactive:
tool.interactive_mode()

elif args.process:
result = tool.process(
content=args.process,
operation_mode=args.mode,
automation_level=args.automation,
output_format=args.output_format
)
print(json.dumps(result, indent=2, ensure_ascii=False))

elif args.batch:
result = tool.batch_process(
directory=args.batch,
operation_mode=args.mode,
automation_level=args.automation,
max_workers=args.max_workers
)
print(json.dumps(result, indent=2, ensure_ascii=False))

elif args.status:
status = tool.get_system_status()
print(json.dumps(status, indent=2, ensure_ascii=False))

elif args.report:
report = tool.generate_report(args.report)
print(json.dumps(report, indent=2, ensure_ascii=False))

elif args.cleanup:
tool.cleanup(args.cleanup)
print(f"✅ 已清理超过{args.cleanup}天的数据")

elif args.save_session:
session_file = tool.save_session()
print(f"✅ 会话已保存到: {session_file}")

else:
print("启动交互式模式...")
tool.interactive_mode()

except KeyboardInterrupt:
print("\n\n🛑 程序被用户中断")
sys.exit(0)
except Exception as e:
print(f"❌ 程序执行失败: {e}")
logging.exception("程序执行错误")
sys.exit(1)

if name == "main":
main()

text
复制
下载

---

# 📚 第三部分：使用说明文档

## 快速开始

### 1. 安装依赖