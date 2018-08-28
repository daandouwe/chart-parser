#!/usr/bin/env python
import sys
import json
import unicodedata
from collections import Counter

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


def main(path, vocab_size):
    # Construct vocabulary.
    vocab = []
    with open(path) as fin:
        for line in fin:
            words = line.strip().split()
            for word in words:
                word = process(word)
                vocab.append(word)
    counter = Counter(vocab)
    vocab = dict(counter.most_common(vocab_size))
    with open('vocab.json', 'w') as fp:
        json.dump(vocab, fp, indent=4)
    del counter
    # Get all neccessary substitutions using vocabulary.
    subs = []
    with open(path) as fin:
        for sent_id, line in enumerate(fin, 1):
            words = line.strip().split()
            for word_id, word in enumerate(words, 1):
                processed = process(word)
                if processed not in vocab:
                    subs.append(f'{sent_id} {word_id} {UNK}')
                elif not processed == word:
                    subs.append(f'{sent_id} {word_id} {processed}')
    print('\n'.join(subs))


if __name__ == '__main__':
    if len(sys.argv) > 2:
        path = sys.argv[1]
        vocab_size = int(sys.argv[2])
        main(path, vocab_size)
    else:
        exit('Specify paths.')
