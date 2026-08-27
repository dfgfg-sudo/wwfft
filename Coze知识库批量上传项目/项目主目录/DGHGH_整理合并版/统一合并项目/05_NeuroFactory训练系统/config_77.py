#!/usr/bin/env python3
import sys
import logging
import argparse
from pathlib import Path
from core.config import NeuroConfig
from core.training import TrainingSystem
from gui.main_window import SingularityUI
import pynvml

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", action="store_true", help="启动GUI界面")
    parser.add_argument("--train", action="store_true", help="直接启动训练")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    config = NeuroConfig()
    if args.gui:
        try:
            pynvml.nvmlInit()
        except:
            pass
        app = SingularityUI(config)
        app.run()
    elif args.train:
        system = TrainingSystem(config)
        system.run_pipeline()
    else:
        # 默认启动GUI
        try:
            pynvml.nvmlInit()
        except:
            pass
        app = SingularityUI(config)
        app.run()

if __name__ == "__main__":
    main()