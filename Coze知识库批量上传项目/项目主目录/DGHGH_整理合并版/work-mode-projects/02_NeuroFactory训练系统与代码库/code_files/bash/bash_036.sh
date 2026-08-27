# 克隆项目
git clone https://github.com/yourusername/ai-training-system.git
cd ai-training-system

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化配置文件
cp config.example.yaml config.yaml