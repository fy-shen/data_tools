import os.path
import random

import cv2
import numpy as np

from utils.file import *
from utils import IMG_FORMATS, ops


warnings.filterwarnings('ignore', category=UserWarning, message='loadtxt: input contained no data')


class CropData:
    def __init__(self, img_list, crop_shape):
        self.img_list = img_list
        self.w, self.h = crop_shape

    def run(self, img_save_dir=None, txt_save_dir=None):
        for img_path in self.img_list:
            txt_path = img2txt(img_path)
            if not os.path.exists(txt_path):
                warnings.warn(f'{img_path} has no label', UserWarning)
            else:
                fdir, fn, ext = splitfn(img_path)
                if img_save_dir is None:
                    img_save_dir = fdir.replace('raw', 'crop')
                if txt_save_dir is None:
                    txt_save_dir = img_save_dir.replace('images', 'labels')
                os.makedirs(img_save_dir, exist_ok=True)
                os.makedirs(txt_save_dir, exist_ok=True)

                img = cv2.imread(img_path)
                hi, wi = img.shape[:2]
                label = np.loadtxt(txt_path, dtype=np.float32).reshape(-1, 5)
                label[:, 1:] = ops.xywhn2xyxy(label[:, 1:], wi, hi)

                for idx in range(label.shape[0]):
                    obj = label[idx, 1:]
                    x1_crop, y1_crop = self.crop_obj(obj, wi, hi)
                    x2_crop, y2_crop = x1_crop + self.w, y1_crop + self.h
                    crop_img = img[y1_crop:y2_crop, x1_crop:x2_crop]
                    img_save_path = os.path.join(img_save_dir, f'{fn}_{idx:0>2d}{ext}')
                    cv2.imwrite(img_save_path, crop_img)

                    crop_label = label - [0, x1_crop, y1_crop, x1_crop, y1_crop]
                    filter_label = crop_label[
                        crop_label[:, 1] > 0 &
                        crop_label[:, 2] > 0 &
                        crop_label[:, 3] < self.w &
                        crop_label[:, 4] < self.h
                    ]
                    filter_label[:, 1:] = ops.xyxy2xywh(filter_label[:, 1:])
                    txt_save_path = os.path.join(txt_save_dir, f'{fn}_{idx:0>2d}.txt')
                    np.savetxt(txt_save_path, filter_label, fmt='%d %.6f %.6f %.6f %.6f', delimiter=' ')

    def crop_obj(self, obj, wi, hi, eps=50):
        x1, y1, x2, y2 = obj

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

        return random.randint(l, r), random.randint(t, b)


if __name__ == '__main__':
    data_path = ''
    app = CropData(
        img_list=find_files_with_ext(data_path, IMG_FORMATS),
        crop_shape=(960, 960)
    )
    app.run()
