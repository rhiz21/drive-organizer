import ffmpeg
import shutil
import os
import subprocess
import json
from datetime import datetime, timezone, timedelta
from enum import Enum

# ------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------
class Author(Enum):
    NONE = ""
    RYOSUKE = "RYO"
    SATOMI = "SAT"

class Format(Enum):
    MP4 = 0
    MOV = 1

class Controller():
    def __init__(self, file_path: str, is_delete_original: bool = False):
        if not os.path.exists(file_path):
            raise Exception(f"{file_path} not found.")

        self.original_path = file_path
        self.file_path = file_path
        self.is_delete_original = is_delete_original
        if self.file_path.lower().endswith(".mp4"):
            # process for mp4
            self.original_format = Format.MP4
            self.analyze()
        elif self.file_path.lower().endswith(".mov"):
            # process for mov
            self.original_format = Format.MOV
            self.analyze()
            self.convert_mov_to_mp4()
        else:
            raise Exception(f"Unsupprted image format: {os.path.splitext(self.file_path)[1]}.")
        
        # if self.model in ["iPhone 12", "iPhone 15", "iPhone SE (3rd generation)"]:
        #     self.author = Author.SATOMI
        # elif self.model in ["Pixel 8a"]:
        #     self.author = Author.RYOSUKE
        # else:
        #     print(f"Unkown camera model: {self.model}.")
        #     self.author = Author.NONE

        self.replace_file_name()
    
    def get_file_name(self):
        return os.path.basename(self.file_path)

    def analyze(self):
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_entries", "format_tags:stream_tags", self.file_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info = json.loads(result.stdout)
        
        format_tags = info.get("format", {}).get("tags", {})
        stream_tags = info.get("streams", [{}])[0].get("tags", {})

        timestamp_str = format_tags.get("creation_time") or stream_tags.get("creation_time")
        if timestamp_str:
            ts = timestamp_str.replace("Z", "+00:00")
            self.timestamp = datetime.fromisoformat(ts)
            jst = timezone(timedelta(hours=9))
            self.timestamp = self.timestamp.astimezone(jst)
        
        self.make = format_tags.get("com.apple.quicktime.make") or format_tags.get("make")
        self.model = format_tags.get("com.apple.quicktime.model") or format_tags.get("model")
        if not self.model:
            for key, value in format_tags.items():
                if "model" in key.lower():
                    self.model = value
                    break

    def convert_mov_to_mp4(self):
        output = self.file_path.replace(".MOV", ".mp4")
        (
            ffmpeg
            .input(self.file_path)
            .output(
                output, 
                vcodec="libx264",
                pix_fmt="yuv420p",
                crf=23,
                preset="fast",
                acodec="aac",
                audio_bitrate="192k"
                )
            .run()
        )
        self.file_path = output

    def replace_file_name(self):
        timestamp = datetime.strftime(self.timestamp, "%Y%m%d-%H%M%S")
        new_name = f"HIZ_{timestamp}.mp4"

        new_path = os.path.join(os.path.dirname(self.file_path), new_name)
        if self.is_delete_original:
            os.rename(self.file_path, new_path)
            if os.path.exists(self.original_path):
                os.remove(self.original_path)
        elif self.original_format == Format.MOV:
            os.rename(self.file_path, new_path)
        else:
            shutil.copy2(self.file_path, new_path)
        
        self.file_path = new_path

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
if __name__ == "__main__":
    mov = Controller("IMG_0170.MOV", True)
    mp4 = Controller("PXL_20250802_124843176.mp4")
    print("hey")