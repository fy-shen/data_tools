import os.path
import random
from tqdm import tqdm
import cv2
import numpy as np

from utils.file import *
from utils import IMG_FORMATS, ops


warnings.filterwarnings('ignore', category=UserWarning, message='loadtxt: input contained no data')


class CropData:
    def __init__(self, img_dir, txt_dir='', crop_shape=(960, 960)):
        self.img_list = find_files_with_ext(img_dir, IMG_FORMATS)
        self.txt_dir = txt_dir
        self.w, self.h = crop_shape

    def run(self, img_save_dir=None, txt_save_dir=None):
        for img_path in tqdm(self.img_list):
            _, fn, ext = splitfn(img_path)
            txt_path = os.path.join(self.txt_dir, fn + '.txt') if self.txt_dir else img2txt(img_path)

            if not os.path.exists(txt_path):
                warnings.warn(f'{img_path} has no label', UserWarning)
            else:
                if txt_save_dir is None:
                    txt_save_dir = img_save_dir.replace('images', 'labels')
                os.makedirs(img_save_dir, exist_ok=True)
                os.makedirs(txt_save_dir, exist_ok=True)

                img = cv2.imread(img_path)
                hi, wi = img.shape[:2]
                label_raw = np.loadtxt(txt_path, dtype=np.float32).reshape(-1, 5)
                label_raw[:, 1:] = ops.xywhn2xyxy(label_raw[:, 1:], wi, hi)
                # 选取球作为裁剪目标, 当球个数超过5个时, 随机5个球做裁剪
                idxs = np.where(label_raw[:, 0] == 0)[0]
                if len(idxs) > 5:
                    idxs = random.sample(list(idxs), 5)
                for idx in idxs:
                    obj = label_raw[idx, 1:]
                    x1_crop, y1_crop = self.crop_obj(obj, wi, hi)
                    x2_crop, y2_crop = x1_crop + self.w, y1_crop + self.h
                    crop_img = img[y1_crop:y2_crop, x1_crop:x2_crop]
                    img_save_path = os.path.join(img_save_dir, f'{fn}_{idx:0>2d}{ext}')
                    cv2.imwrite(img_save_path, crop_img)

                    label_crop = label_raw - [0, x1_crop, y1_crop, x1_crop, y1_crop]
                    x1s = label_crop[:, 1]
                    y1s = label_crop[:, 2]
                    x2s = label_crop[:, 3]
                    y2s = label_crop[:, 4]
                    ws, hs = x2s - x1s, y2s - y1s
                    # 过滤边界目标
                    ratio = 0.3
                    filter_label = label_crop[
                        ((x1s > 0) & (y1s > 0) & (x1s < self.w - ws * ratio) & (y1s < self.h - hs * ratio)) |
                        ((x2s < self.w) & (y2s < self.h) & (x2s > ws * ratio) & (y2s > hs * ratio))
                    ]
                    filter_label[:, 1:] = ops.xyxy2xywhn(filter_label[:, 1:], self.w, self.h, clip=True)
                    txt_save_path = os.path.join(txt_save_dir, f'{fn}_{idx:0>2d}.txt')
                    np.savetxt(txt_save_path, filter_label, fmt='%d %.6f %.6f %.6f %.6f', delimiter=' ')

    def crop_obj(self, obj, wi, hi, eps=50):
        # 根据球的位置确定裁剪的范围
        x1, y1, x2, y2 = obj.astype(np.int32)

        x1_ = max(x1 - eps, 0)
        y1_ = max(y1 - eps, 0)
        x2_ = min(x2 + eps, wi)
        y2_ = min(y2 + eps, hi)

        w_ = self.w - abs(x2_ - x1_)
        h_ = self.h - abs(y2_ - y1_)
        # 左上角坐标截取位置极限范围
        l = max(x1_ - w_, 0)
        r = x1_ - max(x2_ + w_ - wi, 0)
        t = max(y1_ - h_, 0)
        b = y1_ - max(y2_ + h_ - hi, 0)
        # print(l, r, t, b)
        return random.randint(l, r), random.randint(t, b)


if __name__ == '__main__':
    app = CropData(
        img_dir='/home/sfy/SFY/disk1/data/Football/AKD/BMB/2024-0511/raw/images_train',
        txt_dir='/home/sfy/SFY/disk1/data/Football/AKD/BMB/2024-0511/raw/labels_train_202408281316',
        crop_shape=(960, 960)
    )
    app.run(
        img_save_dir='/home/sfy/SFY/disk1/data/Football/AKD/BMB/2024-0511/images/train',
        # txt_save_dir=''
    )
