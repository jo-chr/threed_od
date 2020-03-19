# Deep Hough Voting for 3D Object Detection in Point Clouds
Created by <a href="http://charlesrqi.com" target="_blank">Charles R. Qi</a>, <a href="https://orlitany.github.io/" target="_blank">Or Litany</a>, <a href="http://kaiminghe.com/" target="_blank">Kaiming He</a> and <a href="https://geometry.stanford.edu/member/guibas/" target="_blank">Leonidas Guibas</a> from <a href="https://research.fb.com/category/facebook-ai-research/" target="_blank">Facebook AI Research</a> and <a href="http://www.stanford.edu" target="_blank">Stanford University</a>.

![teaser](https://github.com/facebookresearch/votenet/blob/master/doc/teaser.jpg)

## Introduction
This repository is code release for our ICCV 2019 paper (arXiv report [here](https://arxiv.org/pdf/1904.09664.pdf)).

Current 3D object detection methods are heavily influenced by 2D detectors. In order to leverage architectures in 2D detectors, they often convert 3D point clouds to regular grids (i.e., to voxel grids or to bird’s eye view images), or rely on detection in 2D images to propose 3D boxes. Few works have attempted to directly detect objects in point clouds. In this work, we return to first principles to construct a 3D detection pipeline for point cloud data and as generic as possible. However, due to the sparse nature of the data – samples from 2D manifolds in 3D space – we face a major challenge when directly predicting bounding box parameters from scene points: a 3D object centroid can be far from any surface point thus hard to regress accurately in one step. To address the challenge, we propose VoteNet, an end-to-end 3D object detection network based on a synergy of deep point set networks and Hough voting. Our model achieves state-of-the-art 3D detection on two large datasets of real 3D scans, ScanNet and SUN RGB-D with a simple design, compact model size and high efficiency. Remarkably, VoteNet outperforms previous methods by using purely geometric information without relying on color images.

In this repository, we provide VoteNet model implementation (with Pytorch) as well as data preparation, training and evaluation scripts on SUN RGB-D and ScanNet.

## Citation

If you find our work useful in your research, please consider citing:

    @inproceedings{qi2019deep,
        author = {Qi, Charles R and Litany, Or and He, Kaiming and Guibas, Leonidas J},
        title = {Deep Hough Voting for 3D Object Detection in Point Clouds},
        booktitle = {Proceedings of the IEEE International Conference on Computer Vision},
        year = {2019}
    }

## Acknowledgements
We want to thank Erik Wijmans for his PointNet++ implementation in Pytorch ([original codebase](https://github.com/erikwijmans/Pointnet2_PyTorch)).

## License
votenet is relased under the MIT License. See the [LICENSE file](https://arxiv.org/pdf/1904.09664.pdf) for more details.

## Change log
10/20/2019: Fixed a bug of the 3D interpolation customized ops (corrected gradient computation). Re-training the model after the fix slightly improves mAP (less than 1 point).
