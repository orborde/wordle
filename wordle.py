#! /usr/bin/env python3

import argparse
import collections
from enum import Enum
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
print(len(WORDS), 'words loaded from', args.dictionary)

class Hint(Enum):
    GREEN = 'GREEN'
    YELLOW = 'YELLOW'
    GRAY = 'GRAY'

    def __repr__(self):
        return self.value

def hint(actual, guess):
    """Returns the hint for the word guessed.

    >>> hint('abcd', 'abcd')
    [GREEN, GREEN, GREEN, GREEN]
    >>> hint('abcd', 'dcba')
    [YELLOW, YELLOW, YELLOW, YELLOW]
    >>> hint('abcde', 'edcba')
    [YELLOW, YELLOW, GREEN, YELLOW, YELLOW]
    >>> hint('xxxxx', 'bacon')
    [GRAY, GRAY, GRAY, GRAY, GRAY]
    >>> hint('xaaax', 'xxaaa')
    [GREEN, YELLOW, GREEN, GREEN, YELLOW]
    >>> hint('aabbc', 'bbxxa')
    [YELLOW, YELLOW, GRAY, GRAY, YELLOW]
    >>> hint('bbxxa', 'aabbc')
    [YELLOW, GRAY, YELLOW, YELLOW, GRAY]
    >>> hint('abaci','bacon')
    [YELLOW, YELLOW, YELLOW, GRAY, GRAY]
    >>> hint('bacon', 'abaci')
    [YELLOW, YELLOW, GRAY, YELLOW, GRAY]
    """
    if len(actual) != len(guess):
        raise ValueError('Word lengths must match')

    floating_letter_counts = collections.Counter(actual)
    for ac, gc in zip(actual, guess):
        if ac == gc:
            floating_letter_counts[ac] -= 1

    out = []
    for ac, gc in zip(actual, guess):
        if ac == gc:
            out.append(Hint.GREEN)
        elif floating_letter_counts[gc] > 0:
            out.append(Hint.YELLOW)
            floating_letter_counts[gc] -= 1
        else:
            out.append(Hint.GRAY)

    return out
        

import doctest
doctest.testmod()