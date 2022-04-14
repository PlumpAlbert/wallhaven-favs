from typing import Any
import logging
import time
import json
from requests import get
from os import mkdir, path
from shutil import copyfileobj

log = logging.getLogger(__file__)

HOST = 'https://wallhaven.cc/api/v1'


def get_collections(username):
    """
    Method for retrieving user's collections

    :param username str: Username
    """
    response = get('{}/collections/{}'.format(HOST, username),
                   params={'apikey': 'FoN92tRu9mlrpUWwp93y5rh9ehTU6lcV'})
    if response.status_code == 429:
        log.info("? Too many requests. Sleeping for 3 seconds...")
        time.sleep(3)
        return get_collections(username)
    return response.json()['data']


def get_images_from_collection(
    username: str,
    collection_id: int,
    cache_dir: str = path.expanduser('~/.cache/wallhaven/collections')
):
    """
    Method for retrieving images from a collection

    :param username str: Username
    :param collection_id int: Collection identifier
    :param cache_dir str: Cache directory for collections
    """
    def get_image_collection(page: int) -> tuple[list[dict[str, Any]] | None,
                                                 int | None]:
        response = get(
            '{}/collections/{}/{}'.format(HOST, username, collection_id),
            params={'apikey': 'FoN92tRu9mlrpUWwp93y5rh9ehTU6lcV', 'page': page}
        )
        if response.status_code == 429:
            log.info("? Too many requests. Sleeping for 3 seconds...")
            time.sleep(3)
            return get_image_collection(page)
        elif response.status_code != 200:
            log.error("! Response is not OK. Response = %s" % response)
            return (None, None)
        json_data = response.json()
        return (json_data['data'], None if page == json_data['meta']['last_page'] else page + 1)

    latest_pics = []
    page = 1
    cache = None
    # Open cached images
    if path.exists(cache_dir):
        with open(path.join(cache_dir, '%s.json' % collection_id)) as cache_file:
            cache = json.load(cache_file)
    while page is not None:
        pics, page = get_image_collection(1)
        if not pics:
            log.error("! Couldn't get the latest pictures")
            return None
        # Try to find last cached image in fresh list of latest pics
        if cache is not None:
            try:
                index = next(i for i, value in enumerate(pics)
                             if value['id'] == cache[0]['id'])
            except StopIteration:
                index = None
            # If we found one -- concatenate it with fresh ones and return to user
            if index is not None:
                result = latest_pics + pics[:index] + cache
                with open(path.join(cache_dir, '%s.json' % collection_id)) as cache_file:
                    json.dump(result, cache_file)
                return result
        latest_pics += pics

    with open(path.join(cache_dir, '%s.json' % collection_id)) as cache_file:
        json.dump(latest_pics, cache_file)
    return latest_pics


def download_image(url, file_path):
    dir_path = path.dirname(file_path)
    if not path.exists(dir_path):
        mkdir(dir_path)
    if path.exists(file_path):
        return
    response = get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            copyfileobj(response.raw, f)
