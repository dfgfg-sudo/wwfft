import albumentations as A
import numpy as np

class DataAugmentation:
    def __init__(self, aug_type='standard'):
        self.aug_type = aug_type
        self.augmentations = {
            'standard': A.Compose([
                A.HorizontalFlip(p=0.5),
                A.RandomRotate90(p=0.3),
                A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.2, rotate_limit=30, p=0.5),
                A.RandomBrightnessContrast(p=0.3),
                A.GaussNoise(var_limit=(10, 50), p=0.2),
            ]),
            'advanced': A.Compose([
                A.OneOf([A.MotionBlur(blur_limit=7), A.MedianBlur(blur_limit=7), A.GaussianBlur(blur_limit=(3,7))], p=0.3),
                A.Cutout(num_holes=8, max_h_size=32, max_w_size=32, p=0.5),
            ]),
            'adversarial': A.Compose([
                A.GaussNoise(var_limit=(50,100), p=0.5),
                A.RandomFog(p=0.2),
            ])
        }

    def apply(self, image, bboxes=None):
        aug = self.augmentations.get(self.aug_type, self.augmentations['standard'])
        if bboxes is not None:
            res = aug(image=image, bboxes=bboxes)
            return res['image'], res['bboxes']
        return aug(image=image)['image'], None

    def mixup(self, x, y, alpha=1.0):
        lam = np.random.beta(alpha, alpha) if alpha > 0 else 1
        index = torch.randperm(x.size(0))
        mixed_x = lam * x + (1 - lam) * x[index]
        y_a, y_b = y, y[index]
        return mixed_x, y_a, y_b, lam

    def cutmix(self, x, y, alpha=1.0):
        lam = np.random.beta(alpha, alpha) if alpha > 0 else 1
        batch_size = x.size(0)
        index = torch.randperm(batch_size)
        bbx1, bby1, bbx2, bby2 = self._rand_bbox(x.size(), lam)
        x[:, :, bbx1:bbx2, bby1:bby2] = x[index, :, bbx1:bbx2, bby1:bby2]
        lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (x.size(2) * x.size(3)))
        y_a, y_b = y, y[index]
        return x, y_a, y_b, lam

    def _rand_bbox(self, size, lam):
        W, H = size[2], size[3]
        cut_rat = np.sqrt(1. - lam)
        cut_w = int(W * cut_rat)
        cut_h = int(H * cut_rat)
        cx = np.random.randint(W)
        cy = np.random.randint(H)
        bbx1 = np.clip(cx - cut_w // 2, 0, W)
        bby1 = np.clip(cy - cut_h // 2, 0, H)
        bbx2 = np.clip(cx + cut_w // 2, 0, W)
        bby2 = np.clip(cy + cut_h // 2, 0, H)
        return bbx1, bby1, bbx2, bby2