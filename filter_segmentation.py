import logging
import shutil
from pathlib import Path

import cv2
import numpy as np
from skimage.filters import threshold_mean

filter_segmentation_logger = logging.getLogger("flickr_retrieval")
filter_segmentation_logger.setLevel(logging.INFO)


def get_threshold_mask(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = gray > threshold_mean(gray)
    gray[mask] = 0
    return mask


def apply_mask(image, mask):
    # invert
    mask = mask.astype(np.uint8)
    mask = (~mask.astype(bool)).astype(np.uint8)

    # smooth morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # apply
    masked = cv2.bitwise_and(image, image, mask=mask)

    return masked


def remove_background(masked_image):
    # save with transparent background
    tmp = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
    _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
    b, g, r = cv2.split(masked_image)
    rgba = [b, g, r, alpha]
    masked_tr = cv2.merge(rgba, 4)
    return masked_tr


if __name__ == "__main__":
    # load images, creat output dir
    all_images = list(
        Path("./output/bdhl_flickr_downloads/72157719533382815/").rglob("*.jpg")
    )
    save_dir = Path("./output/filter_segmentation")
    shutil.rmtree(str(save_dir)) if save_dir.exists() else None
    save_dir.mkdir()

    # apply threshold filtering
    for image_file in all_images:
        image = cv2.imread(str(image_file))
        mask = get_threshold_mask(image)
        masked = apply_mask(image, mask)
        bg_removed = remove_background(masked)
        cv2.imwrite(str(save_dir / f"{image_file.name}_mask.png"), bg_removed)
