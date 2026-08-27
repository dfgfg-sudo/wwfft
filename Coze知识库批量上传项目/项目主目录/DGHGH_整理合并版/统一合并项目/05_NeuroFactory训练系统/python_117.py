import os
from PIL import Image

def clean_dataset(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for fname in os.listdir(input_dir):
        fpath = os.path.join(input_dir, fname)
        try:
            img = Image.open(fpath)
            img.verify()
            img = Image.open(fpath)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(os.path.join(output_dir, fname), 'JPEG', quality=95)
        except Exception as e:
            print(f"删除损坏文件: {fname}, 错误: {e}")