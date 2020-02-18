import os, shutil, sys
import argparse
from natsort import natsorted
import cv2
import yaml

sys.path.append('../')
from utils import create_zip_archive

"""
Example usage:
    python3 extract_data_zed.py hd
"""

ZED_CALIB_FILE = os.path.dirname(__file__) + '../raw_data/zed/intrinsic_parameters_zed_camera.txt'
FILES_DIR = os.path.dirname(__file__) + '../raw_data/zed/files/'

DEPTH_DIR = ''
IMAGE_DIR = ''
CLOUD_DIR = ''
CALIB_FILE = ''


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

def define_image_size(resolution:str):
    if resolution == '2k':
        x = 1080
        y = 2048
    elif resolution == 'fhd':
        x = 1080
        y = 1920
    elif resolution == 'hd':
        x = 720
        y = 1280
    elif resolution == 'vga':
        x = 480
        y = 640
    else: pass

    return x, y

def extract_calib(resolution:str):
    file = open(ZED_CALIB_FILE, 'r')
    file = file.readlines()
    if resolution == '2k':
        fx = file[1][file[1].rindex('=')+1:]
        fy = file[2][file[2].rindex('=')+1:]
        cx = file[3][file[3].rindex('=')+1:]
        cy = file[4][file[4].rindex('=')+1:]
    elif resolution =='fhd':
        fx = file[32][file[32].rindex('=')+1:]
        fy = file[33][file[32].rindex('=')+1:]
        cx = file[34][file[32].rindex('=')+1:]
        cy = file[35][file[32].rindex('=')+1:]
    elif resolution =='hd':
        fx = file[48][file[48].rindex('=')+1:]
        fy = file[49][file[49].rindex('=')+1:]
        cx = file[50][file[50].rindex('=')+1:]
        cy = file[51][file[51].rindex('=')+1:]
    elif resolution =='vga':
        fx = file[64][file[64].rindex('=')+1:]
        fy = file[65][file[65].rindex('=')+1:]
        cx = file[66][file[66].rindex('=')+1:]
        cy = file[67][file[67].rindex('=')+1:]
    else: pass

    return float(fx), float(fy), float(cx), float(cy)

def write_calib(fx, fy, cx, cy):
    """Write the intrinsic and extrinsic parameters in a yaml file."""
    extrin = [1,0,0,0,1,0,0,0,1]
    calib = [{'intrin': [fx, 0, cx, 0, fy, cy, 0, 0, 1]},
        {'extrin': [float(extrin[0]), float(extrin[1]), float(extrin[2]), float(extrin[3]), float(extrin[4]), 
        float(extrin[5]), float(extrin[6]), float(extrin[7]), float(extrin[8])]}]
    with open(CALIB_FILE, 'w') as file:
        yaml.dump(calib, file)
    return


def extract_images(size_x, size_y):
    i = 1
    for filename in natsorted(os.listdir(FILES_DIR)):
        if filename.startswith('ZED_image'):
            print('Extracting image ' + str(i))
            img = cv2.imread(FILES_DIR + filename, 1)
            crop_img = img[0:0+size_x, 0:0+size_y]
            cv2.imwrite(IMAGE_DIR + str(i).zfill(4) + '.jpg',crop_img)
            i += 1
        else: pass

def extract_clouds():
    i = 1
    for filename in natsorted(os.listdir(FILES_DIR)):
        if filename.startswith('Cloud'):
            print('Extracting point cloud ' + str(i))
            shutil.copy2(FILES_DIR + filename, CLOUD_DIR + str(i).zfill(4) + '.ply')
            i += 1
        else: pass

def extract_depth():
    i = 1
    for filename in natsorted(os.listdir(FILES_DIR)):
        if filename.startswith('Depth') and filename.endswith('.png'):
            print('Extracting depth map ' + str(i))
            shutil.copy2(FILES_DIR + filename, DEPTH_DIR + str(i).zfill(4) + '.png')
            i += 1
        else: pass


def main():
    global CALIB_FILE

    make_directories()
    if not os.path.isfile('data/calib.yml'):
        print('Writing calib.yml')
        CALIB_FILE = 'data/calib.yml'
        fx, fy, cx, cy = extract_calib(args.resolution)
        write_calib(fx, fy, cx, cy)
    size_x, size_y = define_image_size(args.resolution)
    extract_images(size_x, size_y)
    extract_clouds()
    extract_depth()

    #If all data is extracted it can be zipped using this function
    if args.compress is not None:
        create_zip_archive.create_zip_archive_stage_one(args.compress)
    else: pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()  
    parser.add_argument("resolution", type=str, choices=['2k','fhd', 'hd', 'vga'],help="Resolution of recorded RGB-D frames.")
    parser.add_argument("-c", "--compress", type=str, help="Specify archive name to compress extracted files.")
    args = parser.parse_args()

    main()