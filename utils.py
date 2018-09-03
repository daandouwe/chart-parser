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


def cleanup_tree(tree):
    clean_label = tree.label().split('|')[0]  # If top node is like VP|<S-PP-,-SBAR>
    tree.set_label(clean_label)
    tree.un_chomsky_normal_form()  # un-binarize.
    # Add TOP label (we don't handle unaries in our CKY so TOP -> X is never recognized.)
    tree = Tree(TOP, [tree])
    return tree


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