from plumphaven import get_collections, get_images_from_collection, download_image
from argparse import ArgumentParser
from os import path
from collection import WallCollection

parser = ArgumentParser(description='Synchronize your wallpapers from https://wallhaven.cc')
parser.add_argument('-u', '--user', metavar='user', type=str, help='Username')

args = parser.parse_args()

args = dict(args._get_kwargs())

if not args['user']:
    raise ValueError("You must provide username")

collections = [WallCollection(args['user'], c['id'], c['label']) for c in get_collections(args['user'])]
# for c in collections:
    # dir_path = path.join(
            # path.expanduser("~/Pictures/"),
            # c['label']
    # )
    # images = get_images_from_collection(args['key'],args['user'],c['id'])
    # count = 1
    # for img in images:
        # print('Updating {} collection [{}/{}]'.format(
            # c['label'],
            # count,
            # len(images)
        # ), end='\r')
        # file_path = path.join(
                # dir_path,
                # img['id'] + guess_extension(img['file_type'])
        # )
        # download_image(img['path'], file_path)
        # count += 1
    # print()

for c in collections:
    c.update()
