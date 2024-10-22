import os
import cv2
from ultralytics import YOLO
from utils.dataload import Video


class DetectVideo(Video):
    def __init__(self, model, video, start=0, end=0, step=1):
        super().__init__(video, start, end, step)

        if isinstance(model, str):
            self.model = [YOLO(model)]
        else:
            self.model = [YOLO(m)for m in model]

    def run(self, save_dir=None, save_video=True, show_result=True, show_label=False):
        if save_dir:
            save_dir = os.path.abspath(save_dir)
            os.makedirs(save_dir, exist_ok=True)
            if save_video:
                out_file = os.path.join(save_dir, self.video.fn + '.mp4')
                fourcc = cv2.VideoWriter.fourcc(*'mp4v')
                w = int(self.video.w)
                h = int(self.video.h * len(self.model))
                out = cv2.VideoWriter(out_file, fourcc, self.video.fps, (w, h))

        if show_result:
            cv2.namedWindow('result', cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
            cv2.resizeWindow('result', 1280, 720)

        play = True
        for frame in self.video:
            if (self.save_range and self.video.idx > self.end) or self.video.idx > 1e6 - 1:
                break

            results = [m.predict(frame, imgsz=max(self.video.h, self.video.w)) for m in self.model]
            res = [result[0].plot(labels=show_label) for result in results]
            res = cv2.vconcat(res)

            if show_result:
                cv2.imshow('result', res)
                key = cv2.waitKey(1) if play else cv2.waitKey(0)
                if key == 32:
                    play = not play
                if key == 27:
                    break

            if save_dir:
                if save_video:
                    out.write(res)
                else:
                    cv2.imwrite(os.path.join(save_dir, f'{self.video.fn}_{self.video.idx:06d}.jpg'), res)

        cv2.destroyAllWindows()
        if save_dir:
            if save_video:
                out.release()


if __name__ == '__main__':
    h1, m1, s1 = 0, 3, 0  # 起始时间
    h2, m2, s2 = 0, 5, 0  # 结束时间
    detector = DetectVideo(
        model=[
            '/home/sfy/SFY/disk2/football/model/20240715-yolov8s-p2-p4/weights/best.pt',
        ],
        video='/home/sfy/SFY/NAS/Datasets/football/raw_data/videos/斑马邦/20240808/X511023510008/20240808-182936/20240808-182936.mp4',
        start=h1 * 3600 + m1 * 60 + s1,
        end=h2 * 3600 + m2 * 60 + s2,
        step=1
    )
    detector.run(
        save_dir=None,
        show_result=True
    )
