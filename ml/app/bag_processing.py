from bagpy import bagreader
import pandas as pd
import cv2
import pandas as pd
import numpy as np
import os


Height, Width = 480, 640

def get_csv(request_id):
    bagfile = bagreader(f'media/{request_id}.bag')
    bagfile.message_by_topic('/device_0/sensor_0/Depth_0/image/data')
    bagfile.message_by_topic('/device_0/sensor_1/Color_0/image/data')
    os.rename(f'./media/{request_id}/device_0-sensor_0-Depth_0-image-data.csv', f'./media/{request_id}-depth.csv')
    os.rename(f'./media/{request_id}/device_0-sensor_1-Color_0-image-data.csv', f'./media/{request_id}-rgb.csv')
    os.rmdir(f'./media/{request_id}')
    bagfile.reader.close()
    os.system(f'rm media/{request_id}.bag')

def to_image_rgb(data):
    raw_string = data
    # преобразовать в байтовую строку с включенными escape-символами
    byte_string = raw_string[2:-1].encode('latin1')
    # удалить эскейп символы
    escaped_string = byte_string.decode('unicode_escape')
    # преобразовать обратно в байтовую строку без экранированных символов
    byte_string = escaped_string.encode('latin1')
    #создание массива NumPy из байтовой строки
    nparr = np.frombuffer(byte_string, np.uint8)
    # преобразовать в 3 мерный массив изображений RGB (высота x ширина x 3(R and G and B))
    rgb = nparr.reshape((Height, Width, -1))
    return rgb 

def get_rgb_video(request_id):
    rgb_df = pd.read_csv(f'media/{request_id}-rgb.csv')
    format_video_color = cv2.VideoWriter_fourcc(*'H264') # формат видео
    rgb_reader = cv2.VideoWriter(f'media/{request_id}-rgb.mp4', format_video_color, 15.0, (640, 480))

    def to_animation_rgb(rgb):
        rgb_reader.write(cv2.cvtColor(to_image_rgb(rgb), cv2.COLOR_RGB2BGR))
    
    rgb_df['data'].apply(to_animation_rgb)
    rgb_reader.release()
    print(f'[INFO]  Successfully created the {request_id}-rgb.mp4') 
    os.system(f'rm media/{request_id}-rgb.csv')

def to_image_depth(data):
    raw_string = data
    # преобразовать в байтовую строку с включенными escape-символами
    byte_string = raw_string[2:-1].encode('latin1')
    # удалить эскейп символы
    escaped_string = byte_string.decode('unicode_escape')
    # преобразовать обратно в байтовую строку без экранированных символов
    byte_string = escaped_string.encode('latin1')
    #создание массива NumPy из байтовой строки
    nparr = np.frombuffer(byte_string, np.uint16)
    # преобразовать в 3 мерный массив изображений RGB (высота x ширина x 3(R and G and B))
    depth = nparr.reshape((Height, Width, -1))
    depth = (cv2.convertScaleAbs(depth / 256)).astype(np.uint8)
    depth = cv2.cvtColor(cv2.applyColorMap(depth, cv2.COLORMAP_VIRIDIS), cv2.COLOR_BGR2RGB)
    return depth

def get_depth_video(request_id):
    depth_df = pd.read_csv(f'media/{request_id}-depth.csv')
    format_video_color = cv2.VideoWriter_fourcc(*'H264') # формат видео
    depth_reader = cv2.VideoWriter(f'media/{request_id}-depth.mp4', format_video_color, 15.0, (640, 480))

    def to_animation_depth(depth):
        depth_reader.write(cv2.cvtColor(to_image_depth(depth), cv2.COLOR_RGB2BGR))
    
    depth_df['data'].apply(to_animation_depth)
    depth_reader.release()
    print(f'[INFO]  Successfully created the media/{request_id}-depth.mp4')
    os.system(f'rm media/{request_id}-depth.csv')

def delete_videos(request_id):
    os.system(f'rm media/{request_id}-rgb.mp4')
    os.system(f'rm media/{request_id}-depth.mp4')
    os.system(f'rm media/{request_id}-pipline.mp4')
