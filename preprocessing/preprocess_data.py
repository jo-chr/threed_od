import os, shutil, sys
import open3d as o3d
import argparse
from natsort import natsorted
import numpy as np
from distutils.dir_util import copy_tree

sys.path.append('../')
from utils import zipping

"""
Example usage:
    For Zed data:
        python3 preprocess_data.py -vs 5 -nn 80 -sr 1 -rx -90

    For Realsense data:
        python3 preprocess_data.py -vs 0.005 -nn 80 -sr 1 -rx 190
"""

DATA_DIR = 'data/'
PROCESSED_DATA_DIR = 'processed_data/'

def processing_loop():
    i = 1
    for filename in natsorted(os.listdir(DATA_DIR + 'cloud/')):
        print('----- Processing point cloud ' + str(i) + ' -----')
        pcd = o3d.io.read_point_cloud(DATA_DIR + 'cloud/' + filename)
        print('Points before transformation: ' + str(len(pcd.points)))
        o3d.io.write_point_cloud(PROCESSED_DATA_DIR + 'demonstration/' + 'downsampled_' + filename, pcd) ###

        # Function to downsample input pointcloud into output pointcloud with a voxel
        pcd = pcd.voxel_down_sample(voxel_size=args.voxel_size)
        print('Points after downsample: ' + str(len(pcd.points)))

        # Function to remove points that are further away from their neighbors in average
        pcd = pcd.remove_statistical_outlier(nb_neighbors=args.nb_neighbors,std_ratio=args.std_ratio)
        pcd = pcd[0]
        print('Points after outlier removal: ' + str(len(pcd.points)))
        o3d.io.write_point_cloud(PROCESSED_DATA_DIR + 'demonstration/' + 'outlier_removed_' + filename, pcd) ###
        
        # Point cloud rotation --> votenet expects z=up, y=forward, x=right-ward
        # Function rotate() seems to have bugs in o3d 0.9.0, only trial and error works
        print('Rotating point cloud')
        pcd = pcd.rotate(pcd.get_rotation_matrix_from_xyz([args.rotation_x,args.rotation_y,args.rotation_z]), center=False)

        o3d.io.write_point_cloud(PROCESSED_DATA_DIR + 'cloud/' + filename, pcd)
        i += 1

def make_directories():
    """Make directories for output."""
    if not os.path.exists(PROCESSED_DATA_DIR + 'cloud/'):
        os.makedirs(PROCESSED_DATA_DIR + 'cloud/')
    if not os.path.exists(PROCESSED_DATA_DIR + 'demonstration/'):
        os.makedirs(PROCESSED_DATA_DIR + 'demonstration/')
    if not os.path.exists(PROCESSED_DATA_DIR + 'image/'):
        os.makedirs(PROCESSED_DATA_DIR + 'image/')
    if not os.path.exists(PROCESSED_DATA_DIR + 'depth/'):
        os.makedirs(PROCESSED_DATA_DIR + 'depth/')

def copy_remaining_files():
    """Copy remaining files into 'processed_data/'."""
    print('Copying images, depth maps and calib.yml')
    copy_tree(DATA_DIR + 'image/', PROCESSED_DATA_DIR + 'image/')
    copy_tree(DATA_DIR + 'depth/', PROCESSED_DATA_DIR + 'depth/')
    shutil.copy2(DATA_DIR + 'calib.yml', PROCESSED_DATA_DIR + 'calib.yml')

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
    processing_loop()    
    copy_remaining_files()
    
    if args.compress is not None:
        zipping.create_zip_archive_stage_two(args.compress)
    else: pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser()  
    parser.add_argument("-vs", "--voxel_size", type=float, default = 0.005, help="Downsample the point cloud with the specified voxel size.")
    parser.add_argument("-nn", "--nb_neighbors", type=int, default = 80, help="Statistical outlier removal: number of neighbors around the target point.")
    parser.add_argument("-sr", "--std_ratio", type=float, default= 1, help="Statistical outlier removal: standard deviation ratio.")
    parser.add_argument("-rx", "--rotation_x", type=int, default= 90, help="Specify angle for rotation around x-axis.")
    parser.add_argument("-ry", "--rotation_y", type=int, default= 0, help="Specify angle for rotation around y-axis.")
    parser.add_argument("-rz", "--rotation_z", type=int, default= 0, help="Specify angle for rotation around z-axis.")
    parser.add_argument("-cd", "--compressed_data", type=str, help="Specify archive name to load extraced files from.")
    parser.add_argument("-c", "--compress", type=str, help="Specify archive name to compress extracted files.")
    args = parser.parse_args()

    main()