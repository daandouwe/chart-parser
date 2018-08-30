import os
import platform
import unicodedata
from collections import defaultdict

from nltk.tree import Tree
from PYEVALB import scorer, parser

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
    label = tree.label().split('|')[0]  # If top node is like VP|<S-PP-,-SBAR>
    tree.set_label(label)
    tree.un_chomsky_normal_form()
    return Tree(TOP, [tree])  # Add TOP label.


def evalb(pred_path, gold_path, result_path):
    scorer.Scorer().evalb(gold_path, pred_path, result_path)


def show(path):
    """Opens a textfile with a text editor."""
    if platform.system() == 'Darwin':
        os.system(f"open -a TextEdit {path}")
    if platform.system() == 'Linux':
        os.system(f"open {path}")
    if platform.system() == 'Windows':
        os.system(f"start {path}")
