import logging
import shutil
import image
import video
import os
import io
import line
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------------
# CONSTANT
# ------------------------------------------------------------------
LOGS_DIR = Path("/logs")
RAW_DIR = Path("/raw")
BACKUP_DIR = Path("/backup")
PHOTO_DIR = Path("/photos")
MASTER_USER_ID = "Uf78e04de8742539d8cb9630ad15ba29c"

# ------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------
def is_valid_image(file_path: Path):
    valid_extensions = {".jpg", ".jpeg", ".heic"}
    return file_path.suffix.lower() in valid_extensions

def is_valid_video(file_path: Path):
    valid_extensions = {".mp4", ".mov"}
    return file_path.suffix.lower() in valid_extensions

def process_file(target_path: Path):
    try:
        # バックアップ
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        if os.path.exists(BACKUP_DIR / target_path.name):
            logging.info(f"SKIP: File already converted. {target_path.name}")
            os.remove(target_path)
            return
        shutil.copy2(target_path, BACKUP_DIR / target_path.name)

        # コンバート
        file_path = None
        file_name = ""
        timestamp = None
        if is_valid_image(target_path):
            ic = image.Controller(str(target_path), True)
            file_path = Path(ic.file_path)
            file_name = ic.get_file_name()
            timestamp = ic.timestamp
        elif is_valid_video(target_path):
            vc = video.Controller(str(target_path), True)
            file_path = Path(vc.file_path)
            file_name = vc.get_file_name()
            timestamp = vc.timestamp
        else:
            print(f"Skipping unsupported file: {target_path}")
            return
        
        # フォルダ作成
        month_dir = PHOTO_DIR / f"{timestamp.year}年" / f"{timestamp.month:02}月"
        month_dir.mkdir(parents=True, exist_ok=True)

        # ファイル移動
        dist_file_path = month_dir / file_name
        if not dist_file_path.exists():
            shutil.move(file_path, dist_file_path)
            logging.info(f"SUCCESS: {target_path.name} moved to {dist_file_path}")
        else:
            logging.warning(f"SKIP: Destination already exist. {dist_file_path}")
    
    except Exception as e:
        logging.error(f"Failed to process {target_path}: {e}")

def process_all():
    if not RAW_DIR.exists():
        print(f"Error: {RAW_DIR} does not exist.")
        return

    for file in RAW_DIR.iterdir():
        if file.is_file():
            process_file(file)

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
if __name__ == "__main__":
    LOGS_DIR.mkdir(exist_ok=True)

    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    stream_handler.setLevel(logging.ERROR)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s\n%(message)s\n"))

    log_filename = LOGS_DIR / datetime.now().strftime("%Y-%m-%d.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),
            logging.StreamHandler(),
            stream_handler
        ]
    )

    try:
        process_all()
    finally:
        error_logs = log_stream.getvalue()
        if error_logs:
            line.push_text(MASTER_USER_ID, f"🚨 以下のエラーが発生しました:\n\n{error_logs[:300]}")
        else:
            line.push_text(MASTER_USER_ID, "✅ 本日の処理はすべて正常に終了しました。")
        
        log_stream.close()