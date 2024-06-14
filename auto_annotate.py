import os
from datetime import datetime
import cv2
import numpy as np

from ultralytics import YOLO
from utils import IMG_FORMATS
from utils.file import find_files_with_ext, img2txt


class Annotator:
    def __init__(self, model, imgdata):
        self.model = YOLO(model)
        self.imgs = find_files_with_ext(imgdata, IMG_FORMATS)

    @staticmethod
    def name2id(cls, names):
        res = []
        for name in names:
            for k, v in cls.items():
                if v == name:
                    res.append(k)
        return res

    def txt_add_cls(self, cls):
        fp_ext = datetime.now().strftime("_%Y%m%d%H%M")
        for img_path in self.imgs:
            txt_path = img2txt(img_path)

            if os.path.exists(txt_path):
                img = cv2.imread(img_path)
                ih, iw = img.shape[:2]
                results = self.model(img, imgsz=max(ih, iw), classes=self.name2id(self.model.names, cls.values()))
                boxes = results[0].boxes.cpu()

                # 根据 yolo 中 class id 获取对应的 class name
                res_cls = [self.model.names[int(i)] for i in boxes.cls]
                # 根据 class name 获取在当前数据集中对应的 class id
                res_cls_id = self.name2id(cls, res_cls)
                res_cls_id = np.asarray(res_cls_id).reshape(-1, 1)
                res_box = np.concatenate((res_cls_id, boxes.xywhn.numpy()), axis=1)

                raw_label = np.loadtxt(txt_path, dtype=np.float32).reshape(-1, 5)
                new_label = np.concatenate((raw_label, res_box), axis=0)

                fp, fn = os.path.split(txt_path)
                new_fp = fp + fp_ext
                os.makedirs(new_fp, exist_ok=True)
                np.savetxt(os.path.join(new_fp, fn), new_label, fmt='%d %.6f %.6f %.6f %.6f', delimiter=' ')


if __name__ == '__main__':
    app = Annotator(
        model='/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football/model/raw/yolov8l.pt',
        imgdata='/media/sfy/47f2d7a5-17b0-403c-94bc-4e594dc510ca/SFY/data/football_det_data/SP/2024-0605/images/train',
    )
    classes = {
        1: 'person'
    }
    app.txt_add_cls(cls=classes)

