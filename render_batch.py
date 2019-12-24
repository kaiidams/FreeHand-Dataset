# Copyright 2019 Katsuya Iida. All rights reserved.
# See LICENSE file in the project root for full license information.

import bpy
import os
import random
from math import pi, cos, sin
import numpy as np


BONE_NAMES = (
    'Camera',
    'Camera',
    'Camera',
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
    -10,
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
    -10,
    30,
    40,
    40,
    40,
    40,    
    40
    ])
    

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
    o = bpy.data.objects['Hand']
    for i in range(5, 10):
        bonename = BONE_NAMES[i]
        bone = o.pose.bones[bonename]
        angle = angles[i]
        bone.rotation_quaternion.x = angle * pi / 180


def render_once(index):
    
    angles = random_angles()
    print(angles)
    apply_handpose(angles)

    scene = bpy.data.scenes['Scene']
    camera_object = bpy.data.objects['Camera']
    
    elevation_angle = random.uniform(-30, 90) * pi / 180
    azmith_angle = random.uniform(0, 360) * pi / 180
    yaw_angle = random.uniform(0, 360) * pi / 180
    camera_distance = 1.0
    
    print([x for x in dir(camera_object) if 'rot' in x])
    print(camera_object.rotation_euler)
    
    camera_object.rotation_euler.x = - elevation_angle + pi / 2
    camera_object.rotation_euler.y = 0 #yaw_angle
    camera_object.rotation_euler.z = azmith_angle + pi / 2

    camera_pos = (
        camera_distance * cos(azmith_angle) * cos(elevation_angle),
        camera_distance * sin(azmith_angle) * cos(elevation_angle),
        camera_distance * sin(elevation_angle)
        )
    camera_object.location.x = camera_pos[0]
    camera_object.location.y = camera_pos[1]
    camera_object.location.z = camera_pos[2] + 0.07
    
    fname = '{0:05d}.png'.format(index)
    print(fname)
    bpy.context.scene.render.filepath = os.path.join(os.getcwd(), 'images', fname)
    bpy.ops.render.render(write_still=True)
    
    
if __name__ == '__main__':
    view_layer = bpy.context.view_layer
    ob = bpy.data.objects['Hand']
    ob.select_set(True)
    view_layer.objects.active = ob
    # bpy.context.scene.objects.active = ob # 2.7x
    bpy.ops.object.mode_set(mode='POSE')
    for i in range(10):
        render_once(i)