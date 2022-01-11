# wordle
Solves https://www.powerlanguage.co.uk/wordle/ optimally, though (presently) quite slowly.

# Example usage

```
$ ./wordle.py --hints bacon:RRRRY,grues:RGRRR
12972 words loaded from wordle_dictionary.txt
bacon (GRAY, GRAY, GRAY, GRAY, YELLOW) 725 possibilities remain
grues (GRAY, GREEN, GRAY, GRAY, GRAY) 3 possibilities remain
Possibilities: ['drink', 'prink', 'print']
0 1 0.0 [3, 1, 'drink', 'GGGGG']
Best guess: "drink", which should get the right answer in 1.67 guesses on average
```
