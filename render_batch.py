# Copyright 2019 Katsuya Iida. All rights reserved.
# See LICENSE file in the project root for full license information.

import bpy
import mathutils

import sys
import os
import random
import json
from math import pi, cos, sin
import numpy as np


BONE_NAMES = (
    'Camera',  # roll
    'Camera',  # elevation
    'Camera',  # azmith
    'wrist.R', # hori
    'wrist.R', # vert
    'finger1.R',
    'finger2-1.R',
    'finger3-1.R',
    'finger4-1.R',
    'finger5-1.R',
    )
    
BONE_MIN = np.array([
    -30,
    0,
    0,
    -10,
    -30,
    -5,
    -5,
    -5,
    -5,    
    -5
    ])

BONE_RAND_RANGE = np.array([
    90,
    360,
    360,
    10,
    30,
    60,
    60,
    60,
    60,    
    60
    ]) - BONE_MIN

BONE_MAX = np.array([
    90,
    360,
    360,
    10,
    30,
    40,
    40,
    40,
    40,    
    40
    ])
    

BBOX_BONE_NAMES = (['wrist.R'] + 
    ['finger{}-{}.R'.format(i, j)
     for i in range(1, 6)
     for j in (1, 3)
    ])
    
    
def setup():
    '''Changes to the POSE mode.'''
    view_layer = bpy.context.view_layer
    ob = bpy.data.objects['Hand']
    ob.select_set(True)
    view_layer.objects.active = ob
    # bpy.context.scene.objects.active = ob # 2.7x
    bpy.ops.object.mode_set(mode='POSE')
    
    
def random_angles():
    '''Returns random angles as a numpy array.'''
    angles = np.random.random(len(BONE_NAMES)) * BONE_RAND_RANGE + BONE_MIN
    for i in range(6, 9):
        if random.random() < 0.3:
            angles[i] = 0.0
    if random.random() < 0.8:
        # Outer fingers are easier to be flexed. 
        angles[7] = max(angles[6], angles[7])
        angles[8] = max(angles[7], angles[8])
    angles[9] = angles[8] # ring and baby move together.
    angles = np.minimum(angles, BONE_MAX)
    return angles


def apply_handpose(angles):
    '''Applies angles to the hand bones.'''
    ob = bpy.data.objects['Hand']
    for i in range(3, 10):
        bonename = BONE_NAMES[i]
        bone = ob.pose.bones[bonename]
        angle = angles[i]
        if i == 4: # vert
            bone.rotation_quaternion.z = angle * pi / 180
        else:
            bone.rotation_quaternion.x = angle * pi / 180


def apply_camerapose(angles):
    '''Rotate the camera bone to move the camera.'''
    ob = bpy.data.objects['Hand']
    bone = ob.pose.bones['camera']
    bone.rotation_euler.x = angles[0] * pi / 180
    bone.rotation_euler.y = angles[1] * pi / 180
    bone.rotation_euler.z = angles[2] * pi / 180
    

def apply_lights():
    """Changes lights strength."""
    for i in range(1, 6):
        ob = bpy.data.objects['Light{}'.format(i)]
        if random.random() < 0.3:
            ob.data.energy = 0.0
        else:
            ob.data.energy = random.random() * 40.0


def get_render_pos(mat, pos):
    p = mat @ pos
    vx = p.x / -p.z * 3.888
    vy = p.y / -p.z * 3.888
    return vx, vy


def get_bounding_box(image_width, image_height):
    """Returns the bounding box of the hand in the image coordinate."""
    min_vx, min_vy, max_vx, max_vy = 1.0, 1.0, -1.0, -1.0
    ob = bpy.data.objects['Camera']
    mat = ob.matrix_world.normalized().inverted()
    ob = bpy.data.objects['Hand']

    for bonename in BBOX_BONE_NAMES:
        bone = ob.pose.bones[bonename]
        for pt in (bone.head, bone.tail):
            vx, vy = get_render_pos(mat, pt)
            if min_vx > vx:
                min_vx = vx
            if max_vx < vx:
                max_vx = vx
            if min_vy > vy:
                min_vy = vy
            if max_vy < vy:
                max_vy = vy

    # Translate to the image coordinate.
    min_x = round((min_vx + 0.5) * image_width)
    min_y = round((min_vy + 0.5) * image_height)
    max_x = round((max_vx + 0.5) * image_width)
    max_y = round((max_vy + 0.5) * image_height)
    return min_x, min_y, max_x - min_x, max_y - min_y
        

def render_scene(dirpath, filename):
    bpy.context.scene.render.filepath = os.path.join(dirpath, filename)
    bpy.ops.render.render(write_still=True)


def process_once(dirpath, filename, annotations):
    angles = random_angles()
    apply_handpose(angles)
    apply_camerapose(angles)
    apply_lights()
    render_scene(dirpath, filename)
    #dg = bpy.context.evaluated_depsgraph_get()
    #dg.update() 
    #scene = bpy.data.scenes['Scene']
    #scene.update() # 2.7x
    image_width = bpy.context.scene.render.resolution_x
    image_height = bpy.context.scene.render.resolution_y
    bbox = get_bounding_box(image_width, image_height)
    anno = {
        'file_name': filename,
        'pose': list(angles),
        'bbox': bbox
        }
    annotations.append(anno)


def write_annotations(annotations, dirpath, filename):
    with open(os.path.join(dirpath, filename), 'w') as f:
        for anno in annotations:
            line = json.dumps(anno)
            f.write(line + '\n')
        
        
def main(mode='test'):
    setup()

    if mode == 'test':
        num_blocks = 2
        num_images_per_block = 10
    else:
        num_blocks = 100
        num_images_per_block = 1000
        
    annotations_dirpath = os.path.join(os.getcwd(), 'data', 'annotations')
    if not os.path.exists(annotations_dirpath):
        os.makedirs(annotations_dirpath)

    for i in range(num_blocks):
        annotations = []

        image_dirpath = os.path.join(os.getcwd(), 'data', 'images', '{:04d}'.format(i))
        if not os.path.exists(image_dirpath):
            os.makedirs(image_dirpath)

        for j in range(num_images_per_block):
            image_filename = '{:04d}-{:04d}.png'.format(i, j)
            process_once(image_dirpath, image_filename, annotations)

        annotations_filename = '{:04d}.json'.format(i)
        write_annotations(annotations, annotations_dirpath, annotations_filename)

        
if __name__ == '__main__':
    mode = 'full' if '--full' in sys.argv[1:] else 'test'
    print('Mode is {}'.format(mode))
    main(mode=mode)
