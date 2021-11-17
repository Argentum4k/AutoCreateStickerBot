from PIL import Image, ImageFilter, ImageDraw
from pathlib import Path

def mystroke(filename: Path, size: int, color: str = 'black'):
    outf = filename.parent/'mystroke'
    if not outf.exists():
        outf.mkdir()
    img = Image.open(filename)
    X, Y = img.size
    edge = img.filter(ImageFilter.FIND_EDGES).load()
    stroke = Image.new(img.mode, img.size, (0,0,0,0))
    draw = ImageDraw.Draw(stroke)
    for x in range(X):
        for y in range(Y):
            if edge[x,y][3] > 0:
                draw.ellipse((x-size,y-size,x+size,y+size),fill=color)
    stroke.paste(img, (0, 0), img )
    # stroke.show()
    stroke.save(outf/filename.name)

if __name__ == '__main__':
    out_folder_api = Path.cwd()/'images/output_api_1'
    for img in out_folder_api.iterdir():
        if img.is_file(): mystroke(img, 5)
