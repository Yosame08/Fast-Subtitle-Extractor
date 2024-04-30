# Fast-Subtitle-Extractor
A self-selected topic for project1 of CV course at FDU originally, with practical use.

## Brief Introduction

Based on [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) with simple image enhancement, frame skipping and text correction, thus ensuring both efficiency and accuracy.

## Usage

`python main.py video.mp4 [-o out.srt] [-w 500 1000] [-t 800 900] [-b 1000] [-e 2000]`

Replace `video.mp4` with the video file from which the subtitles need to be extracted.

(Optional) If you want to specify the output file name, use `-o`.

(**highly recommended**, Optional) Use `-w` `-t` to specify the rectangular range where the subtitles are located, with the upper left corner as the origin (0,0)

(Optional) Use `-b` `-e` to specify the beginning frame and the ending frame.

## Structure

