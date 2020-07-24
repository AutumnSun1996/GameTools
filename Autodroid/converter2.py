import os
import time

import numpy as np
import cv2 as cv


class CircleVideo:
    def __init__(self, video_name, frame_count=1):
        video = cv.VideoCapture(video_name)
        self.fps = video.get(cv.CAP_PROP_FPS)
        self.frames = []
        for i in range(frame_count):
            ret, img = video.read()
            if not ret:
                break
            self.frames.append(img)
        video.release()
        self.h, self.w = self.frames[0].shape[:2]
        self.idx = -1

    def next(self, fps=None):
        if fps is None:
            self.idx += 1
        else:
            self.idx += self.fps / fps

        if self.idx >= len(self.frames):
            self.idx -= len(self.frames)

        return self.frames[int(self.idx)].copy()


def cv_crop(data, rect):
    """图片裁剪"""
    min_x, min_y, max_x, max_y = rect
    return data[min_y:max_y, min_x:max_x]


def color_point(b, g, r):
    return (r, g, b)


def color_dist(c1, c2):
    b1, g1, r1 = c1
    b2, g2, r2 = c2
    rmean = (r1 + r2) / 2
    r = r1 - r2
    g = g1 - g2
    b = b1 - b2
    return np.sqrt(
        (2 + rmean / 256) * (r ** 2)
        + 4 * (g ** 2)
        + (2 + (255 - rmean) / 256) * (b ** 2)
    )


def frame2pixels(frame, w, h, candidates):
    res = np.zeros((h, w, 3), dtype="float")
    fh, fw = frame.shape[:2]
    ph = fh // h
    pw = fw // w
    for i in range(w):
        for j in range(h):
            source = frame[ph * j : ph * (j + 1), pw * i : pw * (i + 1), :]
            point = cv.resize(source, (1, 1))
            cur = np.array(color_point(*point[0, 0, :].tolist()))
            best = min(candidates, key=lambda c: color_dist(cur, c))
            res[j, i, :] = best
    return res


def pixels2board(board, pixels):
    draw = board.copy()
    rows = 37
    cols = 22
    dx = dy = 20
    for i in range(rows):
        for j in range(cols):
            color = tuple(pixels[j, i].tolist())
            x, y = 1 + dx * i, 1 + dy * j
            draw[y : y + dy, x : x + dx, :] = candidates[color]
    return draw


def get_full_board(shot, multi_x, multi_y):
    pixels = frame2pixels(shot, 37 * multi_x, 22 * multi_y, candidates)
    bh, bw = board.shape[:2]
    fw = bw * multi_x
    fh = bh * multi_y
    full_board = np.zeros((fh, fw, 3), dtype="uint8")
    for x in range(multi_x):
        for y in range(multi_y):
            full_board[bh * y : bh * (y + 1), bw * x : bw * (x + 1), :] = pixels2board(
                pixels[22 * y : 22 * (y + 1), 37 * x : 37 * (x + 1), :]
            )
    return full_board


if __name__ == "__main__":
    base = CircleVideo("./PlayerSimulate/AzurLaneBase.mp4", 457)
    base.idx = 300
    img = base.next()

    bx, by = 277, 108
    bw, bh = 742, 442
    board = cv_crop(img, (bx, by, bx + bw, by + bh))

    dx = dy = 20
    rows = 37
    cols = 22
    candidates = {}
    for i in range(8):
        cell = cv_crop(board, (1 + dx * i, 1 + dy * 2, 1 + dx * (i + 1), 1 + dy * 3))
        color = color_point(*cell[3, 3, :].tolist())
        candidates[color] = cell

    name_in = r"d:\Videos\[Monogatari Series][SFEO-Raws][BD][720P x264 10bit AAC]\01 化物语\[SFEO-Raws] Bakemonogatari - OP_04 (BD 720P x264 10bit AAC)[9FEF0AF8].mp4"
    name_tmp = "./PlayerSimulate/tmp.mp4"

    video_in = cv.VideoCapture(name_in)
    fps = np.round(video_in.get(cv.CAP_PROP_FPS))

    h, w = img.shape[:2]
    print("Convert {} to {}".format(name_in, name_tmp))
    video_out = cv.VideoWriter(
        name_tmp,
        apiPreference=cv.CAP_FFMPEG,
        fourcc=cv.VideoWriter_fourcc(*"mp4v"),
        fps=fps,
        frameSize=(w, h),
    )

    start = last_log = time.time()
    last_frame = 0
    frame_count = 0
    while 1:
        ret, frame = video_in.read()
        if not ret:
            break
        in_h, in_w = frame.shape[:2]
        background = base.next(fps)
        painted_board = pixels2board(board, frame2pixels(frame, rows, cols, candidates))
        background[by : by + bh, bx : bx + bw, :] = painted_board
        video_out.write(background)
        frame_count += 1
        now = time.time()
        if now - last_log > 1:
            process_fps = (frame_count - last_frame) / (now - last_log)
            print("\r{:6d}  {:.2f}fps".format(frame_count, process_fps), end="")
            last_log = now
            last_frame = frame_count
    process_fps = (frame_count) / (now - start)
    print("\r{:6d}  {:.2f}fps".format(frame_count, process_fps))
    video_in.release()
    video_out.release()
    cv.destroyAllWindows()

    name_out = (
        "./PlayerSimulate/"
        + os.path.splitext(os.path.basename(name_in))[0]
        + "-AzurLanePlayer2.mp4"
    )
    print("Combine to {}".format(name_out))
    scale_w = int(base.w / 4)
    scale_h = int(in_h * scale_w / in_w)
    os.system(
        'ffmpeg -y -i "{0}" -i "{1}" -filter_complex "[0]scale=w={2}:h={3}[s];[1][s]overlay=x=main_w-overlay_w:y=main_h-overlay_h" -c:a aac -c:v h264 "{4}"'.format(
            name_in, name_tmp, scale_w, scale_h, name_out
        )
    )
