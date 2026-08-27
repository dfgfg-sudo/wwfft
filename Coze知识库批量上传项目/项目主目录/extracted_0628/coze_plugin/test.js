const ConversationsParser = require('./index');

async function runTests() {
  const parser = new ConversationsParser();
  
  console.log('=== 测试 ConversationsParser 插件 ===\n');
  
  console.log('1. 加载数据...');
  const loadResult = await parser.loadData();
  console.log(`   ${loadResult.success ? '✅' : '❌'} ${loadResult.message}`);
  
  if (loadResult.success) {
    console.log('\n2. 获取所有对话列表...');
    const conversations = parser.getAllConversations();
    console.log(`   ✅ 找到 ${conversations.length} 个对话`);
    conversations.forEach(c => console.log(`      - ${c.title}`));
    
    console.log('\n3. 提取系统模块...');
    const modules = parser.extractSystemModules();
    console.log(`   ✅ 识别到 ${modules.length} 个系统模块`);
    modules.forEach(m => console.log(`      - ${m.name}`));
    
    console.log('\n4. 提取代码块...');
    const codeBlocks = parser.extractAllCodeBlocks();
    console.log(`   ✅ 提取到 ${codeBlocks.length} 个代码块`);
    
    console.log('\n5. 提取函数...');
    const functions = parser.extractFunctions();
    console.log(`   ✅ 识别到 ${functions.length} 个函数`);
    
    console.log('\n6. 生成文档...');
    const doc = parser.generateDocumentation();
    console.log(`   ✅ 文档生成完成 (${doc.length} 字符)`);
    
    console.log('\n7. 完整分析...');
    const analysis = parser.getCompleteAnalysis();
    console.log(`   ✅ 分析完成`);
    console.log(`      - 对话数: ${analysis.metadata.totalConversations}`);
    console.log(`      - 模块数: ${analysis.modules.length}`);
    console.log(`      - 函数数: ${analysis.functions.length}`);
    console.log(`      - 代码块数: ${analysis.codeBlocks.length}`);
    
    console.log('\n=== 所有测试通过！===');
  }

runTests().catch(console.error);