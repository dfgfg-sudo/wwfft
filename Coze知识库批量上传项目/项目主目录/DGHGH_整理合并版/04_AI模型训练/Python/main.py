import asyncio

async def main(args: Args) -> Output:
    intent_result = args.params.intent_result
    workflow_ids = intent_result.workflows
    params = intent_result.params
    
    async def call_workflow(wf_id, wf_params):
        result = await coze.workflows.run(wf_id, wf_params)
        return {"workflow_id": wf_id, "result": result}
    
    tasks = [call_workflow(wf_id, params) for wf_id in workflow_ids]
    results = await asyncio.gather(*tasks)
    
    final_output = {
        "message": "您的任务已完成。",
        "details": results
    }
    return {"output": final_output}