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
        root_dir='/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football',
        data_dir='/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football/soccernet/train',
        txt_fn='data5-soccernet-train.txt'
    )

    app.soccernet(num=200)

