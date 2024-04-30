import cv2
import numpy as np


class Colors:
    """
    Ultralytics default color palette https://ultralytics.com/.

    This class provides methods to work with the Ultralytics color palette, including converting hex color codes to
    RGB values.

    Attributes:
        palette (list of tuple): List of RGB color values.
        n (int): The number of colors in the palette.
        pose_palette (np.array): A specific color palette array with dtype np.uint8.
    """

    def __init__(self):
        """Initialize colors as hex = matplotlib.colors.TABLEAU_COLORS.values()."""
        hexs = ('FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB',
                '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7')
        self.palette = [self.hex2rgb(f'#{c}') for c in hexs]
        self.n = len(self.palette)
        self.pose_palette = np.array([[255, 128, 0], [255, 153, 51], [255, 178, 102], [230, 230, 0], [255, 153, 255],
                                      [153, 204, 255], [255, 102, 255], [255, 51, 255], [102, 178, 255], [51, 153, 255],
                                      [255, 153, 153], [255, 102, 102], [255, 51, 51], [153, 255, 153], [102, 255, 102],
                                      [51, 255, 51], [0, 255, 0], [0, 0, 255], [255, 0, 0], [255, 255, 255]],
                                     dtype=np.uint8)

    def __call__(self, i, bgr=False):
        """Converts hex color codes to RGB values."""
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h):
        """Converts hex color codes to RGB values (i.e. default PIL order)."""
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))


colors = Colors()


class Annotator:
    def __init__(self, img, line_width=None):
        self.lw = line_width or max(round(sum(img.shape) / 2 * 0.003), 2)
        self.img = img
        self.font_thick = max(self.lw - 1, 1)  # font thickness
        self.font_scale = self.lw / 3  # font scale

    def draw_box(self, box, label='', color=(128, 128, 128), txt_color=(255, 255, 255)):
        p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
        cv2.rectangle(self.img, p1, p2, color, thickness=self.lw, lineType=cv2.LINE_AA)
        if label:
            w, h = cv2.getTextSize(label, 0, fontScale=self.font_scale, thickness=self.font_thick)[0]  # text width, height
            outside = p1[1] - h >= 3
            p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
            cv2.rectangle(self.img, p1, p2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(self.img, label,
                        (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),
                        0,
                        self.font_scale,
                        txt_color,
                        thickness=self.font_thick,
                        lineType=cv2.LINE_AA)

    def draw_mask(self, points, label='', color=(128, 128, 128), txt_color=(255, 255, 255)):
        mask = np.zeros_like(self.img, np.uint8)
        cv2.fillPoly(mask, points, color)
        self.img = (self.img * (np.ones_like(self.img)-(mask > 0).astype(np.int32)*0.5) + mask*0.5).astype(np.uint8)
