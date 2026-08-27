class MultiModelCoordinator:
    def __init__(self, models):
        self.models = models

    def ensemble_predict(self, input_data):
        results = []
        for model in self.models:
            results.append(model.predict(input_data))
        # 投票或平均融合
        return self._fuse_results(results)

    def _fuse_results(self, results):
        # 简单平均
        return np.mean(results, axis=0)