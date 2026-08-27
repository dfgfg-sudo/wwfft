from flask import Flask, request, jsonify
import yaml, zipfile, json, tempfile, os
import requests

app = Flask(__name__)

@app.route('/import-workflow', methods=['POST'])
def import_workflow():
    try:
        # 1. 接收并解析数据
        data = request.json
        file_content = data.get('config_file')
        file_format = data.get('format', 'json')
        
        # 2. 根据格式解析
        workflow_config = None
        
        if file_format == 'zip':
            # 创建临时文件处理ZIP
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                tmp.write(file_content.encode() if isinstance(file_content, str) else file_content)
                zip_path = tmp.name
            
            try:
                with zipfile.ZipFile(zip_path, 'r') as z:
                    # 查找配置文件
                    config_files = [f for f in z.namelist() 
                                  if f.endswith(('.json', '.yaml', '.yml'))]
                    if not config_files:
                        return jsonify({'error': 'ZIP中未找到配置文件'}), 400
                    
                    # 读取第一个配置文件
                    with z.open(config_files[0]) as f:
                        content = f.read().decode('utf-8')
                        
                        if config_files[0].endswith('.json'):
                            workflow_config = json.loads(content)
                        else:
                            workflow_config = yaml.safe_load(content)
            finally:
                os.unlink(zip_path)
                
        elif file_format in ['yaml', 'yml']:
            workflow_config = yaml.safe_load(file_content)
        else:  # json
            workflow_config = json.loads(file_content)
        
        # 3. 转换为Coze API格式（需根据实际API调整）
        coze_payload = convert_to_coze_format(workflow_config)
        
        # 4. 调用Coze API（需要有效的API密钥）
        coze_api_key = os.environ.get('COZE_API_KEY')
        workspace_id = data.get('workspace_id', 'default')
        
        headers = {
            'Authorization': f'Bearer {coze_api_key}',
            'Content-Type': 'application/json'
        }
        
        # 注意：以下URL和参数需要根据Coze实际API调整
        response = requests.post(
            f'https://api.coze.cn/v1/workspaces/{workspace_id}/workflows',
            json=coze_payload,
            headers=headers
        )
        
        if response.status_code == 201:
            result = response.json()
            return jsonify({
                'success': True,
                'workflow_id': result.get('id'),
                'workflow_name': result.get('name'),
                'message': '工作流创建成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'API调用失败: {response.status_code}',
                'details': response.text
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }), 400

def convert_to_coze_format(user_config):
    """
    将用户配置转换为Coze API所需的格式
    这是最复杂的部分，需要深入研究Coze工作流的数据结构
    """
    # 基础结构（需要根据实际API文档调整）
    base_structure = {
        "name": user_config.get("name", "导入的工作流"),
        "description": user_config.get("description", ""),
        "nodes": [],  # 需要将用户节点映射为Coze节点格式
        "edges": [],  # 节点连接关系
        "variables": user_config.get("variables", {}),
        "version": "1.0"
    }
    
    # 这里需要编写具体的转换逻辑
    # 例如：映射不同类型的节点，处理连接关系等
    
    return base_structure

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)