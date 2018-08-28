import unicodedata
from collections import defaultdict

from nltk.tree import Tree

from symbol import Span
from rule import Rule

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


def make_nltk_tree(derivation):
    """
    Return a NLTK Tree object based on the derivation
    (list or tuple of Rules)
    """
    d = defaultdict(None, ((r.lhs, r.rhs) for r in derivation))

    def make_tree(lhs):
        return Tree(str(lhs._symbol)[1:-1], (str(child._symbol)[1:-1]
                                             if child not in d else make_tree(child) for child in d[lhs]))

    return make_tree(derivation[0].lhs)


def unbinarize(tree):
    assert isinstance(tree, Tree)

    def clean_children(tree):
        children = []
        for child in tree:
            if child.label().startswith('@'):
                # Move grandchildren up one generation.
                children.extend([grandchild for grandchild in child])
            else:
                children.append(child)
        return Tree(tree.label(), children)

    if len(tree) == 1:
        return tree
    elif len(tree) == 2:
        node = tree.label()
        left_child, right_child = tree
        if left_child.label().startswith('@'):
            left_child.append(right_child)
            tree = left_child
            tree.set_label(node)
        if right_child.label().startswith('@'):
            tree.pop()
            tree.extend(right_child)
        # Above action can cause an @node to become a child.
        # We need to repeatedly remove these intermediate nodes.
        all_clean = False
        while not all_clean:
            tree = clean_children(tree)
            all_clean = all((not child.label().startswith('@') for child in tree))
        # Now unbinarize all the _clean_ child nodes.
        return Tree(tree.label(), [unbinarize(child) for child in tree])
    return tree