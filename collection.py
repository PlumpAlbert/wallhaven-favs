from plumphaven import get_images_from_collection, download_image
from os import path, makedirs
from mimetypes import guess_extension
from progress.bar import ChargingBar

class WallCollection(object):
    def __init__(self, username, id, label):
        self.id = id
        self.label = label
        self.pics = get_images_from_collection(username, id)

    def update(self, root_dir='~/Pictures'):
        collection_dir = path.join(path.expanduser(root_dir), self.label)
        progress = ChargingBar(self.label.ljust(20), max=len(self.pics))
        if not path.exists(collection_dir):
            makedirs(collection_dir)
        for p in self.pics:
            download_image(
                p['path'],
                path.join(collection_dir, p['id'] + guess_extension(p['file_type']))
            )
            progress.next()
        progress.finish()
