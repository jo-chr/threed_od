import os, sys
from natsort import natsorted
import open3d as o3d
import shutil
import json
import yaml
import argparse
import numpy as np

sys.path.append('../')
from utils import zipping

DATA_DIR = 'processed_data/'
CLOUD_DIR = DATA_DIR + 'cloud/'
IMAGE_DIR = DATA_DIR + 'image/'
LABEL_2D_DIR = DATA_DIR + 'label_2d/'
LABEL_3D_DIR = DATA_DIR + 'label_3d/'
CALIB_FILE = DATA_DIR + 'calib.yml'
OBJECTCLASSES_FILE = DATA_DIR + 'objectclasses.json'

DUMP_DIR = 'temp_trainval/'
DUMP_CLOUD_DIR = DUMP_DIR + 'cloud/'
DUMP_IMAGE_DIR = DUMP_DIR + 'image/'
DUMP_LABEL_DIR = DUMP_DIR + 'label/'
DUMP_CALIB_DIR = DUMP_DIR + 'calib/'
DUMP_OBJECTCLASSES_FILE = DUMP_DIR + 'objectclasses.json'

def make_directories():
    if not os.path.exists(DUMP_DIR):
        os.makedirs(DUMP_DIR)
    if not os.path.exists(DUMP_CLOUD_DIR):
        os.makedirs(DUMP_CLOUD_DIR)
    if not os.path.exists(DUMP_IMAGE_DIR):
        os.makedirs(DUMP_IMAGE_DIR)
    if not os.path.exists(DUMP_LABEL_DIR):
        os.makedirs(DUMP_LABEL_DIR)
    if not os.path.exists(DUMP_CALIB_DIR):
        os.makedirs(DUMP_CALIB_DIR)
    
def write_point_clouds():

    for filename in natsorted(os.listdir(CLOUD_DIR)):
        print('Transforming cloud ' + filename + ' to ' + filename.strip('.ply') + '.txt')
        pcd = o3d.io.read_point_cloud(CLOUD_DIR + filename)
        o3d.io.write_point_cloud(DUMP_CLOUD_DIR + filename.strip('.ply') + ".xyzrgb", pcd)
    for filename in natsorted(os.listdir(DUMP_CLOUD_DIR)):
        os.rename(DUMP_CLOUD_DIR + filename, DUMP_CLOUD_DIR + filename.strip('.xyzrgb') + '.txt')

def write_images():

    for filename in natsorted(os.listdir(IMAGE_DIR)):
        print('Copying image ' + filename)
        shutil.copyfile(IMAGE_DIR + filename, DUMP_IMAGE_DIR + filename)

def write_labels():
    """Combine 2D and 3D labels and write into one .txt file"""

    for two_d_filename in natsorted(os.listdir(LABEL_2D_DIR)):
        print('Transforming label ' + two_d_filename + ' to ' + two_d_filename.strip('.json') + '.txt')

        with open(LABEL_2D_DIR + two_d_filename) as f:
                data = json.load(f)
        
        class_name = data[0]['ObjectClassName']
        x_top_left = data[0]['Left']
        y_top_left = data[0]['Top']
        x_bottom_right = data[0]['Right']
        y_bottom_right = data[0]['Bottom']
        
        label_2d = [class_name, x_top_left, y_top_left, x_bottom_right, y_bottom_right]
        np.savetxt(DUMP_LABEL_DIR + two_d_filename.strip('.json') + '.txt', label_2d, newline = ' ', fmt='%s')      

    for three_d_filename in natsorted(os.listdir(LABEL_3D_DIR)):

        with open(LABEL_3D_DIR + three_d_filename) as f:
                data = json.load(f)
        
        centroid_x = data['objects'][0]['centroid']['x']
        centroid_y = data['objects'][0]['centroid']['y']
        centroid_z = data['objects'][0]['centroid']['z']
        coeffs_l = data['objects'][0]['dimensions']['l']
        coeffs_w = data['objects'][0]['dimensions']['w']
        coeffs_h = data['objects'][0]['dimensions']['h']
        angle_1 = 0
        angle_2 = 0


        label_3d = [centroid_x, centroid_y, centroid_z, coeffs_l, coeffs_w, coeffs_h, angle_1, angle_2]
        label_3d = [round(num, 3) for num in label_3d]

        with open(DUMP_LABEL_DIR + three_d_filename.strip('.json') + '.txt', "r") as f:
            label_2d=[i for line in f for i in line.split(' ')]
        
        label = [label_2d[0], int(label_2d[1]), int(label_2d[2]), int(label_2d[3]), int(label_2d[4])] + label_3d

        np.savetxt(DUMP_LABEL_DIR + three_d_filename.strip('.json') + '.txt', label, newline = ' ', fmt='%s') 

def write_calib():

    with open(CALIB_FILE) as file:
        calib = yaml.load(file, Loader=yaml.FullLoader)

    extrin = np.asarray(calib[1]['extrin'])
    intrin = np.asarray(calib[0]['intrin'])
    # votenet Format:
    intrin = [intrin[0],intrin[1], intrin[3], intrin[6], intrin[2], intrin[7], intrin[4], intrin[5], intrin[8]]

    calib = np.vstack((extrin, intrin))

    count = len([name for name in os.listdir(DUMP_IMAGE_DIR)])

    for i in range(count):
        print('Writing calibration file ' + str(i+1).zfill(4) + '.txt')
        np.savetxt(DUMP_CALIB_DIR + str(i+1).zfill(4) + '.txt', calib, fmt='%s') 

def write_split_files():

    # get count of files and calculate train and test share depending on split size
    count = len([name for name in os.listdir(DUMP_IMAGE_DIR)])
    train_share = round(count * args.split)
    test_share = count - train_share
    
    # shuffle randomly
    np.random.seed(7331)
    files = np.arange(1,count+1)
    np.random.shuffle(files)

    # create train and test data files
    train_data = natsorted(files[:train_share])
    test_data = natsorted(files[train_share:train_share + test_share])

    with open(DUMP_DIR + 'train_data_idx.txt', 'w') as f:
        f.write("\n".join(map(str, train_data)))

    with open(DUMP_DIR + 'val_data_idx.txt', 'w') as f:
        f.write("\n".join(map(str, test_data)))

def main():

    # Check if compressed data should be used - If yes, the 'data/' folder is emptied first and the archive is extracted into it
    if args.compressed_data is not None:
        for root, dirs, files in os.walk(DATA_DIR):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        zipping.read_zip_archive(args.compressed_data)

    make_directories()
    write_point_clouds()
    write_images()
    write_labels()
    write_calib()
    write_split_files()
    shutil.copyfile(OBJECTCLASSES_FILE, DUMP_OBJECTCLASSES_FILE)
    zipping.create_zip_archive_stage_four(args.compress)
    shutil.rmtree(DUMP_DIR)
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()  
    parser.add_argument("compress", type=str, help="Specify archive name to compress transformed files.")
    parser.add_argument("-s", "--split", type=int, default = 0.9, help="Specify train/(test) split size.")
    parser.add_argument("-cd", "--compressed_data", type=str, help="Specify archive name to load extraced files from.")
    args = parser.parse_args()

    main()