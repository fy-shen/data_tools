import os
from tqdm import tqdm
import xml.etree.ElementTree as ET

from utils import IMG_FORMATS
from utils.file import find_files_with_ext


def cvat_xml2yolo_txt(image_dir, label_file, save_dir_name, task):
    tree = ET.parse(label_file)
    root = tree.getroot()
    images = root.findall('image')

    # 获取
    img_files = find_files_with_ext(image_dir, IMG_FORMATS)

    for image in tqdm(images):
        attrib = image.attrib
        h, w = float(attrib['height']), float(attrib['width'])

        """
        <id>227</id>
          <start>3000</start>
          <stop>3749</stop>
        <id>259</id>
          <start>27000</start>
          <stop>27749</stop>
        """
        # TODO: soccernet id 过滤
        # img_id = int(attrib['id'])
        # if 3749 < img_id < 27000:
        #     continue

        fn = os.path.split(attrib['name'])[-1]

        img_root = None
        for img_file in img_files:
            if img_file.endswith(attrib['name']):
                img_root = os.path.dirname(os.path.split(img_file)[0])

        if img_root is not None:
            save_path = os.path.join(img_root, save_dir_name)
            os.makedirs(save_path, exist_ok=True)
            save_file = os.path.join(save_path, fn.split('.')[0] + '.txt')

            txt = ''
            find_ball = False

            if task == 'seg':
                polygons = image.findall('polygon')
                for polygon in polygons:
                    cls = polygon.attrib['label']
                    if cls in LABELS.keys():
                        points = polygon.attrib['points'].split(';')
                        txt += str(LABELS[cls])
                        for point in points:
                            x, y = point.split(',')
                            x_ = round(float(x) / w, 6)
                            y_ = round(float(y) / h, 6)
                            txt += f' {x_} {y_}'
                        txt += '\n'
            elif task == 'det':
                boxes = image.findall('box')
                for box in boxes:
                    cls = box.attrib['label']
                    # TODO: 过滤某些标签
                    if cls == 'similar':
                        find_ball = True
                    if cls in LABELS.keys():
                        xl, yl, xr, yr = map(
                            float, [box.attrib['xtl'], box.attrib['ytl'], box.attrib['xbr'], box.attrib['ybr']]
                        )
                        x = round((xl + xr) / (2 * w), 6)
                        y = round((yl + yr) / (2 * h), 6)
                        w_ = round(abs(xr - xl) / w, 6)
                        h_ = round(abs(yr - yl) / h, 6)
                        txt += f'{LABELS[cls]} {x} {y} {w_} {h_}\n'
            else:
                raise ValueError(f'Unsupported task: {task}')

            if txt:
                with open(save_file, mode='w') as fp:
                    fp.writelines(txt)


if __name__ == '__main__':
    # TODO: 定义xml中标签名对应的类别id
    LABELS = {
        'ball': 0,
        'shadow': 0,
        'cover': 0,
        'similar': 0
    }
    image_dir = '/home/sfy/SFY/disk2/football/bmb/2024-0813/raw/val_images'
    label_file = '/home/sfy/SFY/disk2/football/bmb/2024-0813/raw/annotation/val_manual.xml'
    # label_dir = '/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football/sp/2024-0605/raw/annotation/train'
    # for lf in find_files_with_ext(label_dir, 'xml'):
    cvat_xml2yolo_txt(
        image_dir=image_dir,
        label_file=label_file,
        save_dir_name='val_labels',
        task='det'
    )
