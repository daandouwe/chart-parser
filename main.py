#!/usr/bin/env python
import argparse
import pickle
from collections import defaultdict

import numpy as np
from nltk import tokenize

from parser import Parser
from util import unbinarize


def main(args):
    parser = Parser(args.grammar)

    if args.parse_file:
        with open(args.parse_file) as fin:
            lines = fin.readlines()
            sentences = [tokenize.word_tokenize(line.strip()) for line in lines]
        with open(args.out_file, 'w') as fout:
            for sentence in sentences:
                trees = parser(sentence)
                if not trees:
                    print('', file=fout)
                else:
                    tree, _ = trees[0]
                    tree = tree.pformat(margin=np.inf)
                    print(tree, file=fout)
            exit('Finished.')

    elif args.sent:
        sentence = tokenize.word_tokenize(args.sent)
    else:
        sentence = 'The horse walked past the barn fell .'.split()

    print('Parsing sentence..')
    trees = parser(sentence)

    for tree, score in reversed(trees[:10]):
        print('prob: ', score)
        tree.pretty_print()
        unbinarize(tree).pretty_print()
        print(79*'-')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--grammar', type=str, default='train.grammar')
    argparser.add_argument('--sent', type=str, default='')
    argparser.add_argument('--parse-file', type=str, default='')
    argparser.add_argument('--out-file', type=str, default='pred.trees')
    args = argparser.parse_args()

    main(args)
