// Coze 插件测试脚本
const plugins = require('./coze_plugins_complete_fixed.js');
const DeepSeekConversationOrganizer = plugins.DeepSeekConversationOrganizer;

async function test() {
  let passed = 0;
  let failed = 0;

  function check(name, condition) {
    if (condition) { console.log('  [PASS] ' + name); passed++; }
    else { console.log('  [FAIL] ' + name); failed++; }
  }

  // Test 1: batch_upload
  console.log('\n=== Test 1: batch_upload ===');
  const r1 = await plugins.batch_upload.handler({input: {}});
  check('缺少参数返回失败', r1.success === false);

  // Test 2: DeepSeekAIFactoryUltimate
  console.log('\n=== Test 2: DeepSeekAIFactoryUltimate ===');
  const r2 = await plugins.DeepSeekAIFactoryUltimate.handler({input: {user_input: '帮我分析行业趋势'}});
  check('路由到 industry_analysis', r2.module === 'industry_analysis');

  // Test 3: CozeSmartRouter
  console.log('\n=== Test 3: CozeSmartRouter ===');
  const r3 = await plugins.CozeSmartRouter.handler({input: {user_input: '修复代码错误'}});
  check('路由到 code_fix', r3.module === 'code_fix');

  // Test 4: CozeUltimateSuperPlugin
  console.log('\n=== Test 4: CozeUltimateSuperPlugin ===');
  const r4 = await plugins.CozeUltimateSuperPlugin.handler({input: {user_input: '创建一个视频剪辑'}});
  check('路由到 multimedia', r4.module === 'multimedia');

  // Test 5: DeepSeekConversationOrganizer
  console.log('\n=== Test 5: DeepSeekConversationOrganizer ===');
  const r5 = await plugins.DeepSeekConversationOrganizer.handler({input: {action: 'get_statistics'}});
  check('统计查询成功', r5.total_conversations !== undefined);

  // Test 6: NeuroConsciousnessCore
  console.log('\n=== Test 6: NeuroConsciousnessCore ===');
  const r6 = await plugins.NeuroConsciousnessCore.handler({input: {user_input: '机械臂搬运10kg到A工位'}});
  check('神经决策成功', r6.success === true);

  // Test 7: CozeFullSceneAutomation
  console.log('\n=== Test 7: CozeFullSceneAutomation ===');
  const r7 = await plugins.CozeFullSceneAutomation.handler({input: {userInput: '分析数据趋势'}});
  check('全场景自动化成功', r7.processResult.success === true);

  // Test 8: JSON修复
  console.log('\n=== Test 8: JSON修复 ===');
  const r8 = DeepSeekConversationOrganizer.jsonRepair("{'name': 'test'}");
  check('JSON修复成功', r8.success === true);

  // Test 9: 统一入口路由
  console.log('\n=== Test 9: 统一入口 ===');
  const r9 = await plugins.handler({input: {plugin: 'CozeSmartRouter', user_input: '生成一个工作流'}});
  check('路由到 workflow', r9.module === 'workflow');

  // Test 10: 缺少参数
  console.log('\n=== Test 10: 参数校验 ===');
  const r10 = await plugins.handler({input: {}});
  check('缺少参数返回失败', r10.success === false);

  console.log('\n=============================');
  console.log('测试结果: ' + passed + ' 通过, ' + failed + ' 失败');
  console.log('=============================');
  return failed === 0;
}

test().then(function(success) {
  process.exit(success ? 0 : 1);
}).catch(function(err) {
  console.error(err);
  process.exit(1);
});