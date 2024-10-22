import os
from datetime import datetime
import cv2
import numpy as np
import xml.etree.ElementTree as ET

from ultralytics import YOLO
from utils import IMG_FORMATS
from utils.file import find_files_with_ext, img2txt, splitfn


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

                # 过滤小人
                res_box = res_box[res_box[:, -2] * res_box[:, -1] * iw * ih > 260]

                raw_label = np.loadtxt(txt_path, dtype=np.float32).reshape(-1, 5)
                new_label = np.concatenate((raw_label, res_box), axis=0)

                fp, fn = os.path.split(txt_path)
                new_fp = fp + fp_ext
                os.makedirs(new_fp, exist_ok=True)
                np.savetxt(os.path.join(new_fp, fn), new_label, fmt='%d %.6f %.6f %.6f %.6f', delimiter=' ')

    def annotate_xml(self, xml_file, cls):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for image in root.findall('image'):
            attrib = image.attrib
            img_fn = os.path.split(attrib['name'])[-1]
            h, w = int(attrib['height']), int(attrib['width'])

            img_path = None
            for img in self.imgs:
                if img_fn == os.path.basename(img):
                    img_path = img
                    self.imgs.remove(img)

            if img_path is not None:
                results = self.model(img_path, imgsz=max(h, w), classes=self.name2id(self.model.names, cls.values()))
                for box in results[0].boxes:
                    self.add_box_xml(image, box)

        save_dir, xml_fn, _ = splitfn(os.path.abspath(xml_file))
        tree.write(os.path.join(save_dir, f'{xml_fn}_auto.xml'))

    def add_box_xml(self, image, box):
        cls = int(box.cls)
        x1, y1, x2, y2 = box.xyxy[0]
        new_box = ET.SubElement(image, 'box')
        new_box.set('label', self.model.names[cls])
        new_box.set('source', 'auto_generated')
        new_box.set('occluded', '0')
        new_box.set('xtl', f'{x1:.2f}')
        new_box.set('ytl', f'{y1:.2f}')
        new_box.set('xbr', f'{x2:.2f}')
        new_box.set('ybr', f'{y2:.2f}')
        new_box.set('z_order', '0')


if __name__ == '__main__':
    app = Annotator(
        model='models/detect/yolov8l.pt',
        imgdata='/home/sfy/SFY/disk2/football/bmb/2024-0813/raw/val_images',
    )
    classes = {
        1: 'person'
    }
    app.txt_add_cls(cls=classes)

    # app = Annotator(
    #     model='/home/sfy/SFY/disk2/football/model/20240715-yolov8s-p2-p4/weights/best.pt',
    #     imgdata='/home/sfy/SFY/disk2/football/bmb/2024-0813/raw/train_images',
    # )
    # classes = {
    #     0: 'ball'
    # }
    # app.annotate_xml(
    #     xml_file='/home/sfy/SFY/disk2/football/bmb/2024-0813/raw/annotation/train.xml',
    #     cls=classes
    # )

