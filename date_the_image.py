from PIL import Image

def date_the_image(src: str, desc: str) -> None:
    im = Image.open(src)
    im.save(desc)