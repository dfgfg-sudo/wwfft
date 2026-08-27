from .config import NeuroConfig
from .processor import NeuroDataProcessor
from .model_core import NeuroCore
from .optimizer import NeuroOptimizer

class TrainingSystem:
    def __init__(self, config: NeuroConfig):
        self.config = config
        self.processor = NeuroDataProcessor(config)
        self.core = NeuroCore(config)
        self.optimizer = NeuroOptimizer(config)

    def run_pipeline(self):
        dataset = self.processor.process()
        self.core.train(dataset)
        # 可选优化器调整
        self.optimizer.adjust()
        # 生成报告
        self._generate_report()

    def _generate_report(self):
        report_path = self.config.output_dir / "training_report.txt"
        with open(report_path, "w") as f:
            f.write("训练完成\n")
            f.write(f"数据集大小: {len(self.processor.process())}\n")
            f.write(f"模型保存路径: {self.config.output_dir / 'adapter'}\n")