#!/usr/bin/env python
import unicodedata

NUM = '<num>'
UNK = '<unk>'


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
