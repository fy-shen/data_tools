
import os
import shutil
import random
from tqdm import tqdm
import warnings

from utils.file import list_files, find_folders


def random_copy_file(src, dst, num, mode='copy'):
    # 随机选取 src 下若干个文件复制或移动到 dst 下
    # num: 选取文件数量, 0 < num < 1 表示选取文件比例, 1 <= num 表示选取文件数量, num < 0 表示选取所有文件
    os.makedirs(dst, exist_ok=True)
    files = list_files(src)
    if num >= 1:
        selected_files = random.sample(files, int(num))
    elif 0 < num < 1:
        selected_files = random.sample(files, int(num * len(files)))
    else:
        selected_files = files

    for file in tqdm(selected_files):
        src_file = os.path.join(src, file)
        dst_file = os.path.join(dst, file)
        if mode == 'copy':
            shutil.copy(src_file, dst_file)
        elif mode == 'move':
            shutil.move(src_file, dst_file)


def copy_files_base_ref(src, dst, ref, ext, mode='copy'):
    # 将 src 下与 ref 对应的文件(后缀替换为ext)复制到 dst
    # 例如将 labels 中与 images_train 内图像对应的标签移动到 labels_train 下
    # 常用于划分训练验证集后划分对应的标签
    os.makedirs(dst, exist_ok=True)
    files = list_files(src)
    for file in tqdm(files):
        ref_file = os.path.join(ref, file.split('.')[0] + ext)
        if os.path.exists(ref_file):
            src_file = os.path.join(src, file)
            dst_file = os.path.join(dst, file)
            if mode == 'copy':
                shutil.copy(src_file, dst_file)
            elif mode == 'move':
                shutil.move(src_file, dst_file)


def rename_dirs(src, dst, root):
    # 将 root 下所有名为 src 的文件夹重命名为 dst
    src_dirs = find_folders(root, src)
    for src_dir in src_dirs:
        dst_dir = os.path.join(os.path.dirname(src_dir), dst)
        if os.path.exists(dst_dir):
            warnings.warn(f"{dst_dir} already exists, skipping...", UserWarning)
        else:
            os.rename(src_dir, dst_dir)
            print(f'Renamed {src_dir} --> {dst_dir}')


if __name__ == '__main__':
    # 1. 移动验证数据
    random_copy_file(
        src='/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football/sp/2024-0605/raw/images',
        dst='/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football/sp/2024-0605/raw/val_images_raw',
        num=0.3,
        mode='move'
    )

    # 2. 移动剩余数据到训练集文件夹
    random_copy_file(
        src='/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football/sp/2024-0605/raw/images',
        dst='/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football/sp/2024-0605/raw/train_images_raw',
        num=-1,
        mode='move'
    )

    # random_copy_file(
    #     src='/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football/wuxi/2024-0115/raw/images_all',
    #     dst='/media/sfy/47f2d7a5-17b0-403c-94bc-4e594dc510ca/SFY/data/football_det_data/calibrate',
    #     num=50,
    #     mode='copy'
    # )
