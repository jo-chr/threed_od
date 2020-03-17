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
