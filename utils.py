import os
import platform
import unicodedata
from collections import defaultdict

from nltk.tree import Tree

from grammar.utils import NUM, UNK, is_bracket, is_number, process


TOP = 'TOP'

SENT = 'The bill intends to restrict the RTC to Treasury borrowings only , ' + \
       'unless the agency receives specific congressional authorization .'

GOLD = '(TOP (S (NP (DT The) (NN bill)) (VP (VBZ intends) (S (VP (TO to) (VP ' + \
       '(VB restrict) (NP (DT the) (NNP RTC)) (PP (TO to) (NP (NNP Treasury) ' + \
       '(NNS borrowings) (RB only)))))) (, ,) (SBAR (IN unless) (S (NP (DT the) ' + \
       '(NN agency)) (VP (VBZ receives) (NP (JJ specific) (JJ congressional) ' + \
       '(NN authorization)))))) (. .)))'


def process_sentence(sentence, vocab):
    assert isinstance(sentence, list)
    sentence = [process(word.lower()) for word in sentence]
    sentence = [word if word in vocab else UNK for word in sentence]
    return sentence


def show(path):
    """Opens a textfile with a text editor."""
    if platform.system() == 'Darwin':
        os.system(f"open -a TextEdit {path}")
    if platform.system() == 'Linux':
        os.system(f"open {path}")
    if platform.system() == 'Windows':
        os.system(f"start {path}")


def ceil_div(a, b):
    return ((a - 1) // b) + 1


def unkify(token, words_dict):
    """Elaborate UNKing following parsing tradition."""
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

    return final
