import cv2
import logging
from .file import *


class LoadVideo:
    def __init__(self, path, step=1):
        self.path, self.fn, self.ext = splitfn(path)
        self.step = step

        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            logging.warning(f'Open Video {path} failed')

        self.frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        print(f'Load Video {path} success')
        print(f'Video Info: {self.frames} frames, {self.w}x{self.h}, {self.fps} fps')
        self.idx = -1

    def __iter__(self):
        return self

    def __next__(self):
        while 1:
            self.cap.grab()
            if (self.idx + 1) % self.step == 0:
                ret, frame = self.cap.retrieve()
                self.idx += 1
                if ret:
                    return frame
                else:
                    self.cap.release()
                    raise StopIteration
            self.idx += 1

    def set_cap(self, idx):
        idx = max(idx, 0)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        self.idx = idx - 1

    def release(self):
        if self.cap.isOpened():
            self.cap.release()


class Video:
    def __init__(self, video_path, start=0, end=0, step=1):
        self.video = LoadVideo(video_path, max(step, 1))
        self.start = start * self.video.fps
        self.end = end * self.video.fps
        self.video.set_cap(self.start)

        self.save_range = True if self.start < self.end else False

