import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import autocast, GradScaler
from torch.utils.tensorboard import SummaryWriter
import numpy as np
import os
import json
import time
import logging
from datetime import datetime
from tqdm import tqdm
from sklearn.metrics import classification_report, confusion_matrix

class MultiModalTrainer:
    def __init__(self, config, model, device=None):
        self.config = config
        self.model = model
        self.device = device or torch.device(config.device)
        self.model.to(self.device)

        self.optimizer = self._create_optimizer()
        self.scheduler = self._create_scheduler()
        self.criterion = nn.CrossEntropyLoss()
        self.scaler = GradScaler(enabled=config.use_amp)

        self.current_epoch = 0
        self.global_step = 0
        self.best_metric = 0.0

        self.writer = SummaryWriter(os.path.join(config.tensorboard_dir, config.experiment_name))
        os.makedirs(config.checkpoint_dir, exist_ok=True)
        os.makedirs(config.output_dir, exist_ok=True)
        logging.info(f"训练器初始化，设备: {self.device}")

    def _create_optimizer(self):
        params = []
        if hasattr(self.model, 'text_encoder'):
            params.append({'params': self.model.text_encoder.parameters(), 'lr': self.config.learning_rate * 0.1})
        if hasattr(self.model, 'image_encoder'):
            params.append({'params': self.model.image_encoder.parameters(), 'lr': self.config.learning_rate * 0.1})
        fusion_params = []
        if hasattr(self.model, 'fusion'):
            fusion_params += list(self.model.fusion.parameters())
        if hasattr(self.model, 'classifier'):
            fusion_params += list(self.model.classifier.parameters())
        if fusion_params:
            params.append({'params': fusion_params, 'lr': self.config.learning_rate})

        if self.config.optimizer_type.lower() == 'adamw':
            return optim.AdamW(params, lr=self.config.learning_rate, weight_decay=self.config.weight_decay)
        elif self.config.optimizer_type.lower() == 'adam':
            return optim.Adam(params, lr=self.config.learning_rate, weight_decay=self.config.weight_decay)
        else:
            return optim.SGD(params, lr=self.config.learning_rate, momentum=0.9, weight_decay=self.config.weight_decay)

    def _create_scheduler(self):
        if self.config.scheduler_type.lower() == 'cosine':
            return optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=self.config.epochs, eta_min=1e-6)
        elif self.config.scheduler_type.lower() == 'step':
            return optim.lr_scheduler.StepLR(self.optimizer, step_size=self.config.epochs//3, gamma=0.1)
        elif self.config.scheduler_type.lower() == 'plateau':
            return optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='max', factor=0.5, patience=5)
        else:
            return None

    def train_epoch(self, dataloader, epoch):
        self.model.train()
        total_loss, correct, total = 0, 0, 0
        pbar = tqdm(dataloader, desc=f"Epoch {epoch}/{self.config.epochs}")
        for batch in pbar:
            images = batch['image'].to(self.device)
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['label'].to(self.device)

            self.optimizer.zero_grad()
            with autocast(enabled=self.config.use_amp):
                logits, _ = self.model(images, input_ids, attention_mask)
                loss = self.criterion(logits, labels)

            self.scaler.scale(loss).backward()
            self.scaler.unscale_(self.optimizer)
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.max_grad_norm)
            self.scaler.step(self.optimizer)
            self.scaler.update()

            _, pred = torch.max(logits, 1)
            total += labels.size(0)
            correct += (pred == labels).sum().item()
            total_loss += loss.item() * labels.size(0)

            self.global_step += 1
            if self.global_step % self.config.logging_steps == 0:
                self.writer.add_scalar('train/loss', loss.item(), self.global_step)
                self.writer.add_scalar('train/acc', (pred==labels).float().mean().item(), self.global_step)

            pbar.set_postfix({'loss': loss.item(), 'acc': (pred==labels).float().mean().item()})

        avg_loss = total_loss / total
        avg_acc = correct / total
        self.writer.add_scalar('epoch/train_loss', avg_loss, epoch)
        self.writer.add_scalar('epoch/train_acc', avg_acc, epoch)
        return avg_loss, avg_acc

    def evaluate(self, dataloader, epoch=0):
        self.model.eval()
        total_loss, correct, total = 0, 0, 0
        all_preds, all_labels = [], []
        with torch.no_grad():
            for batch in dataloader:
                images = batch['image'].to(self.device)
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['label'].to(self.device)

                logits, _ = self.model(images, input_ids, attention_mask)
                loss = self.criterion(logits, labels)
                _, pred = torch.max(logits, 1)

                total += labels.size(0)
                correct += (pred == labels).sum().item()
                total_loss += loss.item() * labels.size(0)
                all_preds.extend(pred.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())

        avg_loss = total_loss / total
        avg_acc = correct / total
        report = classification_report(all_labels, all_preds, output_dict=True)
        cm = confusion_matrix(all_labels, all_preds)

        if epoch > 0:
            self.writer.add_scalar('eval/loss', avg_loss, epoch)
            self.writer.add_scalar('eval/acc', avg_acc, epoch)

        return {
            'loss': avg_loss,
            'accuracy': avg_acc,
            'classification_report': report,
            'confusion_matrix': cm.tolist()
        }

    def train(self, train_loader, val_loader=None):
        logging.info("开始训练...")
        history = {'train_loss': [], 'train_acc': [], 'eval_loss': [], 'eval_acc': []}
        early_stop_counter = 0

        for epoch in range(1, self.config.epochs + 1):
            self.current_epoch = epoch
            train_loss, train_acc = self.train_epoch(train_loader, epoch)
            history['train_loss'].append(train_loss)
            history['train_acc'].append(train_acc)

            if val_loader:
                eval_metrics = self.evaluate(val_loader, epoch)
                history['eval_loss'].append(eval_metrics['loss'])
                history['eval_acc'].append(eval_metrics['accuracy'])
                logging.info(f"Epoch {epoch}: Train Loss={train_loss:.4f}, Acc={train_acc:.4f} | Eval Loss={eval_metrics['loss']:.4f}, Acc={eval_metrics['accuracy']:.4f}")

                if eval_metrics['accuracy'] > self.best_metric:
                    self.best_metric = eval_metrics['accuracy']
                    self.save_checkpoint('best_model.pth')
                    early_stop_counter = 0
                else:
                    early_stop_counter += 1

                if early_stop_counter >= self.config.early_stopping_patience:
                    logging.info(f"早停触发，第 {epoch} 轮停止")
                    break

            if self.scheduler:
                if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(eval_metrics['accuracy'] if val_loader else train_acc)
                else:
                    self.scheduler.step()

            if epoch % self.config.save_steps == 0:
                self.save_checkpoint(f'checkpoint_epoch_{epoch}.pth')

        self.save_checkpoint('final_model.pth')
        self._save_history(history)
        self.writer.close()
        logging.info("训练完成！最佳指标: {:.4f}".format(self.best_metric))
        return history

    def save_checkpoint(self, filename):
        path = os.path.join(self.config.checkpoint_dir, filename)
        torch.save({
            'epoch': self.current_epoch,
            'global_step': self.global_step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'scaler_state_dict': self.scaler.state_dict(),
            'best_metric': self.best_metric,
            'config': self.config.to_dict()
        }, path)
        logging.info(f"检查点保存: {path}")

    def load_checkpoint(self, path):
        ckpt = torch.load(path, map_location=self.device)
        self.model.load_state_dict(ckpt['model_state_dict'])
        self.optimizer.load_state_dict(ckpt['optimizer_state_dict'])
        if self.scheduler and ckpt.get('scheduler_state_dict'):
            self.scheduler.load_state_dict(ckpt['scheduler_state_dict'])
        self.scaler.load_state_dict(ckpt['scaler_state_dict'])
        self.current_epoch = ckpt.get('epoch', 0)
        self.global_step = ckpt.get('global_step', 0)
        self.best_metric = ckpt.get('best_metric', 0.0)
        logging.info(f"从 {path} 恢复训练")

    def _save_history(self, history):
        path = os.path.join(self.config.output_dir, 'training_history.json')
        with open(path, 'w') as f:
            json.dump(history, f, indent=2)

    def predict(self, dataloader):
        self.model.eval()
        preds, labels, features = [], [], []
        with torch.no_grad():
            for batch in dataloader:
                images = batch['image'].to(self.device)
                input_ids = batch['input_ids'].to(self.device)
                attn = batch['attention_mask'].to(self.device)
                logits, feat = self.model(images, input_ids, attn)
                _, pred = torch.max(logits, 1)
                preds.append(pred.cpu().numpy())
                labels.append(batch['label'].numpy())
                features.append(feat.cpu().numpy())
        return {
            'predictions': np.concatenate(preds),
            'labels': np.concatenate(labels),
            'features': np.concatenate(features)
        }