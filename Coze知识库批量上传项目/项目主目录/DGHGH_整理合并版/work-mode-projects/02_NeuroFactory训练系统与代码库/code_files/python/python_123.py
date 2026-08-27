class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}

    def log_training(self, epoch, train_loss, val_loss, acc):
        self.metrics[epoch] = {'train_loss': train_loss, 'val_loss': val_loss, 'acc': acc}

    def check_alerts(self):
        if len(self.metrics) > 1:
            last = list(self.metrics.values())[-1]
            if last['acc'] < 0.8:
                return "警告：准确率低于80%"
        return None