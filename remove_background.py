# Requires "requests" to be installed (see python-requests.org)
# from os import mkdir
import requests
from pathlib import Path
import numpy as np
import io
from PIL import Image, ImageFile, ImageFilter  # ImageFilter.CONTOUR
from stroke import stroke

ImageFile.LOAD_TRUNCATED_IMAGES = True      # fix the OSError: image file is truncated (5 bytes not processed)

def cut_empty_parts_and_fit_to_512px(filename: Path):
    """ только для png или др. с прозрачностью """
    outf = filename.parent/'cut'
    if not outf.exists(): outf.mkdir()
    img = Image.open(filename)
    # np_img = np.array(img)
    # if np_img.shape[2] != 4:
    #     print('не найден слой прозрачности, как резать то')
    #     return
    # np_img = np_img[np.any(np_img[:,:,3] > 0, axis=1)]
    # np_img = np_img[:,np.any(np_img[:,:,3] > 0,axis=0)]
    img = img.crop(img.getbbox()) # Get the bounding box
    #####################

    # img = Image.fromarray(np_img)
    x, y = img.size
    scale = 512 / max(x, y)
    img = img.resize((round(x*scale), round(y*scale)), Image.LANCZOS) 
    img.save(outf/filename.name)

def remove_bg_api(filename: Path, out_folder: Path = None):
    """ tested """
    if not out_folder:
        out_folder = filename.parent / 'api'
    if not out_folder.exists():
        out_folder.mkdir()
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': open(filename, 'rb')},
        data={'size': 'auto'},
        headers={'X-Api-Key': 'hGGHcrudSndzXKmdzNFsJS8u'},
    )
    if response.status_code == requests.codes.ok:
        name = filename.stem + '.png'
        with open(out_folder/name, 'wb') as out:
            out.write(response.content)
    else:
        print("Error:", response.status_code, response.text)

def remove_bg_local(filename: Path, out_folder: Path = None, alpha=0, model='u2net'):
    """ default alpha params are poor, default model is the best """
    from rembg.bg import remove as rem_bg
    if not out_folder:
        out_folder = filename.parent / 'local'
    if not out_folder.exists():
        out_folder.mkdir()
    f = np.fromfile(filename)
    result = rem_bg(f,alpha_matting=alpha, model_name=model)    
    name = out_folder/(filename.stem + '.png')
    img = Image.open(io.BytesIO(result)).convert("RGBA")
    img.save(out_folder/name)

in_folder = Path(r'C:\Users\Alex\Pictures\стикеры\lionborn')

# for img in in_folder.iterdir():
#     if img.is_file():
#         remove_bg_api(img)
#         remove_bg_local(img)
    
no_bg = [*(in_folder/'api').iterdir(), *(in_folder/'local').iterdir()]

for img in no_bg:
    if img.is_file():
        stroke(img)     # на 1 файл в итоге навалило какойто фигни

stroked = [*(in_folder/'api'/'stroke').iterdir(), *(in_folder/'local'/'stroke').iterdir()]
for img in stroked:
    if img.is_file():
        cut_empty_parts_and_fit_to_512px(img)



# out_folder_local_u2netp = Path.cwd()/'images/output_local_u2netp'
# for img in in_folder.iterdir():
#     remove_bg_local(img, out_folder_local_u2netp, model="u2netp")

# out_folder_local_humanseg = Path.cwd()/'images/output_local_u2net_human_seg'
# for img in in_folder.iterdir():
#     remove_bg_local(img, out_folder_local_humanseg, model="u2net_human_seg")

# out_folder_local = Path.cwd()/'images/output_local'
# for img in out_folder_api.iterdir():
#     if img.is_file():cut_empty_parts_and_fit_to_512px(img)

