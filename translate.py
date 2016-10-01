# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import argparse
import requests
import sys

with open('.api_key') as file:
    API_KEY = file.read().strip()

def translate(queries, target, source=None, chunk_size=0, max_retries=3):
    url = 'https://www.googleapis.com/language/translate/v2'

    queries = list(queries)

    if not chunk_size:
        chunk_size = len(queries)

    for i in range(0, len(queries), chunk_size):
        params = {
            'key': API_KEY,
            'q': queries[i:i+chunk_size],
            'target': target,
        }
        if source:
            params['source'] = source

        for retry in range(max_retries):
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                body = response.json()
                translations = body['data']['translations']
                break
            except Exception as e:
                print(e)
                print('retry {}'.format(retry + 1))
        else:
            raise Exception()

        for translation in translations:
            yield translation['translatedText']

def get_args():
    parser = argparse.ArgumentParser(description='Translate strings')
    parser.add_argument('queries', nargs='*',
        help='strings to be translated')
    parser.add_argument('-t', '--target', required=True,
        help='target language')
    parser.add_argument('-s', '--source',
        help='source language (if none specified will be detected)')
    parser.add_argument('-v', '--verbose', action='count', default=0,
        help='increase verbosity (specify multiple times for more)')

    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()

    queries = args.queries if args.queries else sys.stdin
    queries = filter(None, map(lambda s: s.strip(), queries))

    for t in translate(queries, source=args.source, target=args.target, chunk_size=10):
        print(t)
