import os
import argparse
from copy import deepcopy

import cv2
import numpy as np

from utils.plotting import Annotator, colors
from utils.file import splitfn, img2txt


def xywh2xyxy(box):
    x, y, w, h = box
    x1 = x - w / 2
    x2 = x + w / 2
    y1 = y - h / 2
    y2 = y + h / 2
    return np.asarray([x1, y1, x2, y2])


def show_label(image, label, task='detect'):
    cv2.namedWindow('show_label', cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
    play = False
    is_txt = False
    if os.path.isfile(image) and image.endswith('.txt'):
        is_txt = True

    if is_txt:
        image_dir, _, _ = splitfn(image)
        with open(image, 'r') as f:
            image_paths = [os.path.join(image_dir, p.split()[0]) for p in f.readlines()]
    else:
        image_paths = [os.path.join(image, image_file) for image_file in sorted(os.listdir(image))]

    for image_path in image_paths:
        if is_txt:
            label_path = img2txt(image_path)
        else:
            _, fn, _ = splitfn(image_path)
            label_path = os.path.join(label, f'{fn}.txt') if label else img2txt(image_path)

        if os.path.exists(label_path):
            with open(label_path, 'r') as lf:
                objs = lf.readlines()

            print(f'\r{image_path}', end='')
            img = cv2.imread(image_path)
            h, w = img.shape[:2]

            annotator = Annotator(deepcopy(img))

            for obj in objs:
                info = np.asarray(obj.split()).astype(np.float32)
                cls = int(info[0])
                txt = f'{cls}: {names[cls]}'
                if task == 'detect':
                    box = info[1:] * [w, h, w, h]
                    box = xywh2xyxy(box).astype(np.int32)
                    annotator.draw_box(box, txt, color=colors(cls, True))

                if task == 'seg':
                    points = info[1:].reshape((-1, 2)) * [w, h]
                    points = points.astype(np.int32).reshape(1, -1, 2)
                    annotator.draw_mask(points, txt, color=colors(cls, True))

            cv2.imshow('show_label', annotator.img)
            key = cv2.waitKey(50) if play else cv2.waitKey(0)
            if key == 32:
                play = not play
            if key == 27:
                cv2.destroyAllWindows()
                exit()

        else:
            print(f'\'{image_path}\' label not found')


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str,
                        help='image data dir or yolo format txt',
                        default='/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football/data5-soccernet-train.txt')
    parser.add_argument('--label', type=str,
                        help='label data dir',
                        default='/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football/soccernet/train/SNMOT-061/labels_0508')
    parser.add_argument('--task', choices=['detect', 'seg', 'pose'],
                        help='select task i.e. detect, seg, pose',
                        default='detect')
    return parser.parse_args()


names = {
    0: 'ball',
    1: 'person',
}

if __name__ == '__main__':
    opt = parse_opt()
    show_label(**vars(opt))
