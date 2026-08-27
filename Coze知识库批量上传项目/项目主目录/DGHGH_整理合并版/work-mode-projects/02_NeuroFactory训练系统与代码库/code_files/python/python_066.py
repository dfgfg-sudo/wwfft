import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import BertModel
import timm
import logging

class TextEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.bert = BertModel.from_pretrained(config.text_model_name)
        if config.freeze_text_encoder:
            for p in self.bert.parameters():
                p.requires_grad = False
        self.dropout = nn.Dropout(config.dropout_rate)
        self.proj = nn.Linear(768, config.hidden_size)

    def forward(self, input_ids, attention_mask):
        out = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pool = out.pooler_output
        return self.proj(self.dropout(pool))

class ImageEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.backbone = timm.create_model(
            config.image_model_name,
            pretrained=config.pretrained,
            num_classes=0
        )
        if config.freeze_image_encoder:
            for p in self.backbone.parameters():
                p.requires_grad = False
        feat_dim = self.backbone.num_features
        self.dropout = nn.Dropout(config.dropout_rate)
        self.proj = nn.Linear(feat_dim, config.hidden_size)

    def forward(self, images):
        feat = self.backbone.forward_features(images)
        if feat.dim() == 4:  # [B,C,H,W]
            feat = F.adaptive_avg_pool2d(feat, (1,1)).flatten(1)
        return self.proj(self.dropout(feat))

class MultiModalFusion(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.fusion = nn.Sequential(
            nn.Linear(config.hidden_size * 2, config.hidden_size),
            nn.LayerNorm(config.hidden_size),
            nn.ReLU(inplace=True),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_size, config.hidden_size // 2),
            nn.LayerNorm(config.hidden_size // 2),
            nn.ReLU(inplace=True),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_size // 2, config.hidden_size // 4),
            nn.LayerNorm(config.hidden_size // 4),
            nn.ReLU(inplace=True),
            nn.Dropout(config.dropout_rate)
        )

    def forward(self, text_feat, image_feat):
        combined = torch.cat([text_feat, image_feat], dim=1)
        return self.fusion(combined)

class ClassifierHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.head = nn.Sequential(
            nn.Linear(config.hidden_size // 4, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(config.dropout_rate),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(config.dropout_rate),
            nn.Linear(128, config.num_classes)
        )

    def forward(self, x):
        return self.head(x)

class MultiModalModel(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.text_encoder = TextEncoder(config)
        self.image_encoder = ImageEncoder(config)
        self.fusion = MultiModalFusion(config)
        self.classifier = ClassifierHead(config)
        self.norm = nn.LayerNorm(config.hidden_size // 4)
        logging.info(f"模型初始化完成，参数量: {sum(p.numel() for p in self.parameters())}")

    def forward(self, images, input_ids, attention_mask):
        t_feat = self.text_encoder(input_ids, attention_mask)
        i_feat = self.image_encoder(images)
        fused = self.fusion(t_feat, i_feat)
        fused = self.norm(fused)
        logits = self.classifier(fused)
        return logits, fused

    def save_pretrained(self, path):
        torch.save({'model_state_dict': self.state_dict()}, path)

    @classmethod
    def from_pretrained(cls, path, config):
        model = cls(config)
        ckpt = torch.load(path, map_location='cpu')
        model.load_state_dict(ckpt['model_state_dict'])
        return model