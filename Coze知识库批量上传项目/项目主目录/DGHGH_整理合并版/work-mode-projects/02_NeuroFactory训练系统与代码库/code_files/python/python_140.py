from fastapi import FastAPI, File, UploadFile
import uvicorn

app = FastAPI()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    # 处理并返回结果
    return {"result": "processed"}

# 启动服务：uvicorn.run(app, host="0.0.0.0", port=8000)