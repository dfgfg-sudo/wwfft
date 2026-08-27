from aidatasetpack import ZipImageDataset
import torchvision.transforms as transforms

ds = ZipImageDataset('dataset_v1.zip', transform=transforms.ToTensor())
loader = torch.utils.data.DataLoader(ds, batch_size=32, shuffle=True)
for images in loader:
    # 训练代码
    pass