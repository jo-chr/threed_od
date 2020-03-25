# Training Phase

This phase covers all steps of the training. First, a training image is build using Docker. Second, the data is prepared for training. Third, the training is executed.

## Prerequisites

The host system must use a Linux distribution and must have Docker, CUDA and cuDNN installed on it. Tested with Ubuntu 18.04, CUDA 10.0 and cuDNN 7.5.

## Building and Running the Training Image

Build the image running the Dockerfile `docker build -t 3dod.training .`                                             
Run the image using `docker run -p 3333:3333 -p 4444:4444 --mount type=bind,source="$(pwd)"/trainval,target=/usr/local/training/votenet/data/trainval/ --runtime nvidia 3dod.training`

Open jupyter lab in your browser. To open locallay use `http://localhost:3333/3dod/`

## Preparing the training

To generate the ground truth votes run `python3 data.py --gen_data` in a terminal window.

## Training a Model

To train a model navigate to `votenet/` and run `CUDA_VISIBLE_DEVICES=0 python3 train.py --log_dir <log_dir_name> --max_epoch <num_max_epoch> --batch_size <batch_size> --learning_rate <learning_rate>`

Example: `CUDA_VISIBLE_DEVICES=0 python3 train.py --log_dir log --max_epoch 40 --batch_size 1 --learning_rate 0.01`

TensorBoard can be started running `tensorboard --logdir=log --host=0.0.0.0 --port=4444 --path_prefix /tensorboard3dod/` in a new terminal.
To open enter `http://localhost:4444/tensorboard3dod/` in a browser.


## Evaluating a Model

To evaluate a trained model run `python3 eval.py --checkpoint_path log/checkpoint.tar --dump_dir eval --num_point 40000 --cluster_sampling seed_fps --use_3d_nms --use_cls_nms --per_class_proposal`
