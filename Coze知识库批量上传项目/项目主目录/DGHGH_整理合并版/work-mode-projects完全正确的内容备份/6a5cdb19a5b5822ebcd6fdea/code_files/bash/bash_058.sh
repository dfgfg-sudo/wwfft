# 降低批处理大小
   batch_size: 4
   
   # 启用梯度检查点
   gradient_checkpointing: true
   
   # 使用4bit量化
   quantization:
     enabled: true
     bits: 4