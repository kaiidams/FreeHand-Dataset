# Copyright 2019 Katsuya Iida. All rights reserved.
# See LICENSE file in the project root for full license information.

import bpy
import os
import random
import math
import numpy as np


def randomize_pose():
    o = bpy.data.objects['Hand']
    prev_angle = 0.0
    for i in range(1, 6):
        bone = o.pose.bones['finger{}-1.R'.format(i)]
        if i == 5:
            angle = prev_angle
        else:
            angle = random.uniform(-60, 60) * math.pi / 180
            if i >= 3 and angle < prev_angle:
                angle = prev_angle
            elif angle < 0.0:
                angle = 0.0
            elif angle > 40 * math.pi / 180:
                angle = 40 * math.pi / 180
        bone.rotation_quaternion.x = angle
        prev_angle = angle


def render_once(index):
    randomize_pose()
    return
    scene = bpy.data.scenes['Scene']
    camera_object = bpy.data.objects['Camera']
    
    elevation_angle = random.uniform(-30, 90) * math.pi / 180
    azmith_angle = random.uniform(0, 360) * math.pi / 180
    yaw_angle = random.uniform(0, 360) * math.pi / 180
    camera_distance = 1.0
    
    print([x for x in dir(camera_object) if 'rot' in x])
    print(camera_object.rotation_euler)
    
    camera_object.rotation_euler.x = - elevation_angle + math.pi / 2
    camera_object.rotation_euler.y = 0 #yaw_angle
    camera_object.rotation_euler.z = azmith_angle + math.pi / 2

    camera_pos = (
        camera_distance * math.cos(azmith_angle) * math.cos(elevation_angle),
        camera_distance * math.sin(azmith_angle) * math.cos(elevation_angle),
        camera_distance * math.sin(elevation_angle)
        )
    camera_object.location.x = camera_pos[0]
    camera_object.location.y = camera_pos[1]
    camera_object.location.z = camera_pos[2] + 0.07
    
    fname = '{0:05d}.png'.format(index)
    print(fname)
    bpy.context.scene.render.filepath = os.path.join(os.getcwd(), 'images', fname)
    bpy.ops.render.render(write_still=True)
    
    
if __name__ == '__main__':
    bpy.ops.object.mode_set(mode='POSE')
    for i in range(10):
        render_once(i)