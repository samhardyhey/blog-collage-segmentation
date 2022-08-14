## Collage segmentation
Notebooks and scripts for the semi-automated segmentation of collage materials. See the accompanying blog post here.

## Install
- Conda env creation, python dependencies, via `create_env.sh`

## Usage
- Apply for flickr API usage [here](https://www.flickr.com/services/apps/create/apply/), ensure that env variables `FLICKR_API_KEY` and `FLICKR_API_SECRET` are configured appropriately
- Retrieve a sample of images from a collection of reference flickr album URLS via `python flickr_retrieval.py`
- Auto-crop the downloaded images with filter-based thresholding via `python filter_segmentation.py`