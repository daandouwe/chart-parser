#!/usr/bin/env python
import sys
from collections import defaultdict


def get_grammar(path):
    lhs_count = defaultdict(int)
    # First get total count.
    with open(path) as fin:
        lines = fin.readlines()
    for line in lines:
        count, lhs, *rhs = line.split()
        lhs_count[lhs] += int(count)
    rules = []
    for line in lines:
        count, lhs, *rhs = line.split()
        count = int(count)
        if len(rhs) == 1:
            rules.append('[{}] ||| [{}] ||| {}'.format(lhs, rhs[0], count/lhs_count[lhs]))
        elif len(rhs) == 2:
            rules.append('[{}] ||| [{}] [{}] ||| {}'.format(lhs, rhs[0], rhs[1], count/lhs_count[lhs]))
        else:
            raise ValueError(f'strange right hand side of rule: {rhs}')
    return rules

def get_lexical(path):
    tag_count = defaultdict(int)
    with open(path) as fin:
        lines = fin.readlines()
    rules = []
    for line in lines:
        word, *rest = line.split()
        tags, counts = zip(*[(rest[i], int(rest[i+1])) for i in range(0, len(rest), 2)])
        for tag, count in zip(tags, counts):
            tag_count[tag] += count
        rules.append((word, tags, counts))
    print_rules = []
    for word, tags, counts in rules:
        for tag, count in zip(tags, counts):
            print_rules.append('[{}] ||| {} ||| {}'.format(tag, word, count/tag_count[tag]))
    return print_rules


def main(gram_path, lex_path):
    gram_rules = get_grammar(gram_path)
    lex_rules = get_lexical(lex_path)
    print('\n'.join(sorted(gram_rules)))
    print('\n'.join(sorted(lex_rules)))


if __name__ == '__main__':
    if len(sys.argv) > 2:
        gram_path = sys.argv[1]
        lex_path = sys.argv[2]
        main(gram_path, lex_path)
    else:
        exit('Specify paths.')
