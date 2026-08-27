import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread, Event
import time
from core.config import NeuroConfig
from core.training import TrainingSystem

class SingularityUI:
    def __init__(self, config: NeuroConfig):
        self.config = config
        self.root = tk.Tk()
        self.root.title("NeuroFactory - 智能训练系统")
        self.root.geometry("1440x900")
        self.notebook = ttk.Notebook(self.root)
        self.monitor_event = Event()
        self.monitor_event.set()
        self.trainer = TrainingSystem(config)  # 用于后台训练
        self._build_tabs()
        self.notebook.pack(expand=True, fill='both')
        self._start_monitor()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_tabs(self):
        # 简化构建标签页占位，实际各标签页在单独文件中
        from .training_tab import TrainingTab
        from .monitor_tab import MonitorTab
        from .export_tab import ExportTab
        from .chat_tab import ChatTab
        from .preferences_dialog import PreferencesDialog
        from .data_analysis_dialog import DataAnalysisDialog
        from .model_evaluation_dialog import ModelEvaluationDialog

        self.train_tab = TrainingTab(self.notebook, self.config, self.trainer)
        self.monitor_tab = MonitorTab(self.notebook)
        self.export_tab = ExportTab(self.notebook, self.config)
        self.chat_tab = ChatTab(self.notebook, self.config)
        self.notebook.add(self.train_tab, text="训练")
        self.notebook.add(self.monitor_tab, text="监控")
        self.notebook.add(self.export_tab, text="导出")
        self.notebook.add(self.chat_tab, text="对话")

    def _start_monitor(self):
        Thread(target=self._update_monitor, daemon=True).start()

    def _update_monitor(self):
        import psutil
        import pynvml
        while self.monitor_event.is_set():
            try:
                if hasattr(self, 'monitor_tab'):
                    # 更新CPU
                    cpu = psutil.cpu_percent()
                    self.monitor_tab.cpu_bar['value'] = cpu
                    # 更新内存
                    mem = psutil.virtual_memory().percent
                    self.monitor_tab.mem_bar['value'] = mem
                    # 更新GPU
                    try:
                        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        gpu_usage = info.used / info.total * 100
                        self.monitor_tab.gpu_bar['value'] = gpu_usage
                    except:
                        pass
            except Exception as e:
                pass
            time.sleep(1)

    def run(self):
        self.root.mainloop()

    def _on_close(self):
        self.monitor_event.clear()
        self.root.destroy()