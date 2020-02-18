import argparse
import pyrealsense2 as rs
import yaml
import os.path
import os, sys, inspect, math
import numpy as np
import cv2

sys.path.append('../')
from utils import prompt

"""
Example usage:
    python3 extract_data_realsense.py 20200206_162018.bag 10

    to get all possible Frames:
    python3 extract_data_realsense.py filename.bag 1

the --length argument is not always working as expected
"""

RS_CONFIG_FILE = os.path.dirname(__file__) + '../raw_data/realsense/config.yml'
FILES_DIR = os.path.dirname(__file__) + '../raw_data/realsense/files/'

DEPTH_DIR = ''
IMAGE_DIR = ''
CLOUD_DIR = ''
CALIB_FILE = ''


def read_config():
    """Read camera config from yaml file."""
    with open(RS_CONFIG_FILE , 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
    return cfg

def get_file_count():
    """Get file count of extracted frames."""
    files = os.listdir(CLOUD_DIR)
    return(len(files))

def count_frames():
    """Count the number of frames resulting from camera FPS and extraction interval."""
    stream_cfg = read_config()
    count = args.length*stream_cfg['depth']['fps']/args.interval
    return int(math.floor(count * 1) *0.5 / 1)

def read_format(stream_cfg):
    """Read the format of the depth and color stream."""
    if stream_cfg['depth']['format'] == 'z16':
        depth_format = rs.format.z16
    if stream_cfg['color']['format'] == 'rgb8':
        color_format = rs.format.rgb8
    return depth_format, color_format

def make_directories():
    """Make directories for output."""
    global DEPTH_DIR, IMAGE_DIR, CLOUD_DIR

    if not os.path.exists('data/depth'):
        os.makedirs('data/depth')
    DEPTH_DIR = 'data/depth/'
    if not os.path.exists('data/image'):
        os.makedirs('data/image')
    IMAGE_DIR = 'data/image/'
    if not os.path.exists('data/cloud'):
        os.makedirs('data/cloud')
    CLOUD_DIR = 'data/cloud/'

def initialize_device(file: str):
    """Initialize camera and start the stream from a .bag file."""
    stream_cfg = read_config()
    depth_format, color_format = read_format(stream_cfg)
    config = rs.config()
    rs.config.enable_device_from_file(config, FILES_DIR + file, repeat_playback=False)
    pipeline = rs.pipeline()
    config.enable_stream(rs.stream.depth, stream_cfg['depth']['width'],stream_cfg['depth']['height'], depth_format, stream_cfg['depth']['fps'])
    config.enable_stream(rs.stream.color, stream_cfg['color']['width'],stream_cfg['color']['height'], color_format, stream_cfg['color']['fps'])
    pipeline.start(config)
    return pipeline

def write_calib(intrin, extrin):
    """Write the intrinsic and extrinsic parameters in a yaml file."""
    extrin = np.asarray(extrin.rotation)
    calib = [{'intrin': [intrin.fx, 0, intrin.ppx, 0, intrin.fy, intrin.ppy, 0, 0, 1]},
        {'extrin': [float(extrin[0]), float(extrin[1]), float(extrin[2]), float(extrin[3]), float(extrin[4]), 
        float(extrin[5]), float(extrin[6]), float(extrin[7]), float(extrin[8])]}]
    with open(CALIB_FILE, 'w') as file:
        yaml.dump(calib, file)
    return

def extract_data(pl):
    """Extract depth maps, color images and point clouds from recording

    Parameters:
    pipeline : Pipeline stream from recording
   """
    global CALIB_FILE

    pipeline = pl
    try:
        #get file count to properly continue extracting files if there are extracted files from previous .bag file
        i = get_file_count() + 1
        j = 1
        while True:
            for x in range(args.interval):
                pipeline.wait_for_frames()
            
            frames = pipeline.wait_for_frames()

            #stream alignment
            align = rs.align(rs.stream.color)
            frames = align.process(frames)

            #get depth and color frames
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            #get intrinsics & extrinsics only once for color camera module
            if not os.path.isfile('data/calib.yml'):
                print('Writing calib.yml')
                CALIB_FILE = 'data/calib.yml'
                intrin = color_frame.profile.as_video_stream_profile().intrinsics
                extrin = color_frame.profile.get_extrinsics_to(color_frame.profile)
                write_calib(intrin, extrin)

            #instatiate pointcloud
            pc = rs.pointcloud()
            points = rs.points()

            #transform to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            #get and save point clouds in .ply format
            pc.map_to(color_frame)
            points = pc.calculate(depth_frame)
            print("Extracting frame:", i)
            points.export_to_ply(CLOUD_DIR + str(i).zfill(4) + '.ply', color_frame)

            #save image and depth map
            cv2.imwrite(DEPTH_DIR + str(i).zfill(4) + ".png", depth_image)
            cv2.imwrite(IMAGE_DIR + str(i).zfill(4) + ".jpg", cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR))

            i += 1
            j += 1
    except (RuntimeError):
        print('End of recording. Extracted frames: ' + str(j-1))
    finally:
        pass


def main():
    """First check if video length is provided. Then perform file extraction"""
    if args.length is not None:
        frames = count_frames()
        answer = prompt.main(str(frames) + ' frames will be approximately extracted. Continue (y/n)?')
        if answer == False:
            sys.exit()
        else: pass
    else: pass
    make_directories()
    pipeline = initialize_device(file = args.file)
    extract_data(pipeline)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()  
    parser.add_argument("file", type=str, help=".Bag file to read")
    parser.add_argument("interval", type=int, help="How many frames to save: lower = more data / higher = less data")
    parser.add_argument("-l", "--length", type=int, help="Length of the recording (in Seconds)")
    args = parser.parse_args()
    
    main()