import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from PIL import Image
import pandas as pd
import numpy as np
import os
import logging
from transformers import BertTokenizer

class MultiModalDataset(Dataset):
    def __init__(self, config, split='train'):
        self.config = config
        self.split = split
        self.tokenizer = BertTokenizer.from_pretrained(config.text_model_name)
        self.image_transform = self._get_image_transform()
        self.data = self._load_data()
        logging.info(f"初始化 {split} 数据集，样本数: {len(self.data)}")

    def _get_image_transform(self):
        if self.split == 'train':
            return transforms.Compose([
                transforms.Resize((self.config.image_size, self.config.image_size)),
                transforms.RandomHorizontalFlip(),
                transforms.RandomRotation(10),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        else:
            return transforms.Compose([
                transforms.Resize((self.config.image_size, self.config.image_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

    def _load_data(self):
        data_path = os.path.join(self.config.data_dir, f"{self.split}.csv")
        if not os.path.exists(data_path):
            logging.warning(f"数据文件 {data_path} 不存在，生成示例数据")
            return self._create_sample_data()
        try:
            df = pd.read_csv(data_path)
            required = ['image_path', 'text', 'label']
            for col in required:
                if col not in df.columns:
                    raise ValueError(f"缺少列: {col}")
            df = df.dropna(subset=required)
            df['label'] = df['label'].astype(int)
            return df
        except Exception as e:
            logging.error(f"加载数据失败: {e}")
            return self._create_sample_data()

    def _create_sample_data(self):
        num = 100 if self.split == 'train' else 20
        data = []
        for i in range(num):
            data.append({
                'image_path': f"sample_{i}.jpg",
                'text': f"示例文本描述 {i}",
                'label': i % self.config.num_classes
            })
        return pd.DataFrame(data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        try:
            row = self.data.iloc[idx]
            # 图像
            img_path = row['image_path']
            if not os.path.exists(img_path):
                img = Image.new('RGB', (224, 224), color='gray')
            else:
                img = Image.open(img_path).convert('RGB')
            img_tensor = self.image_transform(img)

            # 文本
            text = str(row['text'])
            enc = self.tokenizer(
                text,
                max_length=self.config.max_text_length,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            label = torch.tensor(int(row['label']), dtype=torch.long)
            return {
                'image': img_tensor,
                'input_ids': enc['input_ids'].squeeze(0),
                'attention_mask': enc['attention_mask'].squeeze(0),
                'label': label,
                'index': idx
            }
        except Exception as e:
            logging.error(f"样本 {idx} 处理失败: {e}")
            return self._get_default_sample()

    def _get_default_sample(self):
        dummy_img = torch.zeros(3, self.config.image_size, self.config.image_size)
        enc = self.tokenizer("默认", max_length=128, padding='max_length', truncation=True, return_tensors='pt')
        return {
            'image': dummy_img,
            'input_ids': enc['input_ids'].squeeze(0),
            'attention_mask': enc['attention_mask'].squeeze(0),
            'label': torch.tensor(0, dtype=torch.long),
            'index': -1
        }

class MultiModalDataLoader:
    def __init__(self, config):
        self.config = config
        self.datasets = {}
        self.dataloaders = {}

    def prepare_datasets(self):
        for split in ['train', 'val', 'test']:
            self.datasets[split] = MultiModalDataset(self.config, split)

    def prepare_dataloaders(self):
        for split, ds in self.datasets.items():
            shuffle = (split == 'train')
            loader = DataLoader(
                ds,
                batch_size=self.config.batch_size,
                shuffle=shuffle,
                num_workers=self.config.num_workers,
                pin_memory=True,
                drop_last=(split=='train')
            )
            self.dataloaders[split] = loader
        return self.dataloaders

    def get_dataloader(self, split):
        if split not in self.dataloaders:
            raise ValueError(f"未知分割: {split}")
        return self.dataloaders[split]