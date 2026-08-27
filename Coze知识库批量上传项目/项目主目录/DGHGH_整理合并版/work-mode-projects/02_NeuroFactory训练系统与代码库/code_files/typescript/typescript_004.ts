const result = await run({
  user_input: `
    {"name": "插件A", "inputs": [{"name": "param1"}]}
    {"name": "插件B", "inputs": [{"name": "param2", "type": "number"}]}
  `,
  operation_mode: "batch_process"
});