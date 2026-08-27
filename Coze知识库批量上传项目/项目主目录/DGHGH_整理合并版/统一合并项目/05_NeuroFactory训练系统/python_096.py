class GradientFusion:
    def __init__(self, models):
        self.models = models
        self.grad_buffers = {id(m): [] for m in models}

    def register_hooks(self):
        for mid, model in enumerate(self.models):
            for param in model.parameters():
                param.register_hook(lambda grad, idx=mid: self._collect_grad(grad, idx))

    def _collect_grad(self, grad, idx):
        self.grad_buffers[idx].append(grad.detach())
        if all(len(buf) == len(list(self.models[0].parameters())) for buf in self.grad_buffers.values()):
            fused = self._fuse_gradients()
            self._apply_fused(fused)
            self.grad_buffers = {k: [] for k in self.grad_buffers}
        return grad

    def _fuse_gradients(self):
        # 平均融合
        fused = []
        for i in range(len(list(self.models[0].parameters()))):
            layer_grads = [self.grad_buffers[mid][i] for mid in self.grad_buffers]
            avg = torch.mean(torch.stack(layer_grads), dim=0)
            fused.append(avg)
        return fused

    def _apply_fused(self, fused_grads):
        for model in self.models:
            for param, grad in zip(model.parameters(), fused_grads):
                if param.grad is not None:
                    param.grad = grad.to(param.device)