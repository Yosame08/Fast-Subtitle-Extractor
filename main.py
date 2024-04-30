"""
This script is used to extract subtitles from a video file.

Usage:
python main.py video.mp4 -o output.srt -w 100 200 -t 50 150 -tr
-o is an optional argument to specify the output file name.
-w and -h are optional arguments to specify the width and height of the subtitle area.
-b and -e are optional arguments to specify the beginning and ending frame numbers, -b inclusive and -e exclusive.
-tr is an optional argument that enables text translation. You need to set the destination languages in the config.ini file.
"""
import cv2
import numpy as np
import logging
import argparse
from configparser import ConfigParser
from tqdm import tqdm
from PIL import ImageFont, ImageDraw, Image
from paddleocr import PaddleOCR

from SRT import SRT
print("Imported modules successfully")

parser = argparse.ArgumentParser(description='Process video file.')
parser.add_argument('video_file', type=str, help='Path to the video file')
parser.add_argument('-o', '--output', type=str, help='Name of output SRT file')
parser.add_argument('-w', '--width', type=int, nargs=2, help='Width range of subtitle')
parser.add_argument('-t', '--tall', type=int, nargs=2, help='Height range of subtitle')
parser.add_argument('-b', '--begin', type=int, help='The beginning frame, inclusive')
parser.add_argument('-e', '--end', type=int, help='The ending frame, exclusive')
# parser.add_argument('-tr', '--translate', action='store_true', help='Translate the subtitle')
args = parser.parse_args()
video_file = args.video_file
output_file = args.output if args.output else 'output.srt'

conf = ConfigParser()
conf.read('config.ini')
font_name = conf.get('OCR', 'FontName')
src_lang = conf.get('OCR', 'SrcLang')
dst_lang = conf.get('OCR', 'DstLang')

font = ImageFont.truetype(font_name, 18)
ocr = PaddleOCR(use_angle_cls=False, cls=False, use_gpu=True, lang='ch', det=True, rec=True, show_log=False)
logging.disable(logging.DEBUG)
logging.disable(logging.WARNING)

cap = cv2.VideoCapture(video_file)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_duration = 1.0 / fps
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width_range = args.width if args.width else [0, int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))]
tall_range = args.tall if args.tall else [0, int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
beginning = int(args.begin) if args.begin else 0
ending = int(args.end) if args.end else total_frames

print("Parameters: ")
print(f"Input: {video_file}    Output: {output_file}")
print(f"Frames: [{beginning}, {ending}], {fps}fps ")
print(f"Rect: ({width_range[0]}, {tall_range[0]}), ({width_range[1]}, {tall_range[1]})")

if beginning >= ending:
    raise ValueError("Invalid frame range")
if beginning < 0 or beginning > total_frames:
    raise ValueError("Invalid beginning frame number")
print("Video loaded successfully")

def correction(area):
    # 灰度化
    area = np.amin(area, axis=2, keepdims=False)
    area[area < 210] = 0
    # 线性映射
    bright = area > 0
    area[bright] = (area[bright] - 170) * 3
    return area.astype(np.uint8)

def update(frame, text) -> bool:
    image_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(image_pil)
    draw.text((0, 0), text, font=font, fill=255)
    cv2.imshow('Processed Image', np.array(image_pil))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return False
    return True

def recognize(frame):
    subtitle_area = correction(frame[tall_range[0]:tall_range[1], width_range[0]:width_range[1]])
    result = ocr.ocr(subtitle_area)
    if len(result) > 1:
        print(result[1])
    assert len(result) == 1
    return subtitle_area, result[0]

clip_cache = []

def bin_search(l: int, r: int, bg_frm: int, srt: SRT) -> int:
    while l < r:
        mid = (l + r) // 2
        # cap.set(cv2.CAP_PROP_POS_FRAMES, mid)
        # _, frame = cap.read()
        _, result = recognize(clip_cache[mid - bg_frm])
        current_text, confidence, similar = srt.correction("" if result is None else result)
        if similar >= 0.85:
            l = mid + 1
        else:
            r = mid
    return l

def main():
    if not cap.set(cv2.CAP_PROP_POS_FRAMES, beginning):
        raise ValueError("Invalid beginning frame number")

    global clip_cache
    srt = SRT(output_file, ending/fps)  # if not args.translate else SRT(output_file, dst_lang[0]==src_lang, True, dst_lang)
    step = 0
    stp_lim = int(fps / 2.5)
    pbar = tqdm(total=ending - beginning, desc="Processing frames")
    at_frame = int(beginning)
    clip_cache = []
    while True:
        new_frame = int(at_frame + step)
        for _ in range(step-1):
            ret, frame = cap.read()
            if not ret:
                break
            clip_cache.append(frame)
        pbar.update(step)
        ret, frame = cap.read()
        clip_cache.append(frame)
        if not ret: break
        else:
            subtitle_area, result = recognize(frame)
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            current_text, confidence, similar = srt.correction("" if result is None else result)

            if step == 0:
                srt.begin(current_text, confidence, similar)
                srt.set_begin(timestamp)
                step = 1
                clip_cache = [frame]
                continue

            if similar >= 0.85:
                if step == 0:
                    step = 1
                elif step < stp_lim:
                    step += 1 if step == 1 else 2
                    if step > stp_lim:
                        step = stp_lim
            else:
                ed_frame = bin_search(at_frame, new_frame-1, at_frame, srt)
                srt.set_end(ed_frame/fps)
                srt.begin(current_text, confidence, 1)
                if current_text != "":
                    srt.set_begin(bin_search(ed_frame+1, new_frame, at_frame, srt)/fps)
                step = 1

            if not update(subtitle_area, current_text):
                break

            at_frame = new_frame
            clip_cache = [frame]

    del srt
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()