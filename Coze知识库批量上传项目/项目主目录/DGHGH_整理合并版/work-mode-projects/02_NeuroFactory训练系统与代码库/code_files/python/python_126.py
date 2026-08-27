# 扩展元代码生成器支持多需求
async def main(params):
    requirements = params.get("requirements_list", [])
    
    all_codes = {}
    for i, req in enumerate(requirements):
        code = generate_code_from_requirement(req)
        all_codes[f"function_{i+1}"] = {
            "code": code,
            "name": f"功能_{i+1}",
            "requirements": req
        }
    
    return {"generated_functions": all_codes}