import os
import platform
import unicodedata
from collections import defaultdict

from nltk.tree import Tree
from PYEVALB import scorer, parser

TOP = 'TOP'
UNK = '<unk>'
NUM = '<num>'


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


def process_sentence(sentence, vocab):
    assert isinstance(sentence, list)
    sentence = [process(word.lower()) for word in sentence]
    sentence = [word if word in vocab else UNK for word in sentence]
    return sentence


def cleanup_tree(tree):
    label = tree.label().split('|')[0]  # If top node is like VP|<S-PP-,-SBAR>
    tree.set_label(label)
    tree.un_chomsky_normal_form()
    return Tree(TOP, [tree])


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
