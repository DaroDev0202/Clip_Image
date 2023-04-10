from PIL import Image
import piexif

output_path = '1.jpg'
ctime = '2023: 03: 15 05: 11: 51'
with Image.open(output_path) as image:
    exif_dict = piexif.load(output_path)
    print(exif_dict)
    # exif_dict['Exit'][piexif.ImageIFD.DateTime] = ctime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = ctime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = ctime
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, output_path)