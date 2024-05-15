import time
import requests
import urllib.parse


UNITS = ['B', 'KB', 'MB', 'GB', 'TB']


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
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_length = int(response.headers.get('content-length'))
        total_size, total_unit = format_size(total_length)
        print(f"Downloading: {urllib.parse.unquote(url)} ({total_size:.2f} {UNITS[total_unit]})...")

        with open(save_file, 'wb') as f:
            start_time = time.time()
            initial_bytes = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    duration = time.time() - start_time
                    f.write(chunk)
                    initial_bytes += len(chunk)
                    remaining_bytes = total_length - initial_bytes
                    speed = initial_bytes / duration

                    speed_size, speed_unit = format_size(speed)
                    initial_size, _ = format_size(initial_bytes, idx=total_unit)
                    remaining_size, _ = format_size(remaining_bytes, idx=total_unit)
                    print(f"\rDownload average speed: {speed_size:.2f} {UNITS[speed_unit]}/s, "
                          f"{initial_size:.2f} / {remaining_size:.2f} {UNITS[total_unit]}",
                          end="")
        print()
    else:
        print(f"Failed to download {fn}.")

