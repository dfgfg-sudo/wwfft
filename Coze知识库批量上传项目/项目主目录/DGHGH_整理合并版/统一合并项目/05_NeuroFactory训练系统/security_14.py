"""
import { CozeAPI } from '@coze/api';

const apiClient = new CozeAPI({
  token: '这里填你生成的API Key', // ⚠️ 安全提示：生产环境不应暴露在前端
  baseURL: 'https://api.coze.cn' // 国内用户使用
});

async function callMyWorkflow(userInput) {
  const res = await apiClient.workflows.runs.create({
    workflow_id: '这里填你的工作流ID',
    parameters: { "input": userInput }
  });
  console.log(res);
  return res;
}
"""
