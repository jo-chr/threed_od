# Inference Phase

## Prerequisites

The host system must use a Linux distribution and must have Docker, CUDA and cuDNN installed on it. Tested with Ubuntu 18.04, CUDA 10.0 and cuDNN 7.5.

## Preparation

Place your models into the `models/` directory and edit the `modelconfig.json` file. Examples are given. 
In the `data/` directory edit the files `data.py`, `model_util.py` and `utils.py` according to your model specs.

## Building and Running the Inference Image

Build the image running the Dockerfile `docker build -t 3dod.serving .` 
Run the image using `docker run -p 8080:80 --runtime nvidia 3dod.serving`

## Testing the Inference API using Postman

To retrieve the available models send a GET request to `http://localhost:8080/api/models`

To run the inference for a point cloud send a POST request to `http://localhost:8080/api/detect`
As parameters set the `model_id` to the specific model. In the body, enter `file` as key and the point cloud as value.
