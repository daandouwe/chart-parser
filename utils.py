import os
import platform
import unicodedata
from collections import defaultdict

from nltk.tree import Tree

from grammar.utils import NUM, UNK, is_bracket, is_number, process, unkify


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
    sentence = [word if word in vocab else unkify(word, vocab) for word in sentence]
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
