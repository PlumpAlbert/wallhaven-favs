from typing import Any, Optional
import logging
import time
import json
import pathlib
from requests import get
from os import path, getenv
from shutil import copyfileobj

LOG_LEVEL = getenv('LOG_LEVEL', 'INFO').upper()

log = logging.getLogger(__file__)
log.setLevel(LOG_LEVEL)

HOST = 'https://wallhaven.cc/api/v1'


def _get_api_key(api_key: Optional[str] = None) -> str:
    """Resolve the API key: explicit arg > WALLHAVEN_API_KEY env var."""
    key = api_key or getenv('WALLHAVEN_API_KEY')
    if not key:
        raise ValueError(
            "Wallhaven API key is required. "
            "Set the WALLHAVEN_API_KEY environment variable "
            "or pass it via --apikey flag."
        )
    return key


def _get_auth_header(api_key: Optional[str] = None) -> dict[str, str]:
    """Build the X-Api-Key header from the provided key or env var."""
    return {'X-Api-Key': _get_api_key(api_key)}


def get_collections(username, api_key: Optional[str] = None):
    """
    Method for retrieving user's collections

    :param username str: Username
    :param api_key Optional[str]: API key override
    """
    response = get('{}/collections/{}'.format(HOST, username), headers=_get_auth_header(api_key))
    if response.status_code == 429:
        log.info("? Too many requests. Sleeping for 3 seconds...")
        time.sleep(3)
        return get_collections(username)
    return response.json()['data']


def get_images_from_collection(
    username: str,
    collection_id: int,
    cache_dir: str = path.expanduser('~/.cache/wallhaven/collections'),
    api_key: Optional[str] = None
):
    """
    Method for retrieving images from a collection

    :param username str: Username
    :param collection_id int: Collection identifier
    :param cache_dir str: Cache directory for collections
    :param api_key Optional[str]: API key override
    """
    def get_image_collection(page: int) -> tuple[list[dict[str, Any]] | None,
                                                 int | None]:
        log.debug("$ Fetching %d page for %d collection of %s" %
                  (page, collection_id, username))
        response = get(
            '{}/collections/{}/{}'.format(HOST, username, collection_id),
            params={'page': page},
            headers=_get_auth_header(api_key),
        )
        if response.status_code == 429:
            log.info("? Too many requests. Sleeping for 3 seconds...")
            time.sleep(3)
            return get_image_collection(page)
        elif response.status_code != 200:
            log.error("! Response is not OK. Response = %s" % response)
            return (None, None)
        json_data = response.json()
        log.debug('response = %s' % json_data)
        return (json_data['data'], None if page == json_data['meta']['last_page'] else page + 1)

    latest_pics = []
    page = 1
    cache = None
    # Open cached images
    if path.exists(cache_dir):
        log.debug('$ Found cache directory')
        cache_file_path = path.join(cache_dir, '%s.json' % collection_id)
        if path.exists(cache_file_path):
            with open(cache_file_path, 'r') as cache_file:
                log.debug('$ Found cache directory')
                cache = json.load(cache_file)
    else:
        pathlib.Path(cache_dir).mkdir(parents=True, exist_ok=True)
    while page is not None:
        pics, page = get_image_collection(page)
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
                log.debug("$ Concatenate with cache")
                result = latest_pics + pics[:index] + cache
                cache_file_path = path.join(
                    cache_dir, '%s.json' % collection_id)
                with open(cache_file_path, 'w') as cache_file:
                    json.dump(result, cache_file)
                return result
        latest_pics += pics

    with open(path.join(cache_dir, '%s.json' % collection_id), 'w') as cache_file:
        json.dump(latest_pics, cache_file)
    return latest_pics


def download_image(url, file_path):
    """
    Method for downloading image to the specified path

    :param url str: URL of the image to download
    :param file_path str: Path to store image
    """
    dir_path = path.dirname(file_path)
    if path.exists(file_path):
        return
    if not path.exists(dir_path):
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
    response = get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            copyfileobj(response.raw, f)
    else:
        log.error('! Response is not OK. Response= % s' % response)
