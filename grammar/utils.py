#!/usr/bin/env python
import unicodedata

NUM = 'NUM'
UNK = 'UNK'


def is_bracket(word):
    """E.g. -LRB-"""
    return word.startswith('-') and word.endswith('B-')


def is_number(s):
    s = s.replace(',', '')  # 10,000 -> 10000
    s = s.replace(':', '')  # 5:30 -> 530
    s = s.replace('-', '')  # 17-08 -> 1708
    s = s.replace('/', '')  # 17/08/1992 -> 17081992
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def process(word):
    if not is_bracket(word):
        word = word.lower()
    if is_number(word):
        word = NUM
    return word


def unkify(token, words_dict, frozen=False):
    """Elaborate UNKing following parsing tradition.

    Taken from https://github.com/clab/rnng/blob/master/get_oracle.py.
    """
    if len(token.rstrip()) == 0:
        final = 'UNK'
    else:
        numCaps = 0
        hasDigit = False
        hasDash = False
        hasLower = False
        for char in token.rstrip():
            if char.isdigit():
                hasDigit = True
            elif char == '-':
                hasDash = True
            elif char.isalpha():
                if char.islower():
                    hasLower = True
                elif char.isupper():
                    numCaps += 1
        result = 'UNK'
        lower = token.rstrip().lower()
        ch0 = token.rstrip()[0]
        if ch0.isupper():
            if numCaps == 1:
                result = result + '-INITC'
                if lower in words_dict:
                    result = result + '-KNOWNLC'
            else:
                result = result + '-CAPS'
        elif not(ch0.isalpha()) and numCaps > 0:
            result = result + '-CAPS'
        elif hasLower:
            result = result + '-LC'
        if hasDigit:
            result = result + '-NUM'
        if hasDash:
            result = result + '-DASH'
        if lower[-1] == 's' and len(lower) >= 3:
            ch2 = lower[-2]
            if not(ch2 == 's') and not(ch2 == 'i') and not(ch2 == 'u'):
                result = result + '-s'
        elif len(lower) >= 5 and not(hasDash) and not(hasDigit and numCaps > 0):
            if lower[-2:] == 'ed':
                result = result + '-ed'
            elif lower[-3:] == 'ing':
                result = result + '-ing'
            elif lower[-3:] == 'ion':
                result = result + '-ion'
            elif lower[-2:] == 'er':
                result = result + '-er'
            elif lower[-3:] == 'est':
                result = result + '-est'
            elif lower[-2:] == 'ly':
                result = result + '-ly'
            elif lower[-3:] == 'ity':
                result = result + '-ity'
            elif lower[-1] == 'y':
                result = result + '-y'
            elif lower[-2:] == 'al':
                result = result + '-al'
        final = result

    if frozen and final not in word_vocab:
        # increasingly strip UNK refinements until it is part of the vocabulary
        while final not in word_vocab:
            final = '-'.join(final.split('-')[:-1])

    return final
