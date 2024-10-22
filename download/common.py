import os
import time
import requests
import urllib.parse


UNITS = ['B', 'KB', 'MB', 'GB', 'TB']


class Color:
    class W:    # 文字颜色
        black = "\033[30m"
        red = "\033[31m"
        green = "\033[32m"
        yellow = "\033[33m"
        blue = "\033[34m"
        magenta = "\033[35m"
        cyan = "\033[36m"
        white = "\033[37m"

    class B:    # 背景颜色
        black = "\033[40m"
        red = "\033[41m"
        green = "\033[42m"
        yellow = "\033[43m"
        blue = "\033[44m"
        magenta = "\033[45m"
        cyan = "\033[46m"
        white = "\033[47m"

    class S:    # 特殊效果
        bold = "\033[1m"            # 加粗
        underline = "\033[4m"       # 下划线
        blink = "\033[5m"           # 闪烁

    reset = "\033[0m"


def format_size(size, idx=None):
    if idx is None:
        idx = 0
        new_size = size
        while new_size >= 1024 and idx < len(UNITS) - 1:
            idx += 1
            new_size /= 1024

        return new_size, idx
    else:
        return size / (1024 ** idx), idx


def download_file(url, save_file, fn):
    retries = 0
    time_step = 0
    while retries < 3:
        try:
            head_response = requests.head(url)
            if head_response.status_code != 200:
                print(f"{Color.W.red}无法获取文件: {head_response.status_code}{Color.reset}")
                return

            total_length = int(head_response.headers.get('content-length', 0))
            total_size, total_unit = format_size(total_length)

            if os.path.exists(save_file):
                file_size = os.path.getsize(save_file)
                if file_size == total_length:
                    print(f'{Color.W.green}该文件已存在:{Color.reset} {urllib.parse.unquote(url)}')
                    return
            else:
                file_size = 0

            headers = {"Range": f"bytes={file_size}-"}
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code in [200, 206]:  # 200 表示全文件下载，206 表示断点续传
                print(f"{Color.W.green}开始下载:{Color.reset} {urllib.parse.unquote(url)} ({total_size:.2f} {UNITS[total_unit]})")
                with open(save_file, 'ab') as f:
                    start_time = op = time.time()
                    initial_bytes = 0
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            ed = time.time()
                            time_step += (ed - op)
                            op = ed

                            initial_bytes += len(chunk)
                            remaining_bytes = total_length - file_size - initial_bytes
                            speed = initial_bytes / (ed - start_time)

                            if time_step > 0.5:
                                speed_size, speed_unit = format_size(speed)
                                initial_size, _ = format_size(initial_bytes + file_size, idx=total_unit)
                                remaining_size, _ = format_size(remaining_bytes, idx=total_unit)
                                print(f"\r{Color.W.blue}下载速度:{Color.reset} {speed_size:.2f} {UNITS[speed_unit]}/s, "
                                      f"{initial_size:.2f} / {remaining_size:.2f} {UNITS[total_unit]}",
                                      end="")
                                time_step = 0
                print()
                if os.path.getsize(save_file) == total_length:
                    print(f"{Color.W.green}下载成功{Color.reset}")
                    return
                else:
                    retries += 1
                    print(f"{Color.W.red}Error file size. Retrying {retries}...{Color.reset}")

        except requests.exceptions.RequestException as e:
            print(f"{Color.W.red}Error occurred: {e}. Retrying {retries}...{Color.reset}")
            retries += 1

    print(f"{Color.W.red}下载失败:{Color.reset} {urllib.parse.unquote(url)}")

