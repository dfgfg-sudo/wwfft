// 测试示例
const ImporterNode = require('./src/nodes/importer-node');

describe('WorkflowImporterNode', () => {
  let node;
  
  beforeEach(() => {
    node = new ImporterNode();
  });
  
  test('应该正确解析JSON文件', async () => {
    const mockInput = {
      configFile: {
        name: 'workflow.json',
        content: JSON.stringify({
          name: '测试工作流',
          nodes: [{ id: '1', type: 'start' }]
        })
      }
    };
    
    const result = await node.execute(mockInput);
    expect(result.success).toBe(true);
  });
  
  test('应该拒绝无效格式', async () => {
    const mockInput = {
      configFile: {
        name: 'workflow.txt',
        content: '无效内容'
      }
    };
    
    await expect(node.execute(mockInput))
      .rejects
      .toThrow('不支持的文件格式');
  });
});