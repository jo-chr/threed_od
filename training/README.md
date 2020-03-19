# Training Phase

This phase covers all steps of the training. First, a training image is build using Docker. Second, the data is prepared for training. Third, the training is executed.

## Prerequisites

The host system must use a Linux distribution and must have Docker, CUDA and cuDNN installed on it. Tested with Ubuntu 18.04, CUDA 10.0 and cuDNN 7.5.

## Building and Running the Training Image

Build the image running the Dockerfile `docker build -t 3dod.training .`                                                      
Run the image running `docker run -p 3333:3333 --runtime nvidia 3dod.training`

## 
