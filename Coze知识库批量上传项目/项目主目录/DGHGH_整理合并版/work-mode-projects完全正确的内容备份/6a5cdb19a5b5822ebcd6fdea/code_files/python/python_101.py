class ModelOptimizer:
    def __init__(self, model):
        self.model = model

    def quantize_dynamic(self):
        import torch.quantization
        return torch.quantization.quantize_dynamic(
            self.model, {torch.nn.Linear, torch.nn.Conv2d}, dtype=torch.qint8
        )

    def prune_l1(self, amount=0.3):
        import torch.nn.utils.prune as prune
        parameters_to_prune = []
        for name, module in self.model.named_modules():
            if isinstance(module, (torch.nn.Linear, torch.nn.Conv2d)):
                parameters_to_prune.append((module, 'weight'))
        prune.global_unstructured(parameters_to_prune, pruning_method=prune.L1Unstructured, amount=amount)
        return self.model

    def export_onnx(self, dummy_input, output_path):
        torch.onnx.export(self.model, dummy_input, output_path,
                          opset_version=13, input_names=['input'], output_names=['output'],
                          dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}})