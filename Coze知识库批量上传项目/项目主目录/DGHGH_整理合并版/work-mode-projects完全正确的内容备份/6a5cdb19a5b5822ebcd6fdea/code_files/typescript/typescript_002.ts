const result = await run({
  user_input: `{
    name: 测试插件,
    description: "一个需要修复的插件",
    inputs: [
      {name: "city", type: "string"},
      {name: "country", type: "string"}
    ],
    outputs: [{name: result, type: object}]
  }`,
  operation_mode: "quick_fix",
  repair_depth: "comprehensive"
});