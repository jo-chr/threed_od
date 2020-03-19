# Preprocessing Phase

This phase covers all steps of the data preprocessing. First, the raw data is extracted. Second, some preprocessing is performed based on the point clouds. Third, The data is annotated using a custom 3D bounding box label tool. Fourth, 2D labels are extracted from the Robotron label tool. 

## Installation

Install the Python dependencies.

`pip install -r requirements.txt` 

## Data Extraction

Extract the raw data.

### Intel RealSense

Adjust the interval parameter according to how many frames you wish to extract: 1 = all possible frames, higher = less frames.

`python extract_data_realsense.py <file_name>.bag --interval 1` 

### Stereolabs ZED

Define the resolution of the recorded files.

`python extract_data_zed.py --resolution <res>` 

## Data Preprocessing

The preprocessing includes voxel downsampling, statistical outlier removal and rotation of the point clouds. 

Example for the RealSense:

`python preprocess_data.py -vs 5 -nn 80 -sr 1 -rx -90`

Example for the ZED:

`python preprocess_data.py -vs 0.005 -nn 80 -sr 1 -rx 190`

## Ground Truth Annotation 

Run `python label_data.py` to annotate the processed point clouds. Following, the basic controls of the tool are described.

| Key           | Description                                              |
| ------------- |----------------------------------------------------------|
| Left mouse button + drag   | Rotate point cloud                          |             
| Wheel mouse button + drag  | Translate point cloud                       |
| Shift + left button + drag | Roll point cloud                            |
| k                          | Lock screen and to switch to selection mode |
| c                          | Crop point cloud                            |
| q                          | Finish annotation process for one object    |

Crop the point cloud until the object of interest is left. After each cropping iteration, save the cropped point clouds in the `preprocessing/` directory. Once you are happy with the result, press q. You are prompted to enter the object class name and if there are any other objects within the current point cloud. 

For 2D annotations, use the Robotron `.json` label format and dump the labels in a directory called `label_2d/`.

## Transformation to VoteNet format

For training, [VoteNet](https://github.com/facebookresearch/votenet) is used. In order to transform the data to the expected format, run the following script:

`python transform_to_votenet_format.py`

The train/test split size can be adjusted using the `--split` flag (Float). 
