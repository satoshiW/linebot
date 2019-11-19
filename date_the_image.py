from PIL import Image
from PIL.ExifTags import TAGS

def date_the_image(src: str, desc: str) -> None:
    im = Image.open(src)
    im.save(desc)
    
    try:
    	exif = im._getexif()
    except AttributeError:
    	return {}
    	
    exif_table = {}
    for tag_id, value in exif.items():
    	tag = TAGS.get(tag_id, tag_id)
    	exif_table[tag] = value

    return exif_table.get("DateTimeOriginal")