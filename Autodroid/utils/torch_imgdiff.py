"""
基于pytorch的GPU加速实现的模板匹配算法

用于OpenCV计算结果出错时作为后备计算方式
"""
import torch
import torch.nn.functional as F
import numpy as np

import cv2.cv2 as cv


def init_tensor(arr):
    return torch.Tensor(arr.astype("float32")).transpose(0, 2).unsqueeze(0).cuda()


def match_template_torch(img, templ, mask=None):
    img = init_tensor(img)
    templ = init_tensor(templ)
    if mask is None:
        mask2 = torch.ones_like(templ)
        templ_mask2 = templ
    else:
        mask = init_tensor(mask)
        mask2 = mask * mask
        templ_mask2 = templ * mask2

    result = F.conv2d(img, templ_mask2)
    templ2_mask2_sum = (templ * templ_mask2).sum()
    temp_result = F.conv2d(img * img, mask2)
    temp_result = torch.sqrt(temp_result * templ2_mask2_sum)
    result = result / temp_result
    return result.squeeze(0).squeeze(0).transpose(0, 1).cpu().numpy()


def split_bgra(bgra):
    """将BGRA图像分离为BGR图像和Mask"""
    bgr = bgra[:, :, :3]
    h, w = bgr.shape[:2]
    a = bgra[:, :, 3].reshape(h, w, 1)
    mask = np.concatenate((a, a, a), axis=2)
    return bgr, mask


def get_all_match(image, needle):
    """在image中搜索needle"""
    img = image.astype("float32")
    templ = needle.astype("float32")
    if len(needle.shape) == 3 and needle.shape[2] == 4:
        bgr, mask = split_bgra(templ)
    else:
        bgr = templ
        mask = None
    match = 1 - np.nan_to_num(match_template_torch(img, bgr, mask))
    return match
