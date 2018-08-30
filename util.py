import os
import platform
import unicodedata
from collections import defaultdict

from nltk.tree import Tree
from PYEVALB import scorer, parser

from grammar.utils import NUM, UNK, is_bracket, is_number, process

TOP = 'TOP'


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
