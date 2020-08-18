from plumphaven import get_collections, get_images_from_collection, download_image
from argparse import ArgumentParser
from os import path
from collection import WallCollection

parser = ArgumentParser(description='Synchronize your wallpapers from https://wallhaven.cc')
parser.add_argument('-u', '--user', metavar='USERNAME', type=str, help='Username')
parser.add_argument('-d', '--directory', metavar='DIRECTORY', type=str, help='Root directory for saving wallpapers')

args = parser.parse_args()

args = dict(args._get_kwargs())

if not args['user']:
    raise ValueError("You must provide username")

collections = [WallCollection(args['user'], c['id'], c['label']) for c in get_collections(args['user'])]
for c in collections:
    c.update(args['directory'])
