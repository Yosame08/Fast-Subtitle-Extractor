import difflib
import re


def seconds_to_timestamp(second):
    hours = int(second // 3600)
    minutes = int((second % 3600) // 60)
    seconds = int(second % 60)
    milliseconds = int(second * 1000) % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


class SRT:
    def __init__(self, output_file, finish, keep = True, translate = False, trans_dst = None):
        self.index = 1
        self.start = 0
        self.st_str = ""
        self.last = ""
        self.confidence = 0.0
        self.finish = finish
        self.f = open(output_file, 'w', encoding='utf-8')

        self.keep = keep
        self.translate = translate
        self.trans_dst = trans_dst

    def correction(self, results):
        max_confidence = 0
        selected_text = ""

        if results == "":
            max_confidence = 0.9
        else:
            for result in results:
                text = result[1][0]
                if len(text) == 1 and not re.search(r'[\u4e00-\u9fff]', text):
                    text = ''  # 单个字符且非中文，更正为空字符串
                confidence = result[1][1]
                if selected_text == "":
                    selected_text = text
                    max_confidence = confidence
                elif confidence > 0.8:
                    if max_confidence < 0.8:
                        selected_text = text
                    else:
                        selected_text += f" {text}"
                    if confidence > max_confidence:
                        max_confidence = confidence
        return selected_text, max_confidence, difflib.SequenceMatcher(None, self.last, selected_text).ratio()

    def begin(self, txt, conf, ratio):
        assert ratio >= 0.85
        if conf > self.confidence:
            self.last = txt
            self.confidence = conf

    def set_begin(self, st):
        self.start = st
        self.st_str = seconds_to_timestamp(st)

    def set_end(self, ed):
        if self.last != "" and ed - self.start >= 0.3:
            self.f.write(f"{self.index}\n")
            self.f.write(f"{self.st_str} --> {seconds_to_timestamp(ed-0.001)}\n")
            self.f.write(f"{self.last}\n\n")
            self.index += 1
        self.confidence = 0

    def __del__(self):
        if self.last != "" and self.finish - self.start >= 0.3:
            self.f.write(f"{self.index}\n")
            self.f.write(f"{self.st_str} --> {seconds_to_timestamp(self.finish)}\n")
            self.f.write(f"{self.last}\n\n")
        self.f.close()
        print("Subtitles saved successfully")
