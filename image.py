import os
import pillow_heif
import piexif
import shutil
from enum import Enum
from datetime import datetime
from PIL import Image as pil
from geopy.geocoders import Nominatim

# ------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------
class ExifNotFoundError(Exception):
    pass
    
class Author(Enum):
    NONE = ""
    RYOSUKE = "RYO"
    SATOMI = "SAT"

class Format(Enum):
    JPG = 0
    HEIC = 1

class Controller:
    def __init__(self, file_path: str, is_delete_original: bool = False):
        if not os.path.exists(file_path):
            raise Exception(f"{file_path} not found.")

        self.original_path = file_path
        self.file_path = file_path
        self.is_delete_original = is_delete_original
        if self.file_path.lower().endswith(".jpg") or self.file_path.lower().endswith(".jpeg"):
            # process for jpg
            self.original_format = Format.JPG
            self.analyze_jpeg()
        elif self.file_path.lower().endswith(".heic"):
            # process for heic
            self.original_format = Format.HEIC
            self.analyze_heic()
            self.convert_heic_to_jpeg()
        else:
            raise Exception(f"Unsupprted image format: {os.path.splitext(self.file_path)[1]}.")
        
        if self.model in ["iPhone 12", "iPhone 15", "iPhone SE (3rd generation)"]:
            self.author = Author.SATOMI
        elif self.model in ["Pixel 8a"]:
            self.author = Author.RYOSUKE
        else:
            print(f"Unkown camera model: {self.model}.")
            self.author = Author.NONE
        
        self.replace_file_name()
    
    def get_file_name(self):
        return os.path.basename(self.file_path)
    
    def analyze_heic(self):
        heif = pillow_heif.read_heif(self.file_path)
        
        exif_bytes = heif.info.get("exif")
        self.analyze_exif(exif_bytes)

    def analyze_jpeg(self):
        self.analyze_exif(self.file_path)

    def analyze_exif(self, exif_bytes):
        if not exif_bytes:
            raise Exception("Exif is none.")
        
        exif_dict = piexif.load(exif_bytes)
        exif = exif_dict.get("Exif", {})
        gps = exif_dict.get("GPS", {})
        zeroth = exif_dict.get("0th", {})

        if piexif.ExifIFD.DateTimeOriginal in exif:
            date = exif[piexif.ExifIFD.DateTimeOriginal].decode()
            self.timestamp = datetime.strptime(date, "%Y:%m:%d %H:%M:%S")
        else:
            raise ExifNotFoundError(f"Exif not found in {self.get_file_name}.")

        if gps:
            lat = self.convert_to_degree(gps[piexif.GPSIFD.GPSLatitude])
            lat_ref = gps.get(piexif.GPSIFD.GPSLatitudeRef, b'N')
            if lat_ref == b'S':
                lat = -lat

            lon = self.convert_to_degree(gps[piexif.GPSIFD.GPSLongitude])
            lon_ref = gps.get(piexif.GPSIFD.GPSLongitudeRef, b'E')
            if lon_ref == b'W':
                lon = -lon

            self.coordinates = {"lat": lat, "lon": lon}
        else:
            self.coordinates = {"lat": None, "lon": None}
        
        self.make = zeroth.get(piexif.ImageIFD.Make, b"Unknown").decode("utf-8").strip()
        self.model = zeroth.get(piexif.ImageIFD.Model, b"Unknown").decode("utf-8").strip()
        self.software = zeroth.get(piexif.ImageIFD.Software, b"Unknown").decode("utf-8").strip()
    
    def convert_heic_to_jpeg(self):
        heif = pillow_heif.read_heif(self.file_path)
        image = pil.frombytes(
            heif.mode,
            heif.size,
            heif.data
        )
        
        self.file_path = self.file_path.replace(".heic", ".jpg")
        image.save(self.file_path, "JPEG")
    
    def replace_file_name(self):
        timestamp_str = datetime.strftime(self.timestamp, "%Y%m%d-%H%M%S")
        new_name = f"HIZ_{self.author.value}_{timestamp_str}.jpg"

        new_path = os.path.join(os.path.dirname(self.file_path), new_name)
        if self.is_delete_original:
            os.rename(self.file_path, new_path)
        else:
            shutil.copy2(self.file_path, new_path)

        self.file_path = new_path

    # ----- utilities -----
    def convert_to_degree(self, value):
        d = value[0][0] / value[0][1]
        m = value[1][0] / value[1][1]
        s = value[2][0] / value[2][1]
        return d + (m / 60.0) + (s / 3600.0)
    
    def decompose_location(self):
        if not self.coordinates["lat"] or not self.coordinates["lon"]:
            return {}

        geolocator = Nominatim(user_agent="photo-organizer")
        location = geolocator.reverse((self.coordinates["lat"], self.coordinates["lon"]), language="ja")

        if not location: return {}

        address = location.raw.get("address", {})
        address_dict = {
            "country": address.get("country"),
            "prefecture": address.get("prefecture"),
            "city": address.get("city"),
            "ward": address.get("ward"),
            "suburb": address.get("suburb"),
            "postcode": address.get("postcode")
        }
        return address_dict

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
if __name__ == "__main__":
    heic = Controller("IMG_0249.HEIC")
    jpeg = Controller("PXL_20250926_053730506.jpg")