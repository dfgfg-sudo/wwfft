import { CozeAPI } from '@coze/api';

const apiClient = new CozeAPI({
  token: '你的API Key', // ⚠️ 生产环境禁止暴露在前端
  baseURL: 'https://api.coze.cn'
});

async function callMyWorkflow(userInput) {
  const res = await apiClient.workflows.runs.create({
    workflow_id: '你的工作流ID',
    parameters: { "input": userInput }
  });
  return res;
}