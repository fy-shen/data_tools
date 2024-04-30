import os
import cv2

from utils.dataload import LoadVideo
from utils.file import yaml_load, yaml_save


class SplitVideo:
    def __init__(self, video_path, save_dir, start=0, end=0, step=1, max_n=-1, datatype=None, database='cfg/database.yaml'):
        self.video_path = video_path
        self.save_dir = os.path.abspath(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        self.step = step
        self.max_n = max_n
        self.database = self.load_database(database)
        self.datatype = datatype

        self.video = LoadVideo(video_path, max(step, 1))
        self.start = start * self.video.fps
        self.end = end * self.video.fps
        self.video.set_cap(self.start)

        self.save_range = True if self.start < self.end else False
        self.save_num = True if self.max_n > 0 else False
        self.save_n = 0

    def img_fn(self):
        # TODO: 注意修改文件名
        if self.datatype == 'SR':
            # 思锐AI: 去除中文场地名前缀
            fn = '_'.join(self.video.fn.split('_')[1:]) + f'_{self.video.idx:06d}.jpg'
        else:
            # 常用文件名: 视频文件名_帧数.jpg
            fn = self.video.fn + f'_{self.video.idx:06d}.jpg'
        return fn

    def load_database(self, database):
        data = yaml_load(database)
        data['database'].append(self.save_dir) if self.save_dir not in data['database'] else None
        yaml_save(database, data)
        return data

    def check_database(self, fn):
        for datadir in self.database['database']:
            if os.path.exists(os.path.join(datadir, fn)):
                return True
        return False

    def save_frame(self, fn, frame):
        cv2.imwrite(os.path.join(self.save_dir, fn), frame)
        self.save_n += 1
        return self.save_num and self.save_n == self.max_n

    def auto_split(self):
        for frame in self.video:
            idx = self.video.idx
            message = f'\r{idx} / {self.end}' if self.save_range else f'\r{idx} / {self.video.frames}'
            print(message, end='')
            # 超出预设范围或帧索引值超过6位数停止
            if (self.save_range and idx > self.end) or idx > 1e6 - 1:
                break

            fn = self.img_fn()
            if self.check_database(fn):
                # 当前帧在数据库中已存在
                continue
            if self.save_frame(fn, frame):
                break

        self.video.release()

    def manual_split(self, model=None, conf=0.25, show_label=False):
        if model is not None:
            from ultralytics import YOLO
            model = YOLO(model)

        play = False
        cv2.namedWindow('split video', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        for frame in self.video:
            idx = self.video.idx
            print(f'\r{idx} / {self.video.frames}', end='')
            if (self.save_range and idx > self.end) or idx > 1e6 - 1:
                break

            if model is not None:
                results = model.predict(frame, imgsz=max(self.video.h, self.video.w), conf=conf)
                res = results[0].plot(labels=show_label)
                cv2.imshow('split video', res)
            else:
                cv2.imshow('split video', frame)

            key = cv2.waitKey(1) if play else cv2.waitKey(0)
            if key == 32:
                play = not play
            if key == 27:
                break
            if key == ord('s'):
                fn = self.img_fn()
                if self.check_database(fn):
                    continue
                if self.save_frame(fn, frame):
                    break
            if key == ord('a'):
                self.video.set_cap(idx - 1)
        self.video.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    h1, m1, s1 = 0, 0, 0    # 起始时间
    h2, m2, s2 = 0, 0, 0    # 结束时间
    app = SplitVideo(
        video_path='/home/sfy/SFY/NAS/Datasets/football/思锐AI/温州移动-2/温州移动-2_0750-0848_2024-0201_dd24f7faa84e.mp4',
        save_dir='/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football/SR-AI/2024-0424/raw/images',
        start=h1*3600 + m1*60 + s1,
        end=h2*3600 + m2*60 + s2,
        step=1,
        max_n=-1,
        datatype='SR'
    )

    # app.auto_split()
    app.manual_split(
        model='/media/sfy/91a012f8-ed6a-4c03-898c-359294a3c17f/sfy/football/model/20240423-yolov8s-p2/weights/best.pt',
    )
