import argparse
import os
import cv2
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.file import find_files_with_ext, splitfn
from utils.dataload import LoadVideo

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', required=True, help='data path')
    opt = parser.parse_args()

    videos = find_files_with_ext(opt.path, 'mp4')
    for v in videos:
        fp, fn, _ = splitfn(v)
        save_path = os.path.join(os.path.dirname(fp), '预览图')
        os.makedirs(save_path, exist_ok=True)
        img = os.path.join(save_path, fn + '.jpg')
        if not os.path.exists(img):
            vid = LoadVideo(v)
            vid.set_cap(vid.frames // 2)
            frame = next(vid)
            cv2.imwrite(img, frame)
