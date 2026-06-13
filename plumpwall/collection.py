from .wallhaven_api import get_images_from_collection, download_image
import logging
from os import path, makedirs, getenv
from mimetypes import guess_extension
from progress.bar import ChargingBar
from typing import Optional

LOG_LEVEL = getenv('LOG_LEVEL', 'INFO').upper()

log = logging.getLogger(__file__)
log.setLevel(LOG_LEVEL)


class WallCollection(object):
    def __init__(self, username, id, label, api_key: Optional[str] = None):
        self.id = id
        self.label = label
        pics = get_images_from_collection(username, id, api_key=api_key)
        self.pics = pics

    def update(self, root_dir='~/Pictures'):
        if not root_dir:
            root_dir = '~/Pictures'
        collection_dir = path.join(path.expanduser(root_dir), self.label)
        progress = ChargingBar(self.label.ljust(20), max=len(self.pics))
        if not path.exists(collection_dir):
            makedirs(collection_dir)
        for p in self.pics:
            download_image(p['path'],
                           path.join(
                               collection_dir, p['id'] +
                               guess_extension(p['file_type'])))
            progress.next()
        progress.finish()
