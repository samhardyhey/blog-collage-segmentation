# Collage Segmentation 🎨

Semi-automated tools for extracting vintage biological illustrations from the Biodiversity Heritage Library. Companion code for ["Collagey Segmenty"](https://www.samhardyhey.com/collagey-segmenty).

## Features
- 🖼️ Automated Flickr image retrieval
- ✂️ Filter-based image segmentation
- 🎯 Background removal
- 🔄 Batch processing

## Setup
```bash
# Install dependencies
./create_env.sh
```

## Usage
```bash
# Configure Flickr API credentials
export FLICKR_API_KEY="your-key"
export FLICKR_API_SECRET="your-secret"

# Download images
python flickr_retrieval.py

# Process images
python filter_segmentation.py
```

## Structure
- 📓 `flickr_retrieval.py` # Image collection
- ✂️ `filter_segmentation.py` # Auto-cropping
- ⚙️ `create_env.sh` # Environment setup

*Note: Requires Flickr API access. Apply [here](https://www.flickr.com/services/apps/create/apply/).*