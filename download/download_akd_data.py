import argparse
import urllib.parse
from bs4 import BeautifulSoup
from common import *
import subprocess


def run(url, save_dir):
    print(urllib.parse.unquote(url))
    try:
        find_file = False
        sub_find_file = False
        response = requests.get(url)
        if response.status_code == 200:
            print('链接成功')
            soup = BeautifulSoup(response.text, 'html.parser')

            decoded_url = urllib.parse.unquote(url)
            folder = decoded_url.split('/')[-1] if decoded_url.split('/')[-1] else decoded_url.split('/')[-2]
            folder = folder.replace(' ', '-')
            folder = '-'.join(filter(None, folder.split('-')))
            save_path = os.path.join(save_dir, folder)
            os.makedirs(save_path, exist_ok=True)

            for a_tag in soup.find_all('a'):
                fn = a_tag.get('href')
                if fn.endswith('.h264') or fn.endswith('.aqms'):
                    find_file = True
                    furl = url + fn if url.endswith('/') else url + '/' + fn
                    save_file = os.path.join(save_path, fn)

                    download_file(furl, save_file, fn)

                elif '.' not in fn:
                    sub_url = url + fn if url.endswith('/') else url + '/' + fn
                    sub_find_file = sub_find_file | run(sub_url, save_path)

            if sub_find_file:
                process = subprocess.Popen(["./akd_convert.sh", save_path], stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=True)
                for line in process.stdout:
                    print(line, end="")
                process.wait()

            return True if find_file else False

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

    os.makedirs(opt.output, exist_ok=True)
    run(inp_url, opt.output)
