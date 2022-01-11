#! /usr/bin/env python3

import argparse
import pathlib

parser = argparse.ArgumentParser(description='Wordle solver')
parser.add_argument(
    '--dictionary',
    help='Dictionary to use',
    type=pathlib.Path,
    default='wordle_dictionary.txt',
    )

args = parser.parse_args()
WORDS = set(args.dictionary.read_text().splitlines())
print(WORDS)
