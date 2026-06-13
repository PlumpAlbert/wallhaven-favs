from plumpwall.wallhaven_api import get_collections
from argparse import ArgumentParser
from plumpwall.collection import WallCollection
import logging
import os

LOG_LEVEL = os.getenv('LOGLEVEL', 'INFO').upper()

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(message)s")

parser = ArgumentParser(
    description='Synchronize your wallpapers from https://wallhaven.cc')
parser.add_argument('-u', '--user', metavar='USERNAME',
                    type=str, help='Username')
parser.add_argument(
    '-d', '--directory', metavar='DIRECTORY', type=str,
    help='Root directory for saving wallpapers')
parser.add_argument(
    '--apikey', metavar='API_KEY', type=str,
    help='Wallhaven API key (overrides WALLHAVEN_API_KEY env var)')

args = parser.parse_args()

args = dict(args._get_kwargs())

if not args['user']:
    raise ValueError("You must provide username")

api_key = args.get('apikey')

collections = [WallCollection(args['user'], c['id'], c['label'], api_key=api_key)
               for c in get_collections(args['user'], api_key=api_key)]

for c in collections:
    c.update(args['directory'])
