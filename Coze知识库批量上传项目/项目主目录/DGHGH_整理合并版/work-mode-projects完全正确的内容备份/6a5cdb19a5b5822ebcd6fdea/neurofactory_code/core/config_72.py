async def main_demo():
    print("="*70)
    print("🚀 Coze 全能智能自动化超级中枢 - 完整演示")
    print("="*70)

    # 1. 创建工作流系统
    system = CozeWorkflowSystem()
    user_input = """
工作流名称: 订单智能处理
描述: 自动验证、支付、发货通知
steps:
  - id: validate
    name: 验证订单
    type: condition_check
    config: {conditions: ["order.total > 0"]}
    inputs: [{from: order}]
    outputs: [{name: valid}]
  - id: payment
    name: 支付处理
    type: api_call
    config: {url: https://api.pay.com/charge, method: POST}
    depends_on: [validate]
    inputs: [{from: valid}]
    outputs: [{name: paid}]
"""
    wf = system.create_workflow_from_content(user_input)
    print(f"✅ 工作流创建成功: ID={wf.id}, 名称={wf.name}")

    # 2. 扫描检测
    scan_res = system.scan_workflow(wf.id)
    print(f"🔍 扫描完成: {scan_res.overall_status.value}, 耗时 {scan_res.scan_time:.2f}s")

    # 3. 执行工作流
    exec_res = await system.execute_workflow(wf.id, {"order": {"total": 100}})
    print(f"⚡ 执行状态: {exec_res.status.value}, 耗时 {exec_res.duration:.2f}s")

    # 4. 导出工作流
    exported = system.export_workflow(wf.id, 'json')
    print(f"📤 导出长度: {len(exported)} 字符")

    # 5. 文件合并演示
    merger = UniversalFileMerger()
    demo_files = ["config1.json", "config2.json"]  # 假设存在
    merge_result = merger.merge_files_by_extension(demo_files)
    print(f"📁 文件合并完成: {merge_result.get('summary', {})}")

    print("\n✅ 所有功能演示完成！")