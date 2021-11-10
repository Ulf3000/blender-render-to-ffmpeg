import bpy
import time

import os
import sys
import subprocess

from tempfile import gettempdir
#------------------------------------------------------------------

startTime = time.time() # measure rendering time


# get original Settings
origRenderPath = bpy.context.scene.render.filepath
origLook = bpy.context.scene.view_settings.look # im using an ocio file to preview the real colors on my widegamut monitor , ocio is chosen in render -> color management -> look
origFileFormat = bpy.context.scene.render.image_settings.file_format

# -------------------------- set render settings for temp files ---------------------------------------

# disable ocio preview / render with normal rgb values , a lut can be easily added in post instead, 
# eevee is not good at applying lut(ocio), banding and slighly wrong colors are the result but for preview its better than nothing
bpy.context.scene.view_settings.look = 'None'

# set tempRenderPath
tempRenderPath=os.path.join(gettempdir(), 'Blender_Render_Temp')
try:
    os.makedirs(tempRenderPath)
except FileExistsError:
    pass

bpy.context.scene.render.filepath = os.path.join(tempRenderPath, 'temp') # i.e. f:\temp\Blender_Render_Temp\temp####.png

# set to png  or whatever you like!!! important set up the values for the codec beforehand i.e. png with rgba 16bit or add them to the script for full automation
bpy.context.scene.render.image_settings.file_format = "PNG"


# ------------------------- RENDER -----------------------------------------------
bpy.ops.render.opengl(animation=True) # opengl = viewport rendering ! my preferred method , for my toon stuff i dont need more than that

# ------------------------- CONVERT with ffmpeg to your favourite format (prores, cineform, nvenc ???) -------------------

# get render settings fps and framestart , we need them for ffmpeg
startFrame = bpy.context.scene.frame_start
fps = bpy.context.scene.render.fps
finalRenderPath = bpy.context.scene.render.filepath + ".mov" # filename for ffmpeg 

# !! this is for windows ! in inux the syntax is slightly different !
# cineform codec with preset filmscan1 (filmscan2 is about the same data rate as prores 4444)  rgba 12bit  ; -y means overwright file
cmdParameters=f'ffmpeg -framerate {fps} -start_number {startFrame} -i {tempRenderPath}\\temp%04d.png -c:v cfhd -quality film1 -pix_fmt gbrap12le -map v:0 -y "{finalRenderPath}"'
# apple prores 4444 with 16 bit alpha
#cmdParameters=f'ffmpeg -framerate {fps} -start_number {startFrame} -i {tempRenderPath}\\temp%04d.png -c:v prores_ks -pix_fmt yuva444p10le -alpha_bits 16 -profile:v 4444 -map v:0 -y "{finalRenderPath}"'
# in theory it should be possible to call any codec or other tools like adobe media encoder from here.

#print(cmdParameters)
os.system(cmdParameters)

# ------------------------- delete files in the temp folder ----------------------

for file in os.scandir(tempRenderPath):
    os.remove(file.path)

# ------------------------- restore original settings after render ---------------
bpy.context.scene.view_settings.look = origLook
bpy.context.scene.render.filepath = origRenderPath
bpy.context.scene.render.image_settings.file_format = origFileFormat


#print render time to console
executionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(executionTime))