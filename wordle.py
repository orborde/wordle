#! /usr/bin/env python3

import argparse
import collections
from enum import Enum
from fractions import Fraction
import pathlib
import time
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

def brief_hint_piece(hint_piece: HintPiece) -> str:
    if hint_piece == GREEN:
        return 'G'
    elif hint_piece == YELLOW:
        return 'Y'
    elif hint_piece == GRAY:
        return 'R'
    else:
        raise ValueError('Unknown hint piece: {}'.format(hint_piece))

def brief_hint(hint: Tuple[HintPiece]) -> str:
    return ''.join(brief_hint_piece(h) for h in hint)

ALL_GREEN = (GREEN, GREEN, GREEN, GREEN, GREEN)

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

def null_log(*args):
    pass

GuessWithExpectation = collections.namedtuple('GuessWithExpectation', ['guess', 'expected_after'])
class Run:
    def __init__(self, log_func=null_log):
        self._log_func = log_func

    def best_guess(self, possibilities: List[str], stack=[]) -> GuessWithExpectation:
        values = []
        for i, guess in enumerate(possibilities):
            values.append(
                GuessWithExpectation(guess,
                self.expected_guesses_after(
                    possibilities,
                    guess,
                    stack=stack + [len(possibilities), i+1, guess])),
            )
        best = min(
            values,
            key=lambda g: g.expected_after,
        )
        self._log_func(stack, 'best guess:', best.guess, float(best.expected_after))
        return min(values, key=lambda g: g.expected_after)

    def expected_guesses_after(self, possibilities: List[str], guess, stack=[]) -> Fraction:
        remaining_guesses_distribution = collections.Counter()
        for hint_, sub_possibilities in possibilities_by_hint(possibilities, guess).items():
            sub_stack = stack + [brief_hint(hint_)]
            self._log_func(sub_stack)
            assert len(sub_possibilities) > 0

            if hint_ == ALL_GREEN:
                assert len(sub_possibilities) == 1
                remaining_guesses_distribution[0] += 1
            else:
                g = self.best_guess(sub_possibilities, stack=sub_stack)
                remaining_guesses_distribution[g.expected_after + 1] += len(sub_possibilities)

        return Fraction(
            sum(k * v for k, v in remaining_guesses_distribution.items()),
            sum(remaining_guesses_distribution.values()),
        )

def possibilities_by_hint(possibilities, guess):
    possibilities_by_hint = collections.defaultdict(list)
    for actual in possibilities:
        possibilities_by_hint[hint(actual, guess)].append(actual)
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

class IntervalLogger:
    def __init__(self, interval=1):
        self._last_logged = 0
        self._interval = interval

    def log(self, *args):
        if time.time() - self._last_logged > self._interval:
            print(*args)
            self._last_logged = time.time()

if __name__ == '__main__':
    import doctest
    failures, _ = doctest.testmod()
    assert failures == 0

    args = parser.parse_args()
    WORDS = list(args.dictionary.read_text().splitlines())
    print(len(WORDS), 'words loaded from', args.dictionary)

    possibilities = WORDS
    for word, hint_ in parse_hints(args.hints):
        pbh = possibilities_by_hint(possibilities, word)
        if hint_ not in pbh:
            print('No possibilities after hint', hint_)
            exit(1)
        possibilities = pbh[hint_]
        print(word, hint_, len(possibilities), 'possibilities remain')
        if len(possibilities) < 10:
            print('Possibilities:', sorted(possibilities))

    logger = IntervalLogger()
    run = Run(log_func=logger.log)
    print(run.best_guess(possibilities))
