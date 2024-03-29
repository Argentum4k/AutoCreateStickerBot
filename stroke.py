import cv2
import numpy as np
from PIL import Image
from pathlib import Path


def change_matrix(input_mat, stroke_size):
    stroke_size = stroke_size - 1
    mat = np.ones(input_mat.shape)
    check_size = stroke_size + 1.0
    mat[input_mat > check_size] = 0
    border = (input_mat > stroke_size) & (input_mat <= check_size)
    mat[border] = 1.0 - (input_mat[border] - stroke_size)
    return mat


def cv2pil(cv_img):
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGRA2RGBA)
    pil_img = Image.fromarray(cv_img.astype("uint8"))
    return pil_img


def stroke(filename: Path, stroke_size=5, color=(255, 255, 255), threshold=0):
    print('in stroke: ', 'filename ',filename, 'stroke_size',stroke_size, 'color',color, 'threshold', threshold)
    img = np.array(Image.open(filename)) 
    if img.shape[2] != 4:
        print('не найден слой прозрачности, как рамку искать то')
        return
    h, w, _ = img.shape
    padding = stroke_size + 50
    alpha = img[:, :, 3]
    # rgb_img = img[:, :, 0:3]
    rgb_img = img[:, :, 2::-1]  # почемуто инверсия была..

    bigger_img = cv2.copyMakeBorder(rgb_img, padding, padding, padding, padding,
                                    cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    alpha = cv2.copyMakeBorder(
        alpha, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=0)
    bigger_img = cv2.merge((bigger_img, alpha))
    h, w, _ = bigger_img.shape

    _, alpha_without_shadow = cv2.threshold(
        alpha, threshold, 255, cv2.THRESH_BINARY)  # threshold=0 in photoshop
    alpha_without_shadow = 255 - alpha_without_shadow
    # dist l1 : L1 , dist l2 : l2
    dist = cv2.distanceTransform(
        alpha_without_shadow, cv2.DIST_L2, cv2.DIST_MASK_3)
    stroked = change_matrix(dist, stroke_size)
    stroke_alpha = (stroked * 255).astype(np.uint8)

    stroke_b = np.full((h, w), color[2], np.uint8)
    stroke_g = np.full((h, w), color[1], np.uint8)
    stroke_r = np.full((h, w), color[0], np.uint8)

    stroke = cv2.merge((stroke_b, stroke_g, stroke_r, stroke_alpha))
    stroke = cv2pil(stroke)
    bigger_img = cv2pil(bigger_img)
    result = Image.alpha_composite(stroke, bigger_img)
    # result.show()
    outf = filename.parent/'stroke'
    if not outf.exists():
        outf.mkdir()
    result.save(outf/filename.name)
    return outf/filename.name


if __name__ == '__main__':
    # out_folder_api = Path.cwd()/'images/output_api_1'
    inp_file = input('Введите имя файла: ')
    if inp_file[0] == inp_file[-1] == '"':
        inp_file = inp_file[1:-1]
    p = Path(inp_file)
    if p.is_file():
        print('результат: ', stroke(p, 5, threshold=3))
    else:
        print('не похоже на правильный путь к файлу: ', p.absolute())