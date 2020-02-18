import glob, os
import open3d as o3d
import numpy as np
import json

import prompt

DATA = 'data/'
LABEL = 'label/'


def pick_points(pcd):
    vis = o3d.visualization.VisualizerWithEditing()
    vis.create_window()
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

        with open(LABEL + file_name[:-4] + '.json', 'w') as outfile:
            json.dump(data, outfile)
    else:
        with open(LABEL + file_name[:-4] + '.json') as json_file:
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

        with open(LABEL + file_name[:-4] + '.json', 'w') as outfile:
            json.dump(data, outfile)
        

def clean_up():
    for item in os.listdir('.'):
        if item.endswith('.json'):
            os.remove(item)
        elif item.endswith('.ply'):
            os.remove(item)

def label_loop(filename):
    print('Filename: ' + filename)
    pcd = o3d.io.read_point_cloud(DATA + filename)
    pick_points(pcd)
    obj = get_final_object_cloud()
    center, wlh = get_bb_values(obj)
    class_name = input("Specify class name: ")
    write_to_json(file_name=filename,class_name=class_name,center = center,wlh = wlh,add=False)
    clean_up()

def label_loop_more_objects(filename):
    print('Filename: ' + filename)
    pcd = o3d.io.read_point_cloud(DATA + filename)
    pick_points(pcd)
    obj = get_final_object_cloud()
    center, wlh = get_bb_values(obj)
    class_name = input("Specify class name: ")
    write_to_json(file_name=filename,class_name=class_name,center = center,wlh = wlh,add=True)
    clean_up()
    answer = prompt.main()
    if answer == False:
        pass
    else:
        label_loop_more_objects(filename)


def main():
    for filename in sorted(os.listdir(DATA)):
        if filename.endswith('.ply'):
            label_loop(filename)
            answer = prompt.main()
            if answer == False:
                pass
            else:
                label_loop_more_objects(filename)
        else: print('No point cloud in ply format: ' + filename)    

if __name__ == '__main__':
    main()