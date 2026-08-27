async def demo_fix_system():
    fix_system = WorkflowAutoFixSystem()
    broken_workflow = {"nodes": [{"id": "n1", "type": "http", "config": {}}], "edges": []}
    diagnosis = fix_system.diagnose(broken_workflow)
    print("诊断结果:", diagnosis['summary'])
    if diagnosis['issues']:
        fix_result = fix_system.auto_fix(diagnosis['issues'])
        print(f"修复了 {fix_result['fixed_count']} 个问题，成功率 {fix_result['success_rate']}%")
        verify_result = fix_system.verify(broken_workflow)
        print(f"验证通过: {verify_result['passed']}，耗时 {verify_result['latency']}ms")