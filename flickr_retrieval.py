import contextlib
import logging
import os
import shutil
from pathlib import Path

import flickrapi
import pandas as pd
import requests
from tqdm import tqdm

flickr_retrieval_logger = logging.getLogger("flickr_retrieval")
flickr_retrieval_logger.setLevel(logging.INFO)


def get_image_url_etree(image_id):
    sizes = flickr.photos.getSizes(photo_id=image_id)
    largest_available_size = (
        pd.DataFrame([dict(e.items()) for e in list(sizes.find("sizes"))])
        .sort_values(by=["width", "height"], ascending=True)
        .iloc[0]
    )
    return largest_available_size.to_dict()


def retrieve_image_meta_data(album_id, n_images_per_album=30, min_resolution=800):
    image_records = []
    try:
        images_raw = list(flickr.walk_set(album_id))
    except:
        flickr_retrieval_logger.error(f"Unable to walk images for album: {album_id}")
        return pd.DataFrame()  # cat empty df all the same? bit yikes

    for image in tqdm(
        images_raw, desc=f"Retrieving image meta data for album: {album_id}"
    ):
        image = dict(image.items())  # silly e-tree format
        try:
            largest_size = get_image_url_etree(image["id"])
            image["image_meta"] = largest_size
            image_records.append(image)
        except:
            flickr_retrieval_logger.error(
                f"Unable to retrieve image size for: {image['id']}"
            )

    images = (
        pd.DataFrame(image_records)
        .assign(album_id=album_id)
        .assign(download_url=lambda x: x.image_meta.apply(lambda y: y["source"]))
        # filter out small images
        .assign(width=lambda x: x.image_meta.apply(lambda y: int(y["width"])))
        .assign(height=lambda x: x.image_meta.apply(lambda y: int(y["height"])))
        .query("height >= @min_resolution & width >= @min_resolution")
        .pipe(
            lambda x: x.sample(n=n_images_per_album, random_state=42)
            if x.shape[0] > n_images_per_album
            else x
        )
    )
    if len(images) == 0:
        flickr_retrieval_logger.warning(
            f"No images meet the minimum resolution of {min_resolution}; {len(image_records)} initial records found"
        )
    return images


def download_flickr_image(url, save_path):
    response = requests.get(url)
    with open(save_path, "wb") as file:
        file.write(response.content)
        file.close()


def download_image_record(record, download_dir):
    # mkdir album save dir if doesn't exist
    if (download_dir / record.album_id).exists() == False:
        (download_dir / record.album_id).mkdir(parents=True, exist_ok=True)

    save_path = f"{(download_dir / record.album_id / record.id).as_posix()}{Path(record.download_url).suffix}"
    if Path(save_path).exists() == True:
        flickr_retrieval_logger.info(f"Previously saved: {save_path}; skipping")
    else:
        try:
            download_flickr_image(record.download_url, save_path)
        except Exception:
            flickr_retrieval_logger.error(
                f"Unable to download image at: {record.download_url}"
            )


if __name__ == "__main__":
    MIN_RESOLUTION = 1000
    N_IMAGES_PER_ALBUM = 30
    DOWNLOAD_DIR = Path("./output/bdhl_flickr_downloads/")

    # 1. authenticate
    FLICKR_API_KEY = os.getenv("FLICKR_API_KEY")
    FLICKR_API_SECRET = os.environ.get("FLICKR_API_SECRET")

    # json format also available
    flickr = flickrapi.FlickrAPI(FLICKR_API_KEY, FLICKR_API_SECRET, format="etree")
    with contextlib.suppress(Exception):
        flickr.authenticate_console()  # 401 error anyway? but still works?
    flickr_retrieval_logger.info("Successfully authenticated to flickr API")

    # 2. manually curate some biodiversity albums
    CURATED_BDHL_ALBUMS = [
        "https://www.flickr.com/photos/biodivlibrary/albums/72157719441825715",
        "https://www.flickr.com/photos/biodivlibrary/albums/72157719388569819",
        "https://www.flickr.com/photos/biodivlibrary/albums/72157719436056985",
        "https://www.flickr.com/photos/biodivlibrary/albums/72157719344590884",
        "https://www.flickr.com/photos/biodivlibrary/albums/72157719355459807",
        "https://www.flickr.com/photos/biodivlibrary/albums/72157719347463287",
        "https://www.flickr.com/photos/biodivlibrary/albums/72157719167039103",
        "https://www.flickr.com/photos/biodivlibrary/albums/72157719094689375",
        "https://www.flickr.com/photos/biodivlibrary/albums/72157719092377820",
        "https://www.flickr.com/photos/biodivlibrary/albums/72157719004471241",
    ]
    curated_bdhl_albums = [Path(e).name for e in CURATED_BDHL_ALBUMS]

    # walk the albums, retrieve individual image details
    all_images = [
        retrieve_image_meta_data(album, N_IMAGES_PER_ALBUM, MIN_RESOLUTION)
        for album in curated_bdhl_albums
    ]
    all_images = pd.concat(all_images)

    # download each image
    shutil.rmtree(str(DOWNLOAD_DIR)) if DOWNLOAD_DIR.exists() else None
    DOWNLOAD_DIR.mkdir()
    for idx, image in tqdm(list(all_images.iterrows()), desc="Downloading images"):
        download_image_record(image, DOWNLOAD_DIR)
