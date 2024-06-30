import matplotlib.pyplot as plt
import PIL
from PIL import Image
import math
import cv2
import os
import moviepy.editor as mv

API = '5854451716:AAF6h7NpNFjjb3OREkrryXsu41VhOBmZE5Q'

import telebot
import os
from telebot import types

from pydub import AudioSegment
import time

import sys
import shutil


def resize_canvas(image, canvas_width=500, canvas_height=500):
    """
    Resize the canvas of old_image_path.

    Store the new image in new_image_path. Center the image on the new canvas.

    Parameters
    ----------
    old_image_path : str
    new_image_path : str
    canvas_width : int
    canvas_height : int
    """
    im = image
    old_width, old_height = im.size

    # Center the image
    x1 = int(math.floor((canvas_width - old_width) / 2))
    y1 = int(math.floor((canvas_height - old_height) / 2))

    mode = im.mode
    if len(mode) == 1:  # L, 1
        new_background = (0)
    if len(mode) == 3:  # RGB
        new_background = (0, 0, 0)
    if len(mode) == 4:  # RGBA, CMYK
        new_background = (0, 0, 0, 0)

    newImage = Image.new(mode, (canvas_width, canvas_height), new_background)
    newImage.paste(im, (x1, y1, x1 + old_width, y1 + old_height))
    
    return newImage


def main(*args):

    #AudioSegment.converter = "C:/Program Files/ffmpeg/bin"

    bot = telebot.TeleBot(API)

    user_id = args[0][0]

    path = f'./{user_id}'

    bot.send_message(user_id, 'Making video...')

    #creating video
    print('Creating video')

    if ('gif' not in os.listdir(path)):
        os.mkdir(path + '/gif')

    print('Creating image')

    n = 2

    image1 = PIL.Image.open('./Assets/Images/Disk.png', formats=['png']).resize((int(1000/n), int(1000/n)))
    image2 = PIL.Image.open(path + '/image.png').resize((int(490/n), int(490/n)))
    image3 = PIL.Image.open('./Assets/Images/Pin.png').resize((int(1000/n), int(1000/n)))

    image2 = resize_canvas(image2, canvas_width=int(1000/n), canvas_height=int(1000/n))
    image2.paste(image1, (0,0), image1)

    images = [image2.rotate(-3.6*i) for i in range(100)]

    for i in range(len(images)):
        images[i].paste(image3, (0,0), image3)
        images[i].save(path + f'/gif/img{i}.jpeg')

    print('Making video')

    image_folder = path + '/gif'
    video_name = 'video.mp4'

    images = [img for img in sorted(os.listdir(image_folder), key=lambda x: int(x.split('.')[0][3:])) if img.endswith(".jpeg")]*12
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(path + '/' + video_name, 0, 20, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()

    bot.send_message(user_id, 'Done! Now making audio...')


    #creating audio
    print('Creating audio')

    try:
        audio = AudioSegment.from_file(path + '/audio.mp3', 'mp3')
    except:
        audio = AudioSegment.from_file(path + '/audio.mp3', format='mp4')
    audio = audio[:60*1000]

    effect = AudioSegment.from_file('./Assets/Sounds/Vinyl.mp3')
    effect = effect[:60*1000] - 5

    audio = audio.overlay(effect)   

    audio = audio.fade(to_gain=-100, start=53000, end=59500)
    audio.export(path + '/audio_cut.mp3', format='mp3')

    print('Creating clip')
    bot.send_message(user_id, 'Almost there! Glueing it all together...')

    clip = mv.VideoFileClip(path + '/video.mp4')
    audio = mv.AudioFileClip(path + '/audio_cut.mp3')
    final = clip.set_audio(audio)
    final.write_videofile(path + '/final.mp4')

    audio.close()
    clip.close()
    final.close()
    

    print('Sending VN')

    with open(path + '/final.mp4', 'rb') as vn:
        bot.send_message(user_id, 'Catch!')
        bot.send_video_note(user_id, data=vn, duration=60)

    # with open(f'{user_id}.txt', 'a') as f:
    #     f.write(time.time())

    # try:
    #     shutil.rmtree(path)
    # except Exception as e:
    #     print(e)
    #     pass

    return

if __name__ == '__main__':
    print(sys.argv[1:])
    main(sys.argv[1:])