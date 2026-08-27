import os
import sys
import argparse
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(f'logs/system_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                              logging.StreamHandler(sys.stdout)])

def main():
    parser = argparse.ArgumentParser(description='全自动多模态AI训练系统 (AMM-ATS)')
    parser.add_argument('--mode', type=str, required=True,
                        choices=['train', 'evaluate', 'predict', 'export', 'demo'])
    parser.add_argument('--config', type=str, default='config.json')
    parser.add_argument('--checkpoint', type=str, help='检查点文件名')
    parser.add_argument('--data-path', type=str, help='自定义数据路径')
    parser.add_argument('--format', type=str, default='onnx', choices=['onnx','torchscript','huggingface'])
    parser.add_argument('--resume-from', type=str, help='恢复训练的检查点')
    args = parser.parse_args()

    from system.core import AutoMultiModalSystem
    system = AutoMultiModalSystem(args.config)

    if args.mode == 'train':
        system.train(resume_from=args.resume_from)
    elif args.mode == 'evaluate':
        system.evaluate(checkpoint_path=args.checkpoint)
    elif args.mode == 'predict':
        system.predict(data_path=args.data_path, checkpoint_path=args.checkpoint)
    elif args.mode == 'export':
        system.export_model(format=args.format, checkpoint_path=args.checkpoint)
    elif args.mode == 'demo':
        system.initialize()
        system.config.epochs = 5
        system.train()
        system.evaluate()
        system.predict()

if __name__ == '__main__':
    main()