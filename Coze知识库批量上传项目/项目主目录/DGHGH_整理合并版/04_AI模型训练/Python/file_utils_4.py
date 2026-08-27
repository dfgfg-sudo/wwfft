import json
from jsonschema import validate, ValidationError

def validate_tool_schema(tool):
    schema = tool.get("input_params", {})
    if not isinstance(schema, dict):
        return False, "input_params 不是字典"
    return True, "OK"

def check_url_format(base_url, path):
    if base_url.endswith("/"):
        return False, "基础 URL 不能以 / 结尾"
    if not path.startswith("/"):
        return False, "工具路径必须以 / 开头"
    return True, "OK"

with open("plugins_full_dump.json", "r", encoding="utf-8") as f:
    data = json.load(f)

error_report = {}
for pid, plugin in data.items():
    errors = []
    for tool in plugin.get("data", {}).get("tools", []):
        valid, msg = validate_tool_schema(tool)
        if not valid:
            errors.append(f"工具 {tool.get('name')} Schema 错误: {msg}")
        base = plugin.get("data", {}).get("base_url", "")
        path = tool.get("path", "")
        valid, msg = check_url_format(base, path)
        if not valid:
            errors.append(f"工具 {tool.get('name')} URL 错误: {msg}")
    if errors:
        error_report[pid] = errors

with open("error_report.json", "w", encoding="utf-8") as f:
    json.dump(error_report, f, ensure_ascii=False, indent=2)