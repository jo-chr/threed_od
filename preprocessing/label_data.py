import os, glob, sys
from natsort import natsorted
import open3d as o3d
import numpy as np
import json
import argparse

sys.path.append('../')
from utils import prompt, zipping


DATA_DIR = 'processed_data/cloud/'
LABEL_DIR = 'processed_data/label_3d/'


def check_existing_label():
    files_count = len([filename for filename in os.listdir(LABEL_DIR)])
    if files_count > 0:
        return files_count
    else:
        return
    
def pick_points(pcd):
    vis = o3d.visualization.VisualizerWithEditing()
    vis.create_window(window_name = 'ROBO 3D')
    vis.add_geometry(pcd)
    vis.run()
    vis.destroy_window()

def get_final_object_cloud():
    clouds = sorted(glob.glob('*ply'))
    return clouds[-1]

def get_bb_values(obj):
    pcd = o3d.io.read_point_cloud(obj)
    bb = pcd.get_axis_aligned_bounding_box()
    bb_center = bb.get_center()
    bb_wlh = bb.get_half_extent() 
    return bb_center, bb_wlh

def write_to_json(file_name,class_name,center,wlh,add):
        
    if add == False:    
        data = {}
        data = {'fileName':file_name,
                'objects':[{
                'className':class_name,
                'centroid':{
                    'x':center[0],
                    'y':center[1],
                    'z':center[2]},
                'dimensions':{
                    'w':wlh[0],
                    'l':wlh[1],
                    'h':wlh[2]}
                }]}

        with open(LABEL_DIR + file_name[:-4] + '.json', 'w') as outfile:
            json.dump(data, outfile)
    else:
        with open(LABEL_DIR + file_name[:-4] + '.json') as json_file:
            data = json.load(json_file)

        new_entry = {}
        new_entry = {
                    'className':class_name,
                    'centroid':{
                        'x':center[0],
                        'y':center[1],
                        'z':center[2]},
                    'dimensions':{
                        'w':wlh[0],
                        'l':wlh[1],
                        'h':wlh[2]}
                    }
        data["objects"].append(new_entry)

        with open(LABEL_DIR + file_name[:-4] + '.json', 'w') as outfile:
            json.dump(data, outfile)
        

def clean_up():
    for item in os.listdir('.'):
        if item.endswith('.json'):
            os.remove(item)
        elif item.endswith('.ply'):
            os.remove(item)

def label_loop(filename):
    print('Filename: ' + filename)
    pcd = o3d.io.read_point_cloud(DATA_DIR + filename)
    
    pick_points(pcd)
    obj = get_final_object_cloud()
    center, wlh = get_bb_values(obj)
    class_name = input("Specify class name: ")
    write_to_json(file_name=filename,class_name=class_name,center = center,wlh = wlh,add=False)
    clean_up()

def label_loop_more_objects(filename):
    print('Filename: ' + filename)
    pcd = o3d.io.read_point_cloud(DATA_DIR + filename)
    pick_points(pcd)
    obj = get_final_object_cloud()
    center, wlh = get_bb_values(obj)
    class_name = input("Specify class name: ")
    write_to_json(file_name=filename,class_name=class_name,center = center,wlh = wlh,add=True)
    clean_up()
    answer = prompt.main(message = 'Are there other objects within the point cloud (y/n)?')
    if answer == False:
        pass
    else:
        label_loop_more_objects(filename)


def main():
    
    if not os.path.exists(LABEL_DIR):
        os.makedirs(LABEL_DIR) 

    # Check if compressed data should be used - If yes, the 'data/' folder is emptied first and the archive is extracted into it
    if args.compressed_data is not None:
        for root, dirs, files in os.walk(DATA_DIR):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        zipping.read_zip_archive(args.compressed_data)

    existing_labels = check_existing_label() 

    # Skip first n clouds when they have been already labeled
    # After that, perform labeling
    for filename in natsorted(os.listdir(DATA_DIR))[existing_labels:]:
        label_loop(filename)
        answer = prompt.main(message = 'Are there other objects within the point cloud (y/n)?')
        if answer == False:
            pass
        else:
            label_loop_more_objects(filename)
    
    if args.compress is not None:
        zipping.create_zip_archive_stage_three(args.compress)
    else: pass

    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()  
    parser.add_argument("-cd", "--compressed_data", type=str, help="Specify archive name to load extraced files from.")
    parser.add_argument("-c", "--compress", type=str, help="Specify archive name to compress extracted files.")
    args = parser.parse_args()

    main()