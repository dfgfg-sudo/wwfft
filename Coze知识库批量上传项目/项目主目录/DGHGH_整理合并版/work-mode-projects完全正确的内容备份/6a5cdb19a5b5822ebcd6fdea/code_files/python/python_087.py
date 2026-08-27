class TrainingEngine:
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr)
        self.criterion = torch.nn.CrossEntropyLoss()
        self.scaler = torch.cuda.amp.GradScaler() if self.device.type == 'cuda' else None

    def train_epoch(self, dataloader):
        self.model.train()
        total_loss, correct, total = 0, 0, 0
        for x, y in dataloader:
            x, y = x.to(self.device), y.to(self.device)
            self.optimizer.zero_grad()
            with torch.cuda.amp.autocast(enabled=self.scaler is not None):
                out = self.model(x)
                loss = self.criterion(out, y)
            if self.scaler:
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                loss.backward()
                self.optimizer.step()
            total_loss += loss.item()
            _, pred = out.max(1)
            correct += pred.eq(y).sum().item()
            total += y.size(0)
        return total_loss / len(dataloader), 100. * correct / total

    def validate(self, dataloader):
        self.model.eval()
        loss, correct, total = 0, 0, 0
        with torch.no_grad():
            for x, y in dataloader:
                x, y = x.to(self.device), y.to(self.device)
                out = self.model(x)
                loss += self.criterion(out, y).item()
                _, pred = out.max(1)
                correct += pred.eq(y).sum().item()
                total += y.size(0)
        return loss / len(dataloader), 100. * correct / total