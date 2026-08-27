# 安装依赖
pip install torch transformers datasets nltk spacy pillow pytesseract pdfplumber python-docx PyPDF2 openpyxl opencv-python soundfile watchdog fastapi uvicorn

# 交互式模式（推荐）
python omnineuro_hhcps.py --interactive

# 全自动管道
python omnineuro_hhcps.py --pipeline --auto

# 仅数据吞噬
python omnineuro_hhcps.py --devour

# 代码生成
python omnineuro_hhcps.py --generate "开发一个用户登录系统"

# API服务部署
python omnineuro_hhcps.py --deploy --port 8000