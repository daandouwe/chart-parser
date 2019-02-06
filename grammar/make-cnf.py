#!/usr/bin/env python
import argparse

import numpy as np
from nltk import PCFG, Tree
from tqdm import tqdm


def main(args):
    trees = []
    if args.markov:
        horz_markov, vert_markov = args.markov.split(':')
        horz_markov, vert_markov = int(horz_markov), int(vert_markov)
    else:
        horz_markov, vert_markov = None, 0  # default values
    print(f'Transforming `{args.in_path}` into binary trees at `{args.out_path}`...')
    with open(args.in_path) as fin:
        lines = fin.readlines()
        for tree in tqdm(lines):
            tree = Tree.fromstring(tree.strip())
            tree.collapse_unary()
            tree.chomsky_normal_form(horzMarkov=horz_markov, vertMarkov=vert_markov)
            trees.append(tree.pformat(margin=np.inf))
    with open(args.out_path, 'w') as fout:
        print('\n'.join(trees), file=fout)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_path')
    parser.add_argument('out_path')
    parser.add_argument('--markov', type=str, default='')
    parser.add_argument('--collapse-unaries', action='store_true')
    args = parser.parse_args()

    main(args)
