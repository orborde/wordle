#! /usr/bin/env python3

import argparse
import collections
from enum import Enum
from fractions import Fraction
import pathlib
from typing import List, Tuple, Dict, Set, Optional

parser = argparse.ArgumentParser(description='Wordle solver')
parser.add_argument(
    '--dictionary',
    help='Dictionary to use',
    type=pathlib.Path,
    default='wordle_dictionary.txt',
    )

parser.add_argument(
    '--hints',
    help='Hints received so far. Example: grant:GGYRR',
    type=str,
    default='',
)

class HintPiece(Enum):
    GREEN = 'GREEN'
    YELLOW = 'YELLOW'
    GRAY = 'GRAY'

    def __repr__(self):
        return self.value

# I don't know how to manage namespaces cleanly.
GREEN = HintPiece.GREEN
YELLOW = HintPiece.YELLOW
GRAY = HintPiece.GRAY

ALL_GREEN = [GREEN, GREEN, GREEN, GREEN, GREEN]

def hint(actual, guess):
    """Returns the hint for the word guessed.

    >>> hint('abcd', 'abcd')
    (GREEN, GREEN, GREEN, GREEN)
    >>> hint('abcd', 'dcba')
    (YELLOW, YELLOW, YELLOW, YELLOW)
    >>> hint('abcde', 'edcba')
    (YELLOW, YELLOW, GREEN, YELLOW, YELLOW)
    >>> hint('xxxxx', 'bacon')
    (GRAY, GRAY, GRAY, GRAY, GRAY)
    >>> hint('xaaax', 'xxaaa')
    (GREEN, YELLOW, GREEN, GREEN, YELLOW)
    >>> hint('aabbc', 'bbxxa')
    (YELLOW, YELLOW, GRAY, GRAY, YELLOW)
    >>> hint('bbxxa', 'aabbc')
    (YELLOW, GRAY, YELLOW, YELLOW, GRAY)
    >>> hint('abaci','bacon')
    (YELLOW, YELLOW, YELLOW, GRAY, GRAY)
    >>> hint('bacon', 'abaci')
    (YELLOW, YELLOW, GRAY, YELLOW, GRAY)
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
            out.append(GREEN)
        elif floating_letter_counts[gc] > 0:
            out.append(YELLOW)
            floating_letter_counts[gc] -= 1
        else:
            out.append(GRAY)

    return tuple(out)

GuessWithExpectation = collections.namedtuple('GuessWithExpectation', ['guess', 'expected_after'])
def best_guess(possibilities: Set[str]) -> GuessWithExpectation:
    return min(
        [
            GuessWithExpectation(guess, expected_guesses_after(possibilities, guess))
            for guess in possibilities
        ],
        key=lambda g: g.expectation,
    )

def expected_guesses_after(possibilities: Set[str], guess) -> Fraction:
    remaining_guesses_distribution = collections.Counter()
    for hint_, sub_possibilities in possibilities_by_hint(possibilities, guess).items():
        assert len(sub_possibilities) > 0

        if hint_ == ALL_GREEN:
            assert len(sub_possibilities) == 1
            remaining_guesses_distribution[0] += 1
        else:
            g = best_guess(sub_possibilities)
            remaining_guesses_distribution[g.expected_after + 1] += len(sub_possibilities)

def possibilities_by_hint(possibilities, guess):
    possibilities_by_hint = collections.defaultdict(set)
    for actual in possibilities:
        possibilities_by_hint[hint(actual, guess)].add(actual)
    return possibilities_by_hint

def parse_hint_piece(hint_piece: str) -> HintPiece:
    if hint_piece == 'G':
        return GREEN
    elif hint_piece == 'Y':
        return YELLOW
    elif hint_piece == 'R':
        return GRAY
    else:
        raise ValueError('Unknown hint piece: {}'.format(hint_piece))

def parse_hint(hintstr: str):
    return tuple(map(parse_hint_piece, hintstr))

def parse_hints(all_hints: str):
    for chunk in all_hints.split(','):
        word, hintstr = chunk.split(':')
        yield word, parse_hint(hintstr)

if __name__ == '__main__':
    import doctest
    failures, _ = doctest.testmod()
    assert failures == 0

    args = parser.parse_args()
    WORDS = set(args.dictionary.read_text().splitlines())
    print(len(WORDS), 'words loaded from', args.dictionary)
