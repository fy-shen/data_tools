import os
import argparse
import requests
import urllib.parse
from bs4 import BeautifulSoup
from common import download_file
import warnings


def run(url):
    print(urllib.parse.unquote(url))
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print('链接成功')
            soup = BeautifulSoup(response.text, 'html.parser')
            for a_tag in soup.find_all('a'):
                fn = a_tag.get('href')
                if fn.endswith('.h264') or fn.endswith('.aqms'):
                    furl = url + fn if url.endswith('/') else url + '/' + fn
                    decoded_url = urllib.parse.unquote(url)
                    folder = decoded_url.split('/')[-1] if decoded_url.split('/')[-1] else decoded_url.split('/')[-2]
                    folder = folder.replace(' ', '-')
                    folder = '-'.join(filter(None, folder.split('-')))
                    save_path = os.path.join(save_dir, folder)
                    os.makedirs(save_path, exist_ok=True)
                    save_path = os.path.join(save_path, fn)
                    if os.path.exists(save_path):
                        warnings.warn(f'该文件已存在: {urllib.parse.unquote(furl)}')
                    else:
                        download_file(furl, save_path, fn)
                elif '.' not in fn:
                    sub_url = url + fn if url.endswith('/') else url + '/' + fn
                    run(sub_url)
    except requests.ConnectionError:
        print("网络问题, 连接失败")
    except requests.Timeout:
        print('请求超时')
    except requests.RequestException as e:
        print(f'请求失败: {e}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='input url')
    parser.add_argument('-o', '--output', default='datasets/download', help='save dir')
    opt = parser.parse_args()

    inp_url = opt.input
    if inp_url.endswith('#/'):
        inp_url = inp_url[:-2]
    save_dir = opt.output
    os.makedirs(save_dir, exist_ok=True)
    run(inp_url)
