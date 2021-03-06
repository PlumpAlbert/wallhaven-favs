from requests import get
from os import mkdir, path
from shutil import copyfileobj
from time import sleep


host = 'https://wallhaven.cc/api/v1'


def get_collections(username):
    response = get('{}/collections/{}'.format(host, username),
            params={'apikey': 'FoN92tRu9mlrpUWwp93y5rh9ehTU6lcV'})
    if response.status_code == 429:
        sleep(3)
        return get_collections(username)
    return response.json()['data']


def get_images_from_collection(username, collection_id):
    page = 1
    last_page = 1
    pics = []
    while page <= last_page:
        response = get(
                '{}/collections/{}/{}'.format(host,username,collection_id),
                params={'apikey': 'FoN92tRu9mlrpUWwp93y5rh9ehTU6lcV', 'page': page}
        )
        if response.status_code == 429:
            sleep(3)
            continue
        elif response.status_code != 200:
            break
        res = response.json()
        pics += res['data']
        page += 1
        last_page = res['meta']['last_page']
    pics.reverse()
    return pics


def download_image(url, file_path):
    dir_path =  path.dirname(file_path)
    if not path.exists(dir_path):
        mkdir(dir_path)
    if path.exists(file_path):
        return
    response = get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            copyfileobj(response.raw, f)
