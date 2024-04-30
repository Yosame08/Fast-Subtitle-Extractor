# Fast-Subtitle-Extractor

A self-selected topic for project1 of CV course at FDU originally (finished), with practical use.

Features not implemented yet:

- Recognize subtitles while translating to other languages

Feel free to develop more features for this code!

## Brief Introduction

Based on [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) with simple image enhancement, frame skipping and text correction, thus ensuring both efficiency and accuracy.

## Requirements

`Python3` and libraries:

- `paddlepaddle` or `paddlepaddle-gpu`
- `paddleocr`
- `tqdm`
- `opencv-python`

## Usage

`python main.py video.mp4 [-o out.srt] [-w 500 1000] [-t 800 900] [-b 1000] [-e 2000]`

Replace `video.mp4` with the video file from which the subtitles need to be extracted.

(Optional) If you want to specify the output file name, use `-o`.

(**highly recommended**, Optional) Use `-w` `-t` to specify the rectangular range where the subtitles are located, with the upper left corner as the origin (0,0)

(Optional) Use `-b` `-e` to specify the beginning frame and the ending frame.

If you want to recognize languages other than Simplified Chinese, please modify `config.ini`, and see the repository of PaddleOCR for the corresponding language code.

**The default code is only available when brightness of the subtitle is high. If brightness is low, you may need to refer to the following description *(Structure 2.)* and modify the code.**

## Structure

![structure](img/structure.png)

### 1. Preprocess

Extract arguments from input. Crops a frame to a user-specified caption range before OCR.

### 2. Image Enhancement

First map the brightness of the low brightness region to 0, then map the brightness of the remaining region to 127~255.
If the color of the subtitle does not meet this requirement (low brightness), you may need to disable image enhancement, or modify the corresponding code (`correction(area)` in main.py) to achieve a better result.

### 3. Text Recognition

If a number of consecutive frames have the same/no subtitles, skip frames to speed up the process, and if it is found that the subtitle start/end position has been skipped, bisect the interval to find the exact position.

### 4. Text Correction

The similarity is calculated with the last recognized text.
If the similarity is high, the text is treated as the same subtitle and the one with higher confidence is selected as the correct subtitle.
If the text is short (only one non-Chinese character) or short in duration (<0.3s), it will be treated as misrecognized and ignored.

## Experiment

Comparing speed and accuracy using the first episode of ***Rampage《狂飙》***(Requirements of course project) with [Video-Subtitle-Extractor](https://github.com/YaoFANGUK/video-subtitle-extractor)'s Quick Mode, speed increased by about 12% and correctness increased by about 4%.

