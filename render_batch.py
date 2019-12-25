# Copyright 2019 Katsuya Iida. All rights reserved.
# See LICENSE file in the project root for full license information.

import bpy
import mathutils

import os
import random
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
    for i in range(1, 6):
        ob = bpy.data.objects['Light{}'.format(i)]
        print(ob.data.energy)
        if random.random() < 0.3:
            ob.data.energy = 0.0
        else:
            ob.data.energy = random.random() * 40
    

def render_scene(index):
    scene = bpy.data.scenes['Scene']
    fname = '{0:05d}.png'.format(index)
    bpy.context.scene.render.filepath = os.path.join(os.getcwd(), 'images', fname)
    bpy.ops.render.render(write_still=True)


def process_once(index):
    print('Processing scene {}'.format(index))
    angles = random_angles()
    apply_handpose(angles)
    apply_camerapose(angles)
    apply_lights()
    render_scene(index)
    
    
def main():
    setup()
    for i in range(10):
        process_once(i)

        
if __name__ == '__main__':
    main()