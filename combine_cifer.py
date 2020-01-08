# Copyright 2019 Katsuya Iida. All rights reserved.
# See LICENSE file in the project root for full license information.

from PIL import Image, ImageDraw, ImageColor
import os
from math import sqrt
import random
import numpy as np
import pickle
import json


def read_cifer(block):
    if block == 6:
        filename = 'test_batch'
    else:
        filename = 'data_batch_{}'.format(block)
    with open('cifar-10-batches-py/' + filename, 'rb') as f:
        return pickle.load(f, encoding='bytes')


def write_freehand_data(block, data, output_dir):
    """the data is for test when block % 6 == 0"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if block == 6:
        filename = 'test_batch'
    elif block % 6 == 0:
        filename = 'test_batch_{}'.format(block // 6)
    else:
        filename = 'data_batch_{}'.format(block - block // 6)
    with open(os.path.join(output_dir, filename), 'wb') as f:
        return pickle.dump(data, f)


def read_hand_annotations(hand_block):
    annotations = []
    with open('data/annotations/{:02d}.json'.format(hand_block)) as f:
        for line in f:
            anno = json.loads(line)
            annotations.append(anno)
    return annotations


def get_crop_bbox(bbox, image_width, image_height):
    x1, y1, width, height = bbox
    x2, y2 = x1 + width, y1 + height

    # Enlarge the edge
    r = sqrt(width * height) * 0.5
    x3 = round(x1 - random.random() * r)
    y3 = round(y1 - random.random() * r)
    x4 = round(x2 + random.random() * r)
    y4 = round(y2 + random.random() * r)

    # Make the rectangle a square.
    if x4 - x3 > y4 - y3:
        d = (x4 - x3) - (y2 - y1)
        y3 = y1 - d // 2
        y4 = y2 + d - d // 2
    else:
        d = (y4 - y3) - (x2 - x1)
        x3 = x1 - d // 2
        x4 = x2 + d - d // 2
        
    if x3 < 0:
        y3 += x3
        x3 = 0
    if y3 < 0:
        x3 += y3
        y3 = 0
        
    return x3, y3, x4, y4


def array_to_image(arr):
    return Image.fromarray(arr.reshape((3, 32, 32)).transpose((1, 2, 0)))


def image_to_array(im):
    return np.asarray(im).astype(np.uint8).transpose((2, 0, 1)).reshape((-1,))


def make_image(cifer_data, cifer_index, annotations, hand_block, hand_index, transpose_method=None):
    im = array_to_image(cifer_data[b'data'][cifer_index]).convert(mode='RGBA')
    anno = annotations[hand_index]
    hand_filepath = os.path.join('data', 'images', '{:02d}'.format(hand_block), anno['file_name'])
    handim = Image.open(hand_filepath)
    bbox = get_crop_bbox(anno['bbox'], handim.width, handim.height)
    handim = handim.crop(bbox)
    handim = handim.resize((im.width, im.height), Image.BILINEAR)
    if transpose_method is not None:
        handim = handim.transpose(transpose_method)
    im.alpha_composite(handim)
    im = im.convert('RGB')
    return image_to_array(im)


def combine_cifer_block(cifer_data, cifer_block, hand_block_start, num_hand_blocks_per_cifer_block, num_hand_indices_per_block, transpose_method=None):
    labels = []
    for i in range(num_hand_blocks_per_cifer_block):
        hand_block = hand_block_start + i
        print('cifer_block={}, hand_block={}'.format(cifer_block, hand_block))
        annotations = read_hand_annotations(hand_block)
        for hand_index in range(num_hand_indices_per_block):
            cifer_index = i * num_hand_indices_per_block + hand_index
            arr = make_image(cifer_data, cifer_index, annotations, hand_block, hand_index, transpose_method)
            cifer_data[b'data'][cifer_index] = arr
            anno = annotations[hand_index]
            labels.append(anno['pose'])
    labels = np.array(labels, dtype=np.float)
    cifer_data[b'labels'] = labels
    cifer_data[b'filenames'] = []


def write_readme(output_dir):
    s = '<meta HTTP-EQUIV="REFRESH" content="0; url=https://github.com/kaiidams/FreeHand-Dataset">'
    with open(os.path.join(output_dir, 'readme.html'), 'w') as f:
        f.write(s + '\n')


def main(num_cifer_blocks=6, num_hand_blocks_per_cifer_block=10, num_hand_indices_per_block=1000, output_dir='freehand-batches-py'):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(num_cifer_blocks):
        cifer_block = i + 1
        cifer_data = read_cifer(cifer_block)
        hand_block_start = i * num_hand_blocks_per_cifer_block
        combine_cifer_block(cifer_data, cifer_block, hand_block_start, num_hand_blocks_per_cifer_block, num_hand_indices_per_block)
        write_freehand_data(cifer_block, cifer_data, output_dir)
    write_readme(output_dir)


def main2(num_cifer_blocks=6, num_hand_blocks_per_cifer_block=10, num_hand_indices_per_block=1000, extmode=1, output_dir='freehand-ext-batches-py'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if extmode == 1:
        transpose_methods = [
            Image.FLIP_LEFT_RIGHT
        ]
    elif extmode == 2:
        transpose_methods = [
            Image.FLIP_TOP_BOTTOM,
            Image.ROTATE_90, Image.ROTATE_180, Image.ROTATE_270
        ]

    for i in range(len(transpose_methods)):
        transpose_method = transpose_methods[i]
        for j in range(num_cifer_blocks):
            cifer_block = j + 1
            out_cifer_block = (i + 1) * num_cifer_blocks + (j + 1)
            cifer_data = read_cifer(cifer_block)
            if cifer_block == num_cifer_blocks: # This is test set.
                hand_block_start = j * num_hand_blocks_per_cifer_block
            else:
                k = (i + 1 + j) % (num_cifer_blocks - 1)
                hand_block_start = k * num_hand_blocks_per_cifer_block
            combine_cifer_block(cifer_data, cifer_block, hand_block_start, num_hand_blocks_per_cifer_block, num_hand_indices_per_block, transpose_method)
            write_freehand_data(out_cifer_block, cifer_data, output_dir)
    write_readme(output_dir)


if __name__ == '__main__':
    #main(num_cifer_blocks=2, num_hand_blocks_per_cifer_block=1, num_hand_indices_per_block=10)
    #main(num_cifer_blocks=6, num_hand_blocks_per_cifer_block=10, num_hand_indices_per_block=1000)
    main2()
