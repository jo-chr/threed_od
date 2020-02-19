import os
from natsort import natsorted
import open3d as o3d
import shutil
import json
import numpy as np

DATA_DIR = 'processed_data/'
CLOUD_DIR = DATA_DIR + 'cloud/'
IMAGE_DIR = DATA_DIR + 'image/'
LABEL_2D_DIR = DATA_DIR + 'label_2d/'
LABEL_3D_DIR = DATA_DIR + 'label_3d/'
DUMP_DIR = 'temp_trainval/'
DUMP_CLOUD_DIR = DUMP_DIR + 'depth/'
DUMP_IMAGE_DIR = DUMP_DIR + 'image/'
DUMP_LABEL_DIR = DUMP_DIR + 'label/'
DUMP_CALIB_DIR = DUMP_DIR + 'calib/'

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
    return

def main():

    make_directories()

    #write_point_clouds()
    #write_images()
    #write_labels()
    




if __name__ == "__main__":

    main()