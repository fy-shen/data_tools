import os
from pathlib import Path
import warnings
import re
import yaml


def splitfn(fn):
    path, fn = os.path.split(fn)
    name, ext = os.path.splitext(fn)
    # 文件所在路径 / 文件名 / 后缀
    return [path, name, ext]


def list_files(path):
    # path 下所有文件的文件名
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


def get_all_files(path):
    # path 下所有文件(包含子文件夹内文件)的路径
    result = []
    for root, directories, files in os.walk(path):
        for filename in files:
            result.append(os.path.join(root, filename))
    return result


def find_folders(path, target):
    # path 下所有文件夹名为 target 的路径
    result = []
    for root, dirs, files in os.walk(path):
        if target in dirs:
            result.append(os.path.join(root, target))
    return result


def find_files_with_ext(path, ext):
    # path 下所有文件名后缀在 ext 内的文件"""
    if isinstance(ext, str):
        ext = [ext]
    result = []
    for root, dirs, files in os.walk(path):
        for fn in files:
            _, fext = os.path.splitext(fn)
            if fext.lower()[1:] in ext:
                result.append(os.path.join(root, fn))
    return result


def img2txt(img_path, img_dir='images', txt_dir='labels', ext='txt'):
    return os.path.splitext(img_path.replace(img_dir, txt_dir))[0] + f'.{ext}'


def txt2img(txt_path, txt_dir='labels', img_dir='images', ext='jpg'):
    return os.path.splitext(txt_path.replace(txt_dir, img_dir))[0] + f'.{ext}'


def create_link(src, dst):
    # 创建软链接
    if os.path.exists(dst):
        if os.path.islink(dst):
            os.remove(dst)
            os.symlink(src, dst)
        else:
            warnings.warn(f"{dst} already exists and is not a symlink", UserWarning)
    else:
        os.symlink(src, dst)


def yaml_load(file='data.yaml', append_filename=False):
    """
    Load YAML data from a file.

    Args:
        file (str, optional): File name. Default is 'data.yaml'.
        append_filename (bool): Add the YAML filename to the YAML dictionary. Default is False.

    Returns:
        (dict): YAML data and file name.
    """
    assert Path(file).suffix in ('.yaml', '.yml'), f'Attempting to load non-YAML file {file} with yaml_load()'
    with open(file, errors='ignore', encoding='utf-8') as f:
        s = f.read()  # string

        # Remove special characters
        if not s.isprintable():
            s = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\uD7FF\uE000-\uFFFD\U00010000-\U0010ffff]+', '', s)

        # Add YAML filename to dict and return
        data = yaml.safe_load(s) or {}  # always return a dict (yaml.safe_load() may return None for empty files)
        if append_filename:
            data['yaml_file'] = str(file)
        return data


def yaml_save(file='data.yaml', data=None, header=''):
    """
    Save YAML data to a file.

    Args:
        file (str, optional): File name. Default is 'data.yaml'.
        data (dict): Data to save in YAML format.
        header (str, optional): YAML header to add.

    Returns:
        (None): Data is saved to the specified file.
    """
    if data is None:
        data = {}
    file = Path(file)
    if not file.parent.exists():
        # Create parent directories if they don't exist
        file.parent.mkdir(parents=True, exist_ok=True)

    # Convert Path objects to strings
    valid_types = int, float, str, bool, list, tuple, dict, type(None)
    for k, v in data.items():
        if not isinstance(v, valid_types):
            data[k] = str(v)

    # Dump data to file in YAML format
    with open(file, 'w', errors='ignore', encoding='utf-8') as f:
        if header:
            f.write(header)
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
