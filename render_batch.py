# Copyright 2019 Katsuya Iida. All rights reserved.
# See LICENSE file in the project root for full license information.

import bpy
import os
import random
import math
import numpy as np

def render_once(index):
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
    for i in range(10):
        render_once(i)