import numpy as np


def composite(a, b, aa):
    return a * aa + b * (1.0 - aa)


def zoom_in(img, corner, boundary_params:dict):
    """
    Compute the zoom in region.
    :param img:      np.array
    :param corner:   top-left corner
    :param boundary_params: parameters for the boundary {'hpatch', 'wpatch', 'padding', 'color'}
    :return: return the colored original np.array and zoom-in image
    """
    key_list = ['hpatch', 'wpatch', 'padding', 'color']
    for k in key_list:
        assert k in boundary_params, '<{}> should be in the boundary_params'.format(k)

    hpatch  = boundary_params['hpatch']
    wpatch  = boundary_params['wpatch']
    padding = boundary_params['padding']
    color   = boundary_params['color']

    ret = img.copy()
    h, w = hpatch, wpatch
    padding_region = np.ones((h, w, 1))
    hslice, wslice = slice(padding, h-padding), slice(padding, w-padding)
    padding_region[hslice, wslice, :] = 0.0
    color_patch = np.ones((h, w, 3)) * color

    hc, wc = corner
    patch_h, patch_w = slice(hc, hc + hpatch), slice(wc, wc+wpatch)
    patch_ret = composite(color_patch, ret[patch_h, patch_w], padding_region)

    ret[patch_h, patch_w] = patch_ret

    return ret, patch_ret

