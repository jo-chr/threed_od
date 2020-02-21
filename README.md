# 3D Object Detection in Indoor Environments

## Introduction

This system consists of three steps: Preprocessing, Training and Inference.

## Preprocessing

Navigate to preprocessing/ and perform the following steps in order:

1. extract_data_'device'.py
2. preprocess_data.py
3. label_data.py
4. transform_to_votenet_format.py

## Training

### Set up Training Container

Build Docker container using the provided Dockerfile.

    docker build -t training_3d .

Run Docker container:

    docker run -it --runtime nvidia 'container_id' /bin/bash 

Copy preprocessed files into container:

    docker cp /home/jonas/Desktop/Projekte/threed_od/training/trainval/ 04b:/usr/local/training/votenet/data/

### Prepare data

To check, if the data was preprocessed right, navigate to data/ folder and run

    python data.py --viz

This will visualize the point clouds, ground truth 3D bounding boxes, 2D bounding boxes and projected depth maps.
The results are dumped in data/data_viz_dump/

Generate data set

    python data.py --gen_data

### Run training

Run trainng using the following command:

    CUDA_VISIBLE_DEVICES=0 python3 train.py --log_dir 'log_dir_name'
