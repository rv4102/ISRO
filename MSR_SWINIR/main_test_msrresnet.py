import os.path
import logging
import re

import numpy as np
from collections import OrderedDict

import torch
import argparse

from utils import utils_logger
from utils import utils_image as util
from utils import utils_model


'''
Spyder (Python 3.6)
PyTorch 1.1.0
Windows 10 or Linux

Kai Zhang (cskaizhang@gmail.com)
github: https://github.com/cszn/KAIR

If you have any question, please feel free to contact with me.
Kai Zhang (e-mail: cskaizhang@gmail.com)
(github: https://github.com/cszn/KAIR)

by Kai Zhang (12/Dec./2019)
'''

"""
# --------------------------------------------
testing demo for RRDB-ESRGAN
https://github.com/xinntao/ESRGAN
@inproceedings{wang2018esrgan,
  title={Esrgan: Enhanced super-resolution generative adversarial networks},
  author={Wang, Xintao and Yu, Ke and Wu, Shixiang and Gu, Jinjin and Liu, Yihao and Dong, Chao and Qiao, Yu and Change Loy, Chen},
  booktitle={European Conference on Computer Vision (ECCV)},
  pages={0--0},
  year={2018}
}
@inproceedings{ledig2017photo,
  title={Photo-realistic single image super-resolution using a generative adversarial network},
  author={Ledig, Christian and Theis, Lucas and Husz{\'a}r, Ferenc and Caballero, Jose and Cunningham, Andrew and Acosta, Alejandro and Aitken, Andrew and Tejani, Alykhan and Totz, Johannes and Wang, Zehan and others},
  booktitle={IEEE conference on computer vision and pattern recognition},
  pages={4681--4690},
  year={2017}
}
# --------------------------------------------
|--model_zoo                # model_zoo
   |--msrresnet_x4_gan      # model_name, optimized for perceptual quality      
   |--msrresnet_x4_psnr     # model_name, optimized for PSNR
|--testset                  # testsets
   |--set5                  # testset_name
   |--srbsd68
|--results                  # results
   |--set5_msrresnet_x4_gan # result_name = testset_name + '_' + model_name
   |--set5_msrresnet_x4_psnr
# --------------------------------------------
"""


def main():

    # ----------------------------------------
    # Preparation
    # ----------------------------------------

    parser = argparse.ArgumentParser()
    parser.add_argument('--scale', type=int, default=4, help='scale factor: 1, 2, 3, 4, 8') # 1 for dn and jpeg car)
    parser.add_argument('--model_name', type=str, default='msrresnet_x4_psnr')
    parser.add_argument('--model_path', type=str,
                        default='/content/drive/MyDrive/Super_Resolution_code/KAIR-master/pretrained_weights/msrresnet_x4_psnr.pth')
    parser.add_argument('--folder_lq', type=str, default="/content/drive/MyDrive/Super_Resolution_code/KAIR-master/testsets/hr_tests", help='input low-quality test image folder')
    parser.add_argument('--file_name', type=str, default=None, help='specific file to do sr')
    parser.add_argument('--tile', type=int, default=None, help='Tile size, None for no tile during testing (testing as a whole)')
    parser.add_argument('--tile_overlap', type=int, default=32, help='Overlapping of different tiles')
    parser.add_argument('--output_path', type=str, default=None, help="output file path")
    args = parser.parse_args()



    #model_name = 'msrresnet_x4_psnr'     # 'msrresnet_x4_gan' | 'msrresnet_x4_psnr'
    model_name = args.model_name
    #testset_name = 'set5'                # test set,  'set5' | 'srbsd68'
    #testset_name = 'hr_tests'
    #need_degradation = True              # default: True
    need_degradation = False
    x8 = False                           # default: False, x8 to boost performance, default: False
    #sf = [int(s) for s in re.findall(r'\d+', model_name)][0]  # scale factor
    sf = args.scale
    show_img = False                     # default: False
    window_size = 8                      # for tiling



    task_current = 'sr'       # 'dn' for denoising | 'fsr' for super-resolution
    n_channels = 3            # fixed
    model_pool = 'pretrained_weights'# 'model_zoo'  # fixed
    #testsets = 'testsets'     # fixed
    results = '/content/drive/MyDrive/Super_Resolution_code/KAIR-master/superresolution/super_resolution_result'       # fixed
    noise_level_img = 0       # fixed: 0, noise level for LR image
    result_name = "sdf"
    border = sf if task_current == 'sr' else 0     # shave boader to calculate PSNR and SSIM
    #model_path = os.path.join(model_pool, model_name+'.pth')
    model_path = args.model_path

    # ----------------------------------------
    # L_path, E_path, H_path
    # ----------------------------------------

    # L_path = os.path.join(testsets, testset_name) # L_path, for Low-quality images
    L_path = args.folder_lq # L_path, for Low-quality images
    H_path = L_path                               # H_path, for High-quality images
    E_path = results  # E_path, for Estimated images
    util.mkdir(E_path)

    # if H_path == L_path:
    #     need_degradation = True
    logger_name = result_name
    utils_logger.logger_info(logger_name, log_path=os.path.join(E_path, logger_name+'.log'))
    logger = logging.getLogger(logger_name)

    #need_H = True if H_path is not None else False
    need_H = False
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # ----------------------------------------
    # load model
    # ----------------------------------------

    from models.network_msrresnet import MSRResNet1 as net
    model = net(in_nc=n_channels, out_nc=n_channels, nc=64, nb=16, upscale=4)
    model.load_state_dict(torch.load(model_path), strict=True)
    model.eval()
    for k, v in model.named_parameters():
        v.requires_grad = False
    model = model.to(device)
    logger.info('Model path: {:s}'.format(model_path))
    number_parameters = sum(map(lambda x: x.numel(), model.parameters()))
    logger.info('Params number: {}'.format(number_parameters))

    test_results = OrderedDict()
    test_results['psnr'] = []
    test_results['ssim'] = []
    test_results['psnr_y'] = []
    test_results['ssim_y'] = []

    logger.info('model_name:{}, image sigma:{}'.format(model_name, noise_level_img))
    logger.info(L_path)
    L_paths = util.get_image_paths(L_path)
    H_paths = util.get_image_paths(H_path) if need_H else None

    print("PERFORMING SUPER RESOLUTION USING MSRRESNET")

    for idx, img in enumerate(L_paths):
        if args.file_name is not None and args.file_name!=os.path.basename(img):
            continue

        # ------------------------------------
        # (1) img_L
        # ------------------------------------

        img_name, ext = os.path.splitext(os.path.basename(img))
        # logger.info('{:->4d}--> {:>10s}'.format(idx+1, img_name+ext))
        img_L = util.imread_uint(img, n_channels=n_channels)
        img_L = util.uint2single(img_L)

        # degradation process, bicubic downsampling
        if need_degradation:
            img_L = util.modcrop(img_L, sf)
            img_L = util.imresize_np(img_L, 1/sf)
            # img_L = util.uint2single(util.single2uint(img_L))
            # np.random.seed(seed=0)  # for reproducibility
            # img_L += np.random.normal(0, noise_level_img/255., img_L.shape)

        util.imshow(util.single2uint(img_L), title='LR image with noise level {}'.format(noise_level_img)) if show_img else None

        img_L = util.single2tensor4(img_L)
        img_L = img_L.to(device)

        print("Input image shape = ", img_L.shape)

        # ------------------------------------
        # (2) img_E
        # ------------------------------------

        if not x8:
            if args.tile is None:
                img_E = model(img_L)
            else:
                
                # test the image tile by tile
                b, c, h, w = img_L.size()
                tile = min(args.tile, h, w)
                assert tile % window_size == 0, "tile size should be a multiple of window_size"
                tile_overlap = args.tile_overlap

                stride = tile - tile_overlap
                h_idx_list = list(range(0, h-tile, stride)) + [h-tile]
                w_idx_list = list(range(0, w-tile, stride)) + [w-tile]
                E = torch.zeros(b, c, h*sf, w*sf).type_as(img_L)
                W = torch.zeros_like(E)

                for h_idx in h_idx_list:
                    for w_idx in w_idx_list:
                        in_patch = img_L[..., h_idx:h_idx+tile, w_idx:w_idx+tile]
                      
                        out_patch = model(in_patch)
                    
                        out_patch_mask = torch.ones_like(out_patch)

                        E[..., h_idx*sf:(h_idx+tile)*sf, w_idx*sf:(w_idx+tile)*sf].add_(out_patch)
                        W[..., h_idx*sf:(h_idx+tile)*sf, w_idx*sf:(w_idx+tile)*sf].add_(out_patch_mask)
                img_E = E.div_(W)
        else:
            if args.tile is None:
                img_E = utils_model.test_mode(model, img_L, mode=3, sf=sf)
            else:
                # test the image tile by tile
                b, c, h, w = img_L.size()
                tile = min(args.tile, h, w)
                assert tile % window_size == 0, "tile size should be a multiple of window_size"
                tile_overlap = args.tile_overlap

                stride = tile - tile_overlap
                h_idx_list = list(range(0, h-tile, stride)) + [h-tile]
                w_idx_list = list(range(0, w-tile, stride)) + [w-tile]
                E = torch.zeros(b, c, h*sf, w*sf).type_as(img_L)
                W = torch.zeros_like(E)

                for h_idx in h_idx_list:
                    for w_idx in w_idx_list:
                        in_patch = img_L[..., h_idx:h_idx+tile, w_idx:w_idx+tile]
                        out_patch = utils.model.test_mode(model, in_patch, mode=3, sf=sf)
                        out_patch_mask = torch.ones_like(out_patch)

                        E[..., h_idx*sf:(h_idx+tile)*sf, w_idx*sf:(w_idx+tile)*sf].add_(out_patch)
                        W[..., h_idx*sf:(h_idx+tile)*sf, w_idx*sf:(w_idx+tile)*sf].add_(out_patch_mask)

        img_E = util.tensor2uint(img_E)

        if need_H:

            # --------------------------------
            # (3) img_H
            # --------------------------------

            img_H = util.imread_uint(H_paths[idx], n_channels=n_channels)
            img_H = img_H.squeeze()
            img_H = util.modcrop(img_H, sf)

            # --------------------------------
            # PSNR and SSIM
            # --------------------------------

            psnr = util.calculate_psnr(img_E, img_H, border=border)
            ssim = util.calculate_ssim(img_E, img_H, border=border)
            test_results['psnr'].append(psnr)
            test_results['ssim'].append(ssim)
            logger.info('{:s} - PSNR: {:.2f} dB; SSIM: {:.4f}.'.format(img_name+ext, psnr, ssim))
            util.imshow(np.concatenate([img_E, img_H], axis=1), title='Recovered / Ground-truth') if show_img else None

            if np.ndim(img_H) == 3:  # RGB image
                img_E_y = util.rgb2ycbcr(img_E, only_y=True)
                img_H_y = util.rgb2ycbcr(img_H, only_y=True)
                psnr_y = util.calculate_psnr(img_E_y, img_H_y, border=border)
                ssim_y = util.calculate_ssim(img_E_y, img_H_y, border=border)
                test_results['psnr_y'].append(psnr_y)
                test_results['ssim_y'].append(ssim_y)

        # ------------------------------------
        # save results
        # ------------------------------------

        print("Output image shape = ", img_E.shape)
        if args.output_path is None:
            util.imsave(img_E, os.path.join(E_path, img_name+'_'+model_name+'.png'))
        else:
            util.imsave(img_E, args.output_path)

    if need_H:
        ave_psnr = sum(test_results['psnr']) / len(test_results['psnr'])
        ave_ssim = sum(test_results['ssim']) / len(test_results['ssim'])
        logger.info('Average PSNR/SSIM(RGB) - {} - x{} --PSNR: {:.2f} dB; SSIM: {:.4f}'.format(result_name, sf, ave_psnr, ave_ssim))
        if np.ndim(img_H) == 3:
            ave_psnr_y = sum(test_results['psnr_y']) / len(test_results['psnr_y'])
            ave_ssim_y = sum(test_results['ssim_y']) / len(test_results['ssim_y'])
            logger.info('Average PSNR/SSIM( Y ) - {} - x{} - PSNR: {:.2f} dB; SSIM: {:.4f}'.format(result_name, sf, ave_psnr_y, ave_ssim_y))

if __name__ == '__main__':

    main()
