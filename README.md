# 3D Object Detection in Indoor Environments

## Introduction

This is a system that covers all aspects of a 3D object detection pipeline. It essentially consists of three main phases: [Data preprocessing](/preprocessing/README.md), [training](/training/README.md) and [inference](/inference/README.md). The individual steps are described in more detail in the respective directories. But first you have to place your raw data in this project.

## Raw Data

So far, this project supports two sensor devices: Intel RealSense and StereoLabs ZED. Exemplary data is provided for both devices. In the case of the RealSense, the data has not yet been extracted and is stored in `.bag` files. In case of the ZED, the data has already been extracted (RGB images, depth maps, point clouds). 

Navigate to `raw_data/` and place the exemplary data in the respective directory. 

## Special System Requirements

Note that the containerized training environment and inference API run on a Linux distribution using the NVIDIA runtime environment. Therefore, the host system itself must be a Linux distribution and have CUDA and cuDNN installed. For more information, refer to the corresponding README files. 
