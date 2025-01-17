# ISRO

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#installations">Installations</a></li>
    <li>
        <a href="#usage">Usage</a>
        <ul>
            <li><a href="#arguments-format">Arguments format</a></li>
        </ul>
        <ul>
            <li><a href="#proper-arguments-ordering">Proper arguments ordering</a></li>
        </ul>
    </li>
    <li>
      <a href="#model-description">Model Description</a>
      <ul>
            <li><a href="#lunar-turing-gan-t-gan">Lunar Turing-GAN (T-GAN)</a></li>
        </ul>
      <ul>
            <li><a href="#input-to-the-model">Input to the model</a></li>
        </ul>
    </li>
    <li> <a href="#baselines">Baselines</a></li>
    <li> <a href="#stitched-atlas">Stitched Atlas</a></li>
    <li>
      <a href="#evaluation-of-sr-images-using-feature-comparison">Evaluation of SR images using Feature Comparison</a>
      <ul>
            <li><a href="#dynamic-thresholding-algorithm">Dynamic Thresholding Algorithm</a></li>
      </ul>
    </li>
    <li><a href="#determination-of-physical-features">Determination of Physical Features</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

This project demonstrates the implementation of Deep Learning models for Image Super-Resolution of Lunar Surface data captured from 2 cameras from the Chandrayan-2 Mission of ISRO: namely TMC-2 and OHRC. 
Terrain Mapping Camera-2 (TMC-2) Chadrayaan-2 Orbiter maps the lunar surface in the panchromatic spectral band (0.5-0.8 microns) with a spatial resolution of 5 meter. The Orbiter Higher Resolution Camera (OHRC) onboard Chadrayaan-2 Orbiter is an imaging payloads which provides high resolution (~ 30 cm) images of lunar surface. The Deep Learning model is trained to perform image super-resolution (SR) of the low resolution images to obtain high resolution images (~16x).

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- PROJECT STRUCTURE -->

## Project Structure

```
.
├── ESRGAN
│   ├── assets
│   ├── cog_predict.py
│   ├── cog.yaml
│   ├── experiments
│   ├── inference_realesrgan.py
│   ├── inputs
│   ├── main_test_realesrgan.py
│   ├── MANIFEST.in
│   ├── options
│   ├── README.md
│   ├── realesrgan
│   ├── realesrgan.egg-info
│   ├── requirements.txt
│   ├── results
│   ├── scripts
│   ├── setup.cfg
│   ├── setup.py
│   ├── tb_logger
│   ├── tests
│   ├── VERSION
│   └── weights
├── HAT
│   ├── cog.yaml
│   ├── datasets
│   ├── experiments
│   ├── figures
│   ├── hat
│   ├── hat.egg-info
│   ├── options
│   ├── predict.py
│   ├── README.md
│   ├── requirements.txt
│   ├── results
│   ├── setup.cfg
│   ├── setup.py
│   └── VERSION
├── Interpolate
│   └── interpolate.py
├── LightEnhancement
│   ├── ckpt
│   ├── demo
│   ├── evaluate.py
│   ├── figure
│   ├── network
│   ├── README.md
│   ├── test.py
│   └── utils.py
├── MSR_SWINIR
│   ├── data
│   ├── docs
│   ├── figs
│   ├── kernels
│   ├── main_test_msrresnet.py
│   ├── main_test_swinir.py
│   ├── main_train_gan.py
│   ├── main_train_psnr.py
│   ├── matlab
│   ├── models
│   ├── options
│   ├── pretrained_weights
│   ├── README.md
│   ├── requirement.txt
│   ├── results
│   ├── retinaface
│   ├── scripts
│   ├── superresolution
│   └── utils
├── pipeline.py
├── README.md
├── requirements.txt
└── Sharpen_Denoise
    ├── NAFNet
    └── sharpen.py
```
<p align="right">(<a href="#top">back to top</a>)</p>


<!-- INSTALLATIONS -->

### Installations

```bash

# Change directory to project directory
cd ISRO

# Download model weights from the following link
# https://drive.google.com/drive/folders/1wmWoJ2gYrbt6Fqkyr3x8oS-cvFEfCic1?usp=sharing
# Put the appropriate models in the appropriate weights folders

# Download requirements for SwinIR
cd MSR_SWINIR
pip install -r requirement.txt
cd ..

# Download and setup requirements for RealESRGAN
cd ESRGAN
pip install basicsr
pip install facexlib
pip install gfpgan
pip install -r requirements.txt
python setup.py develop
cd ..

# Download and setup requirements for HAT
cd HAT
pip install -r requirements.txt
python setup.py develop
cd ..

```
<p align="right">(<a href="#top">back to top</a>)</p>


<!-- USAGE -->

## Usage

To run the super resolution code, you need to run the pipeline.py file
passing appropriate arguments. So the present working directory should be the
repository

```bash

python pipeline.py -i <input_file_path> -o <output_file_path> sr --sr_model <model_name> --scale <scale_factor> --tile <tile_size> int --scale <scale_factor> shp

```

Download the pretrained weights from this link: https://drive.google.com/drive/folders/1wmWoJ2gYrbt6Fqkyr3x8oS-cvFEfCic1?usp=share_link

Take note to download the trained weights to the appropriate folders as shown below (given in pipeline.py):
```bash
model_dict = {
    "realesrgan": {
        "sr_path": "ESRGAN",
        "model_path": "experiments/pretrained_models/net_g_15000_realesrgan.pth"
    },
    "msrresnet": {
        "sr_path": "MSR_SWINIR",
        "model_path": "pretrained_weights/msrresnet_x4_psnr.pth"
    },
    "swinir": {
        "sr_path": "MSR_SWINIR",
        "model_path": "pretrained_weights/20000_G_swinIr.pth"
    },
    "HAT": {
        "sr_path": "HAT/hat",
        "model_path": "../experiments/pretrained_models/net_g_5000_hat.pth"
    }
}
```

### Arguments format

| **option**        | **alternate option** | **description**                                                       | **default**                |
|-------------------|----------------------|-----------------------------------------------------------------------|----------------------------|
| --input           | -i                   | input file path for single file input                                 | inputs/input.png           |
| --output          | -o                   | output file path                                                      | outputs                    |
| --input_folder    | -if                  | input folder consisting of only images                                | None                       |
| --output_folder   | -of                  | output folder to store output images                                  | None                       |
| --compress_output | -co                  | flag to indicate whether to save intermediate generated images or not | True                       |
| sr                |                      |                                                                       |                            |
| --sr_model        | -sm                  | name of SR model                                                      | realesrgan                 |
| --sr_path         | -sp                  | path to SR code                                                       | ESRGAN                     |
| --tile            | -t                   | tile size to avoid CUDA error                                         | None                       |
| --model_path      | -mp                  | path of weights                                                       | None                       |
| --scale           | s                    | scale factor                                                          | 4                          |
| int               |                      |                                                                       |                            |
| --int_model       | -im                  | name of interpolation method                                          | bicubic                    |
| --int_path        | -ip                  | path to interpolation code                                            | Interpolate/interpolate.py |
| --scale           | -s                   | scale factor                                                          | 4                          |
| enh               |                      |                                                                       |                            |
| --enh_path        | -ep                  | path containing light enhancement code                                | LightEnhancement           |
| --enh_model       | -em                  | light enhancement model                                               | URetinex                   |
| shp               |                      |                                                                       |                            |
| den               |                      |                                                                       |                            |
| --tile            | -t                   | tile size to avoid cuda error                                         | None                       |


### Proper arguments ordering

-i or --input or -if or --input_folder or -co or --compress_output should be passed first in the arguments list.
Any upscaling should be followed by method name and its corresponding arguments.
For example, if we want to do superresolution 4x by using HAT model and then superresolution 4x by using RealESRGAN model
the proper command to execute will be:
```bash
python pipeline.py -i <input_file_path> -o <output_file_path> sr --sr_model HAT --scale 4 sr --sr_model realesrgan --scale 4
```

Sometimes, we may get CUDA out of memory error, then try to avoid it using tile argument.
Here we are doing 4x superreoslution by HAT using tiling followed by 4x interpolation followed by image sharpening
```bash
python pipeline.py -i <input_file_path> -o <output_file_path> sr --sr_model HAT --scale 4 --tile 256 int --scale 4 shp
```

Make sure to put the markers sr, int, etc. in between to apply corresponding scaling.

<p align="right">(<a href="#top">back to top</a>)</p>

## Model Description

### Lunar Turing-GAN (T-GAN)

<p align="center">
<img src="images/Lunar_T-Gan.png" alt="Figure describes the architecutre of our proposed Lunar Turing-GAN (T-GAN)">
 <br>
Architecutre of our proposed Lunar Turing-GAN (T-GAN)</p>

#### Input to the model:

* Original HR Image
* Low Resolution image (Downsized from Original)
* Manually annotated coordinates of hills and craters as separate .txt files

We modify the conventional discriminator of conventional GANs with a novel turing loss that ensures the model places a special emphasis on the region of interest: in our case the craters and the hills. More specifically, as shown in the figure above, we have a Turing Test 1 (T1) which is trained to discriminate the fake image (SR) from the original image (HR). The Turing Test 2 (T2) is trained to perform the same discrimination only on the craters. Likewise Turing Test 3 (T3) is trained to discriminate the hills in the lunar surface. We detect the hills and craters from the OHRC images by manual annotation.

<p align="right">(<a href="#top">back to top</a>)</p>

## Baselines

We compare our approach (Lunar T-GAN) with several state-of-the-art baselines as shown below
<br>
| Model                                          | Inference Time | Architecture | SSIM  | FSIM  | PSNR   | SAM    |
|------------------------------------------------|----------------|--------------|-------|-------|--------|--------|
| BicubIc Interpolation                          | 21.8 s         | Maths        | 0.762 | 0.651 | 59.014 | 64.672 |
| SRGAN                                          | 55.9 s         | GAN          | 0.812 | 0.681 | 59.421 | 64.659 |
| EDSR                                           | 51.8 s         | GAN          | 0.814 | 0.685 | 59.482 | 64.654 |
| WDSR                                           | 39.5 s         | GAN          | 0.816 | 0.687 | 59.496 | 64.652 |
| MSRNet                                         | 356 s          | CNN          | 0.828 | 0.691 | 59.561 |  64.42 |
| SwinIR                                         | 359 s          | Transformer  | 0.858 | 0.696 | 59.653 |  64.39 |
| Attention 2 Attention                          | 35.7 s         | Attention    | 0.812 | 0.679 | 59.305 | 64.663 |
| Real ESRGAN                                    | 48.7 s         | GAN          | 0.838 | 0.689 | 59.559 | 64.645 |
| HAT                                            | 337s           | Transformer  |  0.88 | 0.705 | 59.719 | 64.635 |
| **Lunar T-GAN (Ours) - trained on 50 images**  | 11s            | GAN          | 0.794 | 0.672 | 59.104 | 64.669 |

<p align="right">(<a href="#top">back to top</a>)</p>

## Stitched Atlas

![Alt text](images/atlas_resized.png?raw=true "Figure shows the complete stitched lunar atlas")
<p align="center">Complete Lunar Atlas</p>

We stitched the TMC-2 data to form the complete lunar atlas. The map spans from -180° to +180° in longitude and -90° to 90° in latitude.

<p align="center">
<img src="images/stereo_resized.png" alt="Figure shows the stereo projection for the polar images of the moon" height="50%" width="50%">
<br>Stereographic projection for the polar images of the moon</p>

The above figure shows the stereographic projection centered on the South Pole of the moon, with a radius of 20° out from the Pole.

<p align="right">(<a href="#top">back to top</a>)</p>

## Evaluation of SR images using Feature Comparison

Observing changes in lunar super-resolution images can provide valuable information about the geological and physical processes that have shaped the moon's surface over time. This can provide a better understanding of the moon's history and evolution, as well as help in planning for future missions to the moon. The high-resolution images can also reveal new features and details that were previously not visible, leading to new discoveries and scientific insights. We have built a variety of algorithms for comparison of physical features obtainable from the lunar images, before and after super-resolution. This conveys the improvement in the detection and analysis of features in the super-resolved images.

### Dynamic Thresholding Algorithm:
We have used a dynamic thresholding algorithm on the DEM data. We have made a histogram of the pixel values and have considered the top 2% of the pixels for identifying hills within the terrain data. Similarly, we have considered the bottom 2## Eval of SR images using Feature Comparison

<p align="right">(<a href="#top">back to top</a>)</p>

## Determination of Physical Features

We observe an increase in the number of hills and high altitude features on the lunar surface due to an increase in the area covered under the altitude threshold. However, the increase and changes in shape are only observed for smaller features and not for large features. This shows that the super-resolution improves the DEM and image quality without and adding any extra features. 

![Alt text](images/image(2).png?raw=true "Contour Plot of High Altitude terrain")
<p align="center">Contour Plot of High Altitude terrain</p>

A 3D plot of the terrain for the original image and the super resolved image shows the effect of the super-resolution and the enhancement of physical features like slope and surface dimensions.

![Alt text](images/isro_3d_plots.png?raw=true "Three dimensional terrain map of original and super-resolved DEM image") 
<p align="center">Three dimensional terrain map of original and super-resolved DEM image</p>

<p align="right">(<a href="#top">back to top</a>)</p>
