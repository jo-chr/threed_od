import os, shutil
import open3d as o3d
import argparse
from natsort import natsorted
import numpy as np


DATA_DIR = 'data/cloud/'
PROCESSED_DATA_DIR = 'processed_data/cloud/'

def main():

    if not os.path.exists(PROCESSED_DATA_DIR):
        os.makedirs(PROCESSED_DATA_DIR)

    i = 1
    for filename in natsorted(os.listdir(DATA_DIR)):
        print('----- Processing point cloud ' + str(i) + ' -----')
        pcd = o3d.io.read_point_cloud(DATA_DIR + filename)
        print('Points before manipulation: ' + str(len(pcd.points)))

        # Function to downsample input pointcloud into output pointcloud with a voxel
        pcd = pcd.voxel_down_sample(voxel_size=args.voxel_size)
        print('Points after downsample: ' + str(len(pcd.points)))

        # Function to remove points that are further away from their neighbors in average
        pcd = pcd.remove_statistical_outlier(nb_neighbors=args.nb_neighbors,std_ratio=args.std_ratio)
        pcd = pcd[0]
        print('Points after outlier removal: ' + str(len(pcd.points)))
        
        # Point cloud rotation --> votenet expects z=up, y=forward, x=right-ward
        # Function rotate() seems to have bugs in o3d 0.9.0, only trial and error works
        print('Rotating point cloud')
        pcd = pcd.rotate(pcd.get_rotation_matrix_from_xyz([190,0,0]), center=False)

        o3d.io.write_point_cloud(PROCESSED_DATA_DIR + filename, pcd)
        i += 1
    return



if __name__ == "__main__":
    parser = argparse.ArgumentParser()  
    parser.add_argument("-vs", "--voxel_size", type=float, default = 0.005, help="Downsample the point cloud with the specified voxel size.")
    parser.add_argument("-nn", "--nb_neighbors", type=int, default = 80, help="Statistical outlier removal: number of neighbors around the target point.")
    parser.add_argument("-sr", "--std_ratio", type=float, default= 1, help="Statistical outlier removal: standard deviation ratio.")
    args = parser.parse_args()

    main()