import os
import random
from utils.file import find_files_with_ext, img2txt, create_link


class GenTXT:
    def __init__(self, root_dir, data_dir, txt_fn):
        self.root_dir = root_dir
        self.data_dir = data_dir
        self.txt_path = os.path.join(root_dir, txt_fn)
        if os.path.exists(self.txt_path):
            os.remove(self.txt_path)

    def save_txt(self, imgs):
        with open(self.txt_path, 'a') as f:
            for img in imgs:
                relative_path = os.path.relpath(img, self.root_dir)
                f.write(f'./{relative_path}\n')

    def normal(self, data_dir=None, ext='jpg', num=None):
        if data_dir is None:
            data_dir = self.data_dir
        imgs = find_files_with_ext(data_dir, ext)
        imgs = [p for p in imgs if os.path.exists(img2txt(p))]
        imgs = random.sample(imgs, min(num, len(imgs))) if num else imgs
        self.save_txt(imgs)

    def soccernet(self, num=None):
        for dn in os.listdir(self.data_dir):
            img_src = os.path.join(self.data_dir, dn, 'images_raw')
            img_link = os.path.join(self.data_dir, dn, 'images')
            label_src = os.path.join(self.data_dir, dn, 'labels_0508')
            label_link = os.path.join(self.data_dir, dn, 'labels')
            if os.path.exists(img_src) and os.path.exists(label_src):
                create_link(img_src, img_link)
                create_link(label_src, label_link)
            else:
                continue

            self.normal(img_link, num=num)


if __name__ == '__main__':
    app = GenTXT(
        root_dir='/media/sfy/47f2d7a5-17b0-403c-94bc-4e594dc510ca/SFY/data/football_det_data',
        data_dir='/media/sfy/47f2d7a5-17b0-403c-94bc-4e594dc510ca/SFY/data/football_det_data/SP/2024-0605/images/train',
        txt_fn='data9-SP-2024-0605-train.txt'
    )
    app.normal()
    # app.soccernet(num=200)

