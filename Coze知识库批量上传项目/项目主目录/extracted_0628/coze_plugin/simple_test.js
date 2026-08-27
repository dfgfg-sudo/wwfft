const ConversationsParser = require('./index');

async function main() {
  console.log('=== ConversationsParser Plugin Test ===\n');
  
  const parser = new ConversationsParser();
  
  console.log('1. Loading data...');
  const loadResult = await parser.loadData();
  console.log(`   ${loadResult.success ? '✅' : '❌'} ${loadResult.message}`);
  
  if (loadResult.success) {
    console.log(`\n2. Getting conversation list...`);
    const convs = parser.getAllConversations();
    console.log(`   ✅ Found ${convs.length} conversations:`);
    convs.forEach(c => console.log(`      - ${c.title}`));
    
    console.log('\n3. Extracting system modules...');
    const modules = parser.extractSystemModules();
    console.log(`   ✅ Found ${modules.length} system modules:`);
    modules.forEach(m => console.log(`      - ${m.name}`));
    
    console.log('\n4. Extracting code blocks...');
    const codeBlocks = parser.extractAllCodeBlocks();
    console.log(`   ✅ Found ${codeBlocks.length} code blocks`);
    
    console.log('\n5. Extracting functions...');
    const funcs = parser.extractFunctions();
    console.log(`   ✅ Found ${funcs.length} unique functions`);
    
    console.log('\n6. Running all modules...');
    const results = parser.runAllModules();
    console.log(`   ✅ Module execution results:`);
    results.forEach(r => {
      const status = r.status === 'success' ? '✅' : '❌';
      console.log(`      ${status} ${r.name}: ${r.status === 'success' ? `${r.classes} classes, ${r.methods} methods` : r.error}`);
    });
    
    console.log('\n=== Plugin is working correctly! ===');
  }

main().catch(console.error);