"""
智能AI多项目训练系统 v3.0
功能：支持原始项目、同级项目和嵌套子项目的自动识别与资源共享
"""

import os
import sys
import time
import shutil
import logging
import platform
from pathlib import Path
from typing import Dict, List, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
from safetensors.torch import load_file

class AITrainingSystem:
    def __init__(self):
        self.setup_logging()
        self.device = self.detect_device()
        self.projects = self.detect_projects()
        
    def setup_logging(self):
        """配置日志系统"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("ai_training.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def detect_device(self) -> str:
        """检测最佳计算设备"""
        if torch.cuda.is_available():
            device = "cuda"
            self.logger.info(f"检测到CUDA设备: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            device = "mps"
            self.logger.info("检测到Apple MPS加速")
        else:
            device = "cpu"
            self.logger.warning("未检测到GPU加速，使用CPU模式")
        return device

    def detect_projects(self) -> Dict[str, Path]:
        """自动检测所有相关项目"""
        base_paths = [
            Path(r"C:\Users\Administrator\Documents\uytrertrt\Bunny-v1_0-3B"),
            Path(r"C:\Users\Administrator\Documents"),
            Path.cwd()  # 当前目录
        ]
        
        projects = {}
        for path in base_paths:
            if path.exists():
                # 查找原始项目
                if "Bunny-v1_0-3B" in path.name:
                    projects["original"] = path
                    self.logger.info(f"发现原始项目: {path}")
                
                # 查找同级项目
                for item in path.parent.glob("*"):
                    if item.is_dir() and item != projects.get("original"):
                        projects[f"parallel_{item.name}"] = item
                
                # 查找嵌套项目
                for sub in path.rglob("*"):
                    if sub.is_dir() and "Bunny" in sub.parts and sub != projects.get("original"):
                        projects[f"nested_{sub.name}"] = sub
        
        if not projects:
            self.logger.error("未找到任何有效项目")
            sys.exit(1)
            
        return projects

    def setup_project(self, project_path: Path) -> bool:
        """初始化项目目录结构"""
        required_dirs = ["data", "model", "output", "logs"]
        success = True
        
        try:
            for dir_name in required_dirs:
                dir_path = project_path / dir_name
                dir_path.mkdir(exist_ok=True)
            
            # 共享原始项目资源
            if "original" in self.projects:
                self.share_resources(self.projects["original"], project_path)
                
            return True
            
        except Exception as e:
            self.logger.error(f"项目初始化失败: {str(e)}")
            return False

    def share_resources(self, src_project: Path, dst_project: Path):
        """共享资源处理"""
        share_items = {
            "model": ["config.json", "model.safetensors"],
            "data": ["*.txt", "*.json", "*.csv"]
        }
        
        for item_type, patterns in share_items.items():
            src_dir = src_project / item_type
            dst_dir = dst_project / item_type
            
            if not dst_dir.exists():
                # 尝试创建符号链接
                try:
                    if platform.system() == "Windows":
                        os.system(f'mklink /J "{dst_dir}" "{src_dir}"')
                    else:
                        os.symlink(src_dir, dst_dir)
                    self.logger.info(f"已创建共享链接: {dst_dir}")
                except:
                    # 回退到复制文件
                    try:
                        shutil.copytree(src_dir, dst_dir)
                        self.logger.info(f"已复制共享资源: {dst_dir}")
                    except Exception as e:
                        self.logger.warning(f"资源共享失败: {str(e)}")

    def load_model(self, project_path: Path):
        """安全加载模型"""
        model_dir = project_path / "model"
        
        try:
            # 验证模型文件
            required_files = ["config.json", "model.safetensors"]
            for f in required_files:
                if not (model_dir / f).exists():
                    raise FileNotFoundError(f"缺少必要文件: {f}")
            
            # 分步加载模型
            config = AutoConfig.from_pretrained(str(model_dir))
            model = AutoModelForCausalLM.from_config(config)
            
            # 加载权重
            state_dict = load_file(str(model_dir / "model.safetensors"))
            model.load_state_dict(state_dict)
            model.to(self.device)
            
            # 加载tokenizer
            tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
            
            return model, tokenizer
            
        except Exception as e:
            self.logger.error(f"模型加载失败: {str(e)}")
            raise

    def run_training(self, project_path: Path):
        """执行训练流程"""
        try:
            # 初始化项目
            if not self.setup_project(project_path):
                return False
                
            # 加载模型
            model, tokenizer = self.load_model(project_path)
            self.logger.info(f"成功加载模型: {project_path.name}")
            
            # 训练流程
            model.train()
            for epoch in range(3):  # 示例训练3轮
                self.logger.info(f"开始第 {epoch+1}/3 轮训练")
                # 实际训练代码...
                
            # 保存结果
            output_dir = project_path / "output" / time.strftime("%Y%m%d_%H%M%S")
            output_dir.mkdir(parents=True)
            model.save_pretrained(output_dir)
            
            self.logger.info(f"训练结果已保存到: {output_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"训练过程出错: {str(e)}")
            return False

    def run(self):
        """主执行流程"""
        self.logger.info("\n" + "="*50)
        self.logger.info("AI多项目训练系统 v3.0")
        self.logger.info("="*50)
        
        success_count = 0
        for name, path in self.projects.items():
            self.logger.info(f"\n处理项目: {name} ({path})")
            if self.run_training(path):
                success_count += 1
        
        self.logger.info("\n" + "="*50)
        self.logger.info(f"完成: {success_count}/{len(self.projects)} 个项目处理成功")
        self.logger.info("="*50)

if __name__ == "__main__":
    try:
        system = AITrainingSystem()
        system.run()
    except Exception as e:
        logging.error(f"系统运行失败: {str(e)}")
        sys.exit(1)